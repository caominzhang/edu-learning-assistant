# 交付与运维 · rev-1

软件与部署配置：0.2.0-preview.1；数据库：schema-1，沿用 v0.1 events 表，未执行结构迁移。文档日期：2026-11-01。

## 服务台账

| 项目 | 群晖 | Windows |
|---|---|---|
| 协议 | HTTP，远程建议 HTTPS 代理 | 本机 HTTP |
| 入口 | / | / |
| 端口 | 默认8765，可配置 | 系统分配，启动窗口显示 |
| 地址 | 由用户填写的群晖局域网IP | 127.0.0.1 |
| 服务/容器 | edu-learning-assistant | EDULearningAssistant.exe |
| 配置 | 项目目录 .env | 用户数据目录 settings.json |
| 数据 | 项目目录 data | %LOCALAPPDATA%/EDULearningAssistant |
| 数据文件 | records.sqlite3、uploads | records.sqlite3、uploads |
| 日志 | 容器标准输出及错误 | 暂无独立日志文件 |
| 权限 | 单家庭 admin；容器需写入data | 当前Windows用户；本机访问 |

无已部署的内外网实际地址或域名，本次仅交付源码与部署配置。

## 备份、迁移及回退

1. 停止程序或容器，避免备份时写入造成数据库与图片不一致。
2. 复制完整数据目录到私有备份位置；群晖另备份 .env，Windows 目录内已含 settings.json。配置含敏感信息，不要发到公开仓库。
3. 恢复时先停止目标实例，先备份目标旧数据，再把备份目录完整复制到目标数据目录。不要只复制数据库而遗漏 uploads。
4. Windows 与群晖可互迁 records.sqlite3 和 uploads，两个版本各自保留配置。校验目录权限后启动并检查记录数、原图和 CSV。
5. 从 v0.1 迁移同样遵循先停止、备份、复制整个数据目录；生产数据迁移尚待实机验证。
6. 回退前先停止并备份当前数据，将旧程序和对应备份一起恢复。将来如果有数据库结构升级，应使用对应版本备份，不能假设旧程序兼容新结构。

本次共享核心经过自动化 HTTP 冒烟检查；Windows GUI、PyInstaller产物、Docker构建、真实群晖和OCR字库仍需各自验收。不可将“已提供打包脚本”表述为“安装包已验证”。

该文档为可直接放入 Obsidian 的 Markdown；本次没有连接或写入用户实际 Obsidian 仓库。
