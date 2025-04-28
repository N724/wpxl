import httpx
from astrbot import EventBus, BotPlugin, MessageEvent
from pathlib import Path

# 常量定义
API_URL = "https://api.317ak.com/API/sp/wpxl.php"
TEMP_DIR = Path("./temp/wpxl")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

class WpxlPlugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _download_video(self) -> Path:
        """下载视频到本地临时文件"""
        try:
            resp = await self.client.get(API_URL, follow_redirects=True)
            resp.raise_for_status()

            if resp.headers['content-type'] != 'video/mp4':
                self.logger.error(f"非视频返回类型: {resp.headers}")
                raise ValueError("Invalid content type")

            file_path = TEMP_DIR / f"wpxl_{int(time.time())}.mp4"
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(resp.content)
            return file_path

        except httpx.HTTPStatusError as e:
            error_map = {
                400: "请求参数错误",
                403: "服务器拒绝访问",
                405: "请求方法不被允许",
                408: "请求超时",
                500: "服务器内部错误",
                503: "系统维护中"
            }
            error_msg = error_map.get(e.response.status_code, f"HTTP错误: {e.response.status_code}")
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    @EventBus.on_command("#微胖", "#wpxl")
    async def handle_command(self, event: MessageEvent):
        try:
            # Step 1: 下载视频
            await event.reply("正在获取视频，请稍候...")
            video_path = await self._download_video()

            # Step 2: 发送视频（不同平台适配）
            if event.platform == "qq":
                await event.reply(file=video_path, type="video")
            elif event.platform == "telegram":
                await event.reply_video(video_path)
            else:
                await event.reply(f"视频已生成：[点击下载]({API_URL})")

        except Exception as e:
            await event.reply(f"获取失败: {str(e)}")
            self.logger.exception("视频获取异常")

    def unload(self):
        # 插件卸载时清理资源
        self.client.close()
        super().unload()
