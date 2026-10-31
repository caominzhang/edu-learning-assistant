# 群晖版 · 0.2.0-preview.1

适用有 Docker / Container Manager 的群晖；不是所有机型都支持。本版尚未在真实群晖上完成验收。

1. 将项目完整目录放到例如 `/volume1/docker/edu-learning-assistant`。
2. 把 `.env.example` 复制为 `.env`。填写孩子姓名、随机至少16位密码。将 TRACKER_BIND_IP 改为群晖实际的局域网 IP。不要把示例地址当作实际地址。
3. 在 Container Manager 的“项目”中新建项目，选中该目录，以 compose.yaml 构建并启动。命令行等价操作为 `docker compose up -d --build`。
4. 在同一局域网打开 `http://群晖实际局域网IP:8765/`，账号 admin，密码为自己的配置值。点击“新增记录”录成绩或上传截图，保存后检查原图、更新姓名确认状态。
5. 停止：项目面板停止，或 `docker compose stop`。启动：`docker compose start`。日志：项目日志，或 `docker compose logs --tail 100`。

容器名与服务名均为 edu-learning-assistant，容器内部 HTTP 8765；主机端口可在 .env 中修改。`./data` 映射至 `/app/data`，目录需要容器可写。数据库与原图都在这里。

镜像构建需要能访问 Python 镜像源、Debian 软件源及 Python 包源。镜像中安装中文 Tesseract；实际手写识别质量仍需人工核对。

这是单家庭实例。密码保护不等于加密传输。远程访问应使用 VPN 或配置 HTTPS 的反向代理；不要在路由器上转发 8765 到公网。反向代理需保留原始 Host 和 Authorization 头，以免影响来源检查和登录。

当前没有群晖 Chat 机器人。手机入口是浏览器上传。
