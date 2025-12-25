"""
CNKI 科研基金信息爬虫 - 直接链接版
使用 Playwright 自动化爬取指定链接的项目详情

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
        print("2. 确保页面已加载完成")
        print("\n完成后，请在此终端中按 Enter 键继续...")
        print("="*60 + "\n")
        input()
        
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
            
    def scrape_url(self, page: Page, url: str, index: int):
        """爬取指定URL的详情页"""
        print(f"\n处理第 {index} 个项目...")
        
        detail_page = None
        try:
            # 获取上下文
            context = page.context
            
            # 在新标签页打开URL
            print(f"  打开详情页: {url}")
            detail_page = context.new_page()
            detail_page.goto(url, timeout=60000)
            detail_page.wait_for_load_state('domcontentloaded')
            
            # 提取详情页数据
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
            
    def save_to_excel(self, filename=None):
        """保存数据到 Excel 文件"""
        if not self.data:
            print("没有数据可保存")
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cnki_projects_direct_{timestamp}.xlsx"
            
        df = pd.DataFrame(self.data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n数据已保存到: {filename}")
        print(f"共保存 {len(self.data)} 条记录")
        
    def run(self, headless=False):
        """运行爬虫"""
        print("启动 CNKI 科研基金信息爬虫（直接链接版）...")
        
        # 读取URL列表
        url_file = "url.txt"
        if not os.path.exists(url_file):
            print(f"错误：未找到URL文件 {url_file}")
            return
            
        with open(url_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("错误：URL文件为空")
            return
            
        print(f"共读取到 {len(urls)} 个URL")
        print("="*60)
        
        with sync_playwright() as p:
            # 启动浏览器（非无头模式，方便手动登录）
            browser = p.chromium.launch(headless=headless, slow_mo=500)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            try:
                # 访问网站（用于登录）
                print(f"正在访问: {self.base_url}")
                page.goto(self.base_url, timeout=60000)
                
                # 等待用户手动完成登录
                self.wait_for_manual_setup(page)
                
                # 开始爬取所有URL
                print(f"\n开始爬取 {len(urls)} 个项目详情...")
                
                for i, url in enumerate(urls, 1):
                    try:
                        # 爬取详情页
                        detail_data = self.scrape_url(page, url, i)
                        
                        # 添加序号和合并数据
                        row_data = {
                            '序号': i,
                            **detail_data  # 包含详情页的所有字段
                        }
                        
                        self.data.append(row_data)
                        
                        # 稍作延迟，避免请求过快
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"  处理项目 {i} 时出错: {e}")
                        continue
                        
                # 保存数据
                self.save_to_excel()
                
            except Exception as e:
                print(f"\n爬虫运行出错: {e}")
                # 即使出错也尝试保存已爬取的数据
                if self.data:
                    self.save_to_excel("cnki_projects_direct_partial.xlsx")
                    
            finally:
                # 关闭浏览器
                print("\n正在关闭浏览器...")
                browser.close()



def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        CNKI 科研基金信息爬虫（直接链接版）                ║
    ║        作者: AI Assistant                              ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # 创建爬虫实例
    scraper = CNKIScraper()
    
    # 运行爬虫
    # headless=False 表示显示浏览器窗口
    scraper.run(headless=False)
    
    print("\n爬取任务完成！")


if __name__ == "__main__":
    main()
