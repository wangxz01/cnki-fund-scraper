"""
CNKI 科研基金信息爬虫
使用 Playwright 自动化爬取网页数据并保存到 Excel

"""

import time
import re
from playwright.sync_api import sync_playwright, Page
import pandas as pd
from datetime import datetime
import os


class CNKIScraper:
    def __init__(self):
        self.data = []
        self.base_url = "https://cdap.cnki.net/cdap/tools/fund/project"
        
    def wait_for_manual_setup(self, page: Page):
        """等待用户手动完成 IP 登录和筛选设置"""
        print("\n" + "="*60)
        print("请在浏览器中完成以下操作：")
        print("1. 点击 IP 登录")
        print("2. 选择对应的筛选条件")
        print("3. 确保页面已加载完成")
        print("\n完成后，请在此终端中按 Enter 键继续...")
        print("="*60 + "\n")
        input()
        
    def extract_list_data(self, page: Page):
        """提取列表页的数据"""
        print("正在提取列表页数据...")
        
        # 等待表格加载
        page.wait_for_selector('table, .project-list, .list-item', timeout=10000)
        time.sleep(2)
        
        # 获取所有项目行
        # 注意：需要根据实际网页结构调整选择器
        rows = page.query_selector_all('tr, .project-item, .list-item')
        
        page_data = []
        for i, row in enumerate(rows):
            try:
                # 提取文本内容
                text = row.inner_text()
                if text.strip():
                    page_data.append({
                        '序号': i + 1,
                        '列表内容': text.strip()
                    })
            except Exception as e:
                print(f"提取行 {i} 时出错: {e}")
                
        print(f"从列表页提取了 {len(page_data)} 条记录")
        return page_data
        
    def extract_detail_data(self, page: Page, detail_page: Page, url: str):
        """提取详情页的数据"""
        print("  正在提取详情页数据...")
        
        try:
            # 等待详情页加载
            detail_page.wait_for_load_state('networkidle', timeout=10000)
            time.sleep(1)
            
            # 存储提取的数据，首先添加详情页网址
            data = {'详情页网址': url}
            
            # 提取项目标题
            try:
                title_elem = detail_page.query_selector('.content__title-text')
                if title_elem:
                    data['项目标题'] = title_elem.inner_text().strip()
            except:
                pass
            
            # 提取项目状态（在研/结题）
            try:
                status_elem = detail_page.query_selector('.fund-project-status')
                if status_elem:
                    data['项目状态'] = status_elem.inner_text().strip()
            except:
                pass
            
            # 提取详情表格中的所有字段
            # 结构: <li><span class="content__table-label">字段名</span><span class="content__table-value">值</span></li>
            try:
                table_items = detail_page.query_selector_all('ul.content__table > li')
                for item in table_items:
                    try:
                        label_elem = item.query_selector('.content__table-label')
                        value_elem = item.query_selector('.content__table-value')
                        
                        if label_elem and value_elem:
                            label = label_elem.inner_text().strip()
                            value = value_elem.inner_text().strip()
                            
                            # 保存到数据字典
                            if label and value:
                                data[label] = value
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"  提取表格数据时出错: {e}")
                
            return data
            
        except Exception as e:
            print(f"  提取详情页时出错: {e}")
            return {'错误': str(e), '详情页网址': url}
            
    def click_and_scrape_detail(self, page: Page, link_element, index: int):
        """点击链接，在新标签页中爬取详情，然后关闭"""
        detail_page = None
        url = '未知'
        try:
            print(f"\n处理第 {index} 个项目...")
            
            # 获取上下文
            context = page.context
            
            # 点击链接（会在新标签页打开）
            with context.expect_page() as new_page_info:
                link_element.click()
                
            # 获取新打开的标签页
            detail_page = new_page_info.value
            detail_page.wait_for_load_state('domcontentloaded')
            
            # 直接从浏览器地址栏获取URL（最可靠的方法）
            url = detail_page.url
            print(f"  详情页网址: {url}")
            
            # 提取详情页数据（传入URL）
            detail_data = self.extract_detail_data(page, detail_page, url)
            
            # 关闭详情页
            detail_page.close()
            
            print(f"  完成第 {index} 个项目")
            return detail_data
            
        except Exception as e:
            print(f"  处理第 {index} 个项目时出错: {e}")
            # 确保关闭可能打开的页面
            if detail_page:
                try:
                    detail_page.close()
                except:
                    pass
            return {'错误': str(e), '详情页网址': url}
            
    def extract_row_info(self, link_element):
        """从列表页的行中提取信息（如立项时间）"""
        row_info = {}
        
        try:
            # 尝试找到包含链接的行元素
            # 可能的父元素：tr, div.row, div.item, div.el-table__row
            row = link_element.evaluate('''element => {
                // 向上查找可能的行元素
                let current = element;
                while (current && current.parentElement) {
                    current = current.parentElement;
                    const tagName = current.tagName.toLowerCase();
                    const className = current.className || '';
                    
                    // 检查是否是行元素
                    if (tagName === 'tr' || 
                        className.includes('row') || 
                        className.includes('item') || 
                        className.includes('el-table__row')) {
                        return current;
                    }
                }
                return null;
            }''')
            
            if row:
                # 从行元素中提取立项时间
                # 尝试多种可能的选择器和模式
                row_handle = link_element.evaluate_handle('element => element.closest("tr, [class*=row], [class*=item]")')
                if row_handle:
                    row_elem = row_handle.as_element()
                    row_text = row_elem.inner_text() if row_elem else ''
                    
                    # 尝试匹配日期格式 (YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, YYYY-MM, YYYY)
                    date_patterns = [
                        r'\d{4}-\d{2}-\d{2}',  # 2023-01-01
                        r'\d{4}/\d{2}/\d{2}',  # 2023/01/01
                        r'\d{4}\.\d{2}\.\d{2}',  # 2023.01.01
                        r'\d{4}-\d{2}',  # 2023-01
                        r'\d{4}年\d{1,2}月\d{1,2}日',  # 2023年1月1日
                        r'\d{4}年\d{1,2}月',  # 2023年1月
                        r'\d{4}年',  # 2023年
                        r'\d{4}',  # 2023
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, row_text)
                        if match:
                            row_info['列表页_立项时间'] = match.group()
                            break
                            
        except Exception as e:
            pass
            
        return row_info
    
    def scrape_page(self, page: Page, page_num: int):
        """爬取单个列表页的所有数据"""
        print(f"\n{'='*60}")
        print(f"正在爬取第 {page_num} 页")
        print(f"{'='*60}")
        
        # 等待页面加载
        time.sleep(3)
        
        # 查找所有可点击的标题链接
        # 根据实际网页结构调整选择器
        title_links = page.query_selector_all('a[href*="project"], .project-title a, td a, .title-link')
        
        if not title_links:
            print("未找到标题链接，尝试其他选择器...")
            # 备选选择器
            title_links = page.query_selector_all('a[target="_blank"]')
            
        print(f"找到 {len(title_links)} 个项目")
        
        page_data = []
        for i, link in enumerate(title_links, 1):
            try:
                # 获取标题文本
                title = link.inner_text().strip()
                
                # 从列表页提取该行的信息（如立项时间）
                row_info = self.extract_row_info(link)
                
                # 点击并爬取详情
                detail_data = self.click_and_scrape_detail(page, link, i)
                
                # 合并数据：列表页信息 + 详情页信息
                row_data = {
                    '页码': page_num,
                    '序号': i,
                    '列表页_标题': title,
                    **row_info,  # 包含列表页_立项时间（如果找到）
                    **detail_data  # 包含详情页的所有字段
                }
                
                page_data.append(row_data)
                self.data.append(row_data)
                
                # 稍作延迟，避免请求过快
                time.sleep(1)
                
            except Exception as e:
                print(f"  处理项目 {i} 时出错: {e}")
                continue
                
        return page_data
        
    def get_current_page_number(self, page: Page) -> int:
        """获取当前页码"""
        try:
            # 查找当前激活的页码按钮
            active_page = page.query_selector('.el-pager .number.is-active')
            if active_page:
                return int(active_page.inner_text().strip())
            return 1
        except:
            return 1
    
    def click_next_page(self, page: Page) -> bool:
        """点击下一页，如果没有下一页则返回 False"""
        try:
            # 获取当前页码
            current_page = self.get_current_page_number(page)
            next_page_num = current_page + 1
            
            print(f"\n当前页码: {current_page}，尝试跳转到第 {next_page_num} 页...")
            
            # 方法1: 查找"btn-next"（右箭头）按钮
            next_button = page.query_selector('.btn-next')
            
            if next_button:
                # 检查是否禁用
                is_disabled = next_button.is_disabled()
                disabled_attr = next_button.get_attribute('disabled')
                
                if is_disabled or disabled_attr == 'true' or disabled_attr == '':
                    print("已到最后一页（下一页按钮已禁用）")
                    return False
                
                # 点击下一页按钮
                next_button.click()
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(2)
                print("翻页成功")
                return True
            
            # 方法2: 直接点击数字按钮
            next_page_button = page.query_selector(f'.el-pager .number:has-text("{next_page_num}")')
            if next_page_button:
                next_page_button.click()
                page.wait_for_load_state('networkidle', timeout=10000)
                time.sleep(2)
                print("翻页成功")
                return True
            
            print("未找到下一页按钮")
            return False
            
        except Exception as e:
            print(f"点击下一页时出错: {e}")
            return False
            
    def save_to_excel(self, filename=None):
        """保存数据到 Excel 文件"""
        if not self.data:
            print("没有数据可保存")
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cnki_projects_{timestamp}.xlsx"
            
        df = pd.DataFrame(self.data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n数据已保存到: {filename}")
        print(f"共保存 {len(self.data)} 条记录")
        
    def run(self, max_pages=None, headless=False):
        """运行爬虫"""
        print("启动 CNKI 科研基金信息爬虫...")
        
        with sync_playwright() as p:
            # 启动浏览器（非无头模式，方便手动登录）
            browser = p.chromium.launch(headless=headless, slow_mo=500)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            try:
                # 访问网站
                print(f"正在访问: {self.base_url}")
                page.goto(self.base_url, timeout=60000)
                
                # 等待用户手动完成登录和筛选
                self.wait_for_manual_setup(page)
                
                # 开始爬取
                page_num = 1
                while True:
                    # 爬取当前页
                    self.scrape_page(page, page_num)
                    
                    # 检查是否达到最大页数
                    if max_pages and page_num >= max_pages:
                        print(f"\n已达到最大页数限制: {max_pages}")
                        break
                        
                    # 尝试点击下一页
                    if not self.click_next_page(page):
                        print("\n所有页面爬取完成")
                        break
                        
                    page_num += 1
                    
                # 保存数据
                self.save_to_excel()
                
            except Exception as e:
                print(f"\n爬虫运行出错: {e}")
                # 即使出错也尝试保存已爬取的数据
                if self.data:
                    self.save_to_excel("cnki_projects_partial.xlsx")
                    
            finally:
                # 关闭浏览器
                print("\n正在关闭浏览器...")
                browser.close()


def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        CNKI 科研基金信息爬虫                            ║
    ║        作者: AI Assistant                              ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # 创建爬虫实例
    scraper = CNKIScraper()
    
    # 运行爬虫
    # max_pages=None 表示爬取所有页面
    # max_pages=5 表示只爬取前5页
    # headless=False 表示显示浏览器窗口
    scraper.run(max_pages=None, headless=False)
    
    print("\n爬取任务完成！")


if __name__ == "__main__":
    main()

