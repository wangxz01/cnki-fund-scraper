# CNKI 科研基金信息爬虫

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Playwright](https://img.shields.io/badge/Playwright-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

自动化爬取 CNKI 科研基金数据库的项目信息并保存到 Excel 文件。

[中文文档](README_CN.md) | [English](README.md)

## 功能特点

✅ 自动化浏览器操作  
✅ 支持手动登录和筛选设置  
✅ 自动翻页爬取所有数据  
✅ 点击标题获取详情页信息  
✅ 数据自动保存到 Excel  
✅ 异常处理和断点续传  

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器驱动

```bash
python -m playwright install chromium
```

## 使用方法

### 基本使用

```bash
python scraper.py
```

### 运行流程

1. **启动脚本**：运行 `python scraper.py`
2. **浏览器打开**：脚本会自动打开 Chrome 浏览器并访问 CNKI 网站
3. **手动设置**：
   - 在浏览器中点击"IP 登录"
   - 选择需要的筛选条件
   - 确保页面加载完成
4. **开始爬取**：在终端按 `Enter` 键，脚本开始自动爬取
5. **自动化流程**：
   - 读取当前页面的所有项目
   - 依次点击每个项目标题
   - 在新标签页提取详细信息
   - 关闭详情页，返回列表页
   - 点击"下一页"继续
6. **保存数据**：爬取完成后，数据自动保存为 Excel 文件

## 输出文件

生成的 Excel 文件包含以下字段：

| 字段 | 说明 |
|------|------|
| 页码 | 数据所在的页码 |
| 序号 | 项目在当前页的序号 |
| 列表页_标题 | 列表页显示的项目标题 |
| **列表页_立项时间** | **从列表页提取的立项时间** |
| **详情页网址** | **项目详情页的完整URL（重要）** |
| 项目标题 | 详情页的完整项目标题 |
| 项目状态 | 项目状态（在研/结题） |
| 开始时间 | 详情页的项目开始时间 |
| 国家/地区 | 项目所属国家或地区 |
| 资助机构 | 资助机构名称 |
| 资助金额 | 资助金额 |
| 项目类型 | 项目类型 |
| 承担机构 | 承担项目的机构 |
| 项目成员 | 项目成员信息 |
| 项目编号 | 项目编号 |
| 项目来源 | 项目来源链接 |

## 高级配置

### 限制爬取页数

修改 `scraper.py` 中的 `main()` 函数：

```python
# 只爬取前 5 页
scraper.run(max_pages=5, headless=False)
```

### 无头模式运行

```python
# 不显示浏览器窗口
scraper.run(max_pages=None, headless=True)
```

### 自定义选择器

如果网页结构发生变化，可以在 `scraper.py` 中修改选择器：

```python
# 在 scrape_page() 方法中
title_links = page.query_selector_all('你的选择器')

# 在 click_next_page() 方法中
next_button = page.query_selector('你的下一页按钮选择器')
```

## 故障排除

### 问题 1：找不到标题链接

**原因**：网页结构与预设选择器不匹配

**解决方案**：
1. 在浏览器中按 F12 打开开发者工具
2. 检查项目标题的 HTML 结构
3. 修改 `scraper.py` 中的 `title_links` 选择器

### 问题 2：无法点击下一页

**原因**：下一页按钮选择器错误

**解决方案**：
1. 检查"下一页"按钮的 HTML 结构
2. 修改 `click_next_page()` 方法中的选择器

### 问题 3：数据提取不完整

**原因**：详情页字段选择器不准确

**解决方案**：
1. 打开详情页，检查数据字段的 HTML 结构
2. 修改 `extract_detail_data()` 方法中的提取逻辑

### 问题 4：爬取中断

**原因**：网络问题或页面加载超时

**解决方案**：
- 脚本会自动保存已爬取的数据到 `cnki_projects_partial.xlsx`
- 可以手动调整超时时间：

```python
page.wait_for_load_state('networkidle', timeout=30000)  # 30秒
```

## 注意事项

⚠️ **重要提示**：

1. **遵守网站规则**：请遵守 CNKI 网站的使用条款和爬虫协议
2. **合理使用**：避免频繁请求，脚本已内置延迟机制
3. **数据用途**：爬取的数据仅供个人学习研究使用
4. **网络稳定**：确保网络连接稳定，避免中断
5. **浏览器版本**：确保 Chromium 浏览器驱动已正确安装

## 关于 BrowserTools MCP

虽然您安装了 BrowserTools MCP 插件，但该插件主要用于：
- 调试和监控网页
- 查看控制台日志
- 捕获网络请求
- 性能审计

**它不支持自动化操作**（如点击、表单填写等），因此本项目使用 Playwright 来实现完整的自动化爬取功能。

## 技术栈

- **Python 3.7+**
- **Playwright**：浏览器自动化
- **Pandas**：数据处理
- **OpenPyXL**：Excel 文件操作

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交 Issue。

