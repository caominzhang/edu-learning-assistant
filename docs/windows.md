# Windows 独立版 · 0.2.0-preview.1

架构：Tkinter 启动窗口 + 本机浏览器界面 + 内嵌 Python 服务。运行时不需要群晖、Docker、独立数据库或 Python 安装（使用打包产物时）。尚未完成 Windows 实机验收。

## 生成运行包（开发者操作）

在 Windows 上安装 Python 3.12，双击 build_windows.bat。生成 dist/EDULearningAssistant 文件夹。将整个文件夹打包分发，不能只复制 EXE。

也可以在 GitHub 仓库的 Actions 中手动运行 Build Windows preview，下载构建产物。这个工作流只生成构建附件，不自动发布 Release。

## 家长使用（取得运行包后）

1. 解压完整文件夹，打开 EDULearningAssistant.exe。
2. 输入关注的孩子姓名，点击“启动 / 打开学习档案”。
3. 浏览器自动打开，在“新增记录”录入成绩或选择图片上传；在详情页人工确认姓名。
4. 保持启动窗口打开。关闭该窗口会停止服务。关闭浏览器标签页不停止服务，可再次点击按钮打开。

程序只监听 127.0.0.1，使用系统分配的空闲端口，实际地址显示在启动窗口。其他手机和电脑不能通过局域网连接这个 Windows 版本。数据保存到 `%LOCALAPPDATA%\EDULearningAssistant`，通过“打开数据目录”查看，升级时保留该目录。

默认运行包没有 OCR 引擎；识别缺失不影响手工记录。开发者可另行安装 Tesseract 并配置 PATH，安装 chi_sim 及 eng 字库，再重启程序。正式免配置 OCR 包仍待制作和许可整理。

目前无安装器、托盘、自动启动、粘贴截图入口；图片通过网页文件选择器导入。Windows 崩溃或权限问题需要实机测试收集；窗口版本未写入独立日志文件，开发排错可用 Python 从终端启动 windows_launcher.py 查看错误。
