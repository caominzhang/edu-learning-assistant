# Windows 安装版 · 0.2.0-preview.1 / installer.1

适用 Windows 10/11 64 位。安装后无需 Python、群晖、Docker 或独立数据库。默认不含 OCR 引擎和中文字库，可手工录入成绩、上传图片、人工确认姓名。

## 安装与使用

1. 下载并解压安装包 ZIP，双击 EDU_Learning_Assistant_0.2.0-preview.1_Setup_x64.exe。
2. 按安装向导完成安装，从开始菜单打开 EDU Learning Assistant。
3. 输入孩子姓名或昵称，点击“启动 / 打开学习档案”。
4. 浏览器打开后，在“新增记录”录成绩、上传截图；在记录详情人工确认姓名。
5. 保持启动窗口打开，关闭窗口会停止服务。关闭浏览器标签页不会停止程序。

安装包未做代码签名，可能显示发布者未知。安装器只安装给当前用户，不要求管理员权限；可选择创建桌面快捷方式。

## 数据和服务台账

- 程序：%LOCALAPPDATA%/Programs/EDULearningAssistant/EDULearningAssistant.exe。
- 配置与数据：%LOCALAPPDATA%/EDULearningAssistant；settings.json 为姓名配置，records.sqlite3 为数据库，uploads 为原图。
- 入口：本机 HTTP 127.0.0.1，端口由系统分配，实际完整地址显示在启动窗口；没有公网地址，手机不能连接。
- 启动：开始菜单或 EXE；停止：关闭启动窗口。暂无独立日志文件。
- 备份：先关闭程序，再复制完整数据目录。升级和卸载保留学习数据。
- 回退：关闭程序，备份现有数据，安装旧版本，再按对应数据库版本恢复备份。当前数据库仍为 schema-1。

## 构建与验证

在 GitHub Actions 运行 Build Windows installer，下载 EDU-Learning-Assistant-Windows-Installer 构建附件。附件保存30天，过期后可重新构建。流程生成安装向导、中文说明、SHA256及验证记录，不自动发布 Release。

installer.1 已在 GitHub Windows Server 2025 x64 环境完成：核心 HTTP 检查、打包后核心检查、静默安装、应用进程启动及卸载检查。未在用户个人 Windows 10/11 电脑完成交互验收，预览版仍需实际使用反馈。进程启动检查不等于逐项验证所有界面操作。

应用使用 Tkinter 启动窗口和本机浏览器。可在 Windows 安装 Python 3.12 后运行 build_windows.bat 生成便携目录；不能只复制其中的 EXE。

## OCR 和已知限制

Tesseract 引擎、chi_sim 和 eng 字库暂未内置；若需本地 OCR，可另行安装并配置 PATH 后重启。未提供托盘、开机启动或剪贴板粘贴。不要因未识别到姓名就判断孩子没有出现。

安装目录包含 LICENSE.txt、THIRD_PARTY_LICENSES.txt 和 BUILD_DEPENDENCIES.txt。源码采用 MIT，各依赖保留各自许可。
