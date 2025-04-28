from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import httpx
import aiofiles
import time
from pathlib import Path
import random

@register("wpxl", "AstrBot", "微胖系列视频", "1.0.0")
class WpxlVideoPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "https://api.317ak.com/API/sp/wpxl.php"
        self.cache_dir = Path("./data/wpxl_videos")
        self.cache_dir.mkdir(exist_ok=True)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _fetch_video(self) -> Path:
        """获取并缓存视频"""
        try:
            resp = await self.client.get(self.api_url)
            resp.raise_for_status()
            
            if 'video/mp4' not in resp.headers.get('content-type', ''):
                raise ValueError("API返回非视频内容")
            
            filename = f"wpxl_{int(time.time())}_{random.randint(1000,9999)}.mp4"
            save_path = self.cache_dir / filename
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(resp.content)
            return save_path

        except httpx.HTTPStatusError as e:
            error_map = {
                400: "请求参数错误",
                403: "访问被拒绝",
                500: "服务器内部错误"
            }
            raise RuntimeError(error_map.get(e.response.status_code, "视频获取失败"))

    @filter.command("微胖", alias=['wpxl'])
    async def send_video(self, event: AstrMessageEvent):
        """发送随机视频"""
        try:
            yield event.plain_result("🔄 正在获取微胖系列视频...")
            video_path = await self._fetch_video()
            
            if event.platform in ("qq", "telegram"):
                yield event.video_result(str(video_path))
            else:
                yield event.plain_result(f"🎬 视频已保存: {video_path.name}")

        except Exception as e:
            self.logger.error(f"视频获取失败: {str(e)}")
            yield event.plain_result(f"❌ 获取失败: {str(e)}")

    @filter.command(["微胖开", "微胖关"])
    async def toggle_plugin(self, event: AstrMessageEvent):
        """插件开关控制"""
        group_id = str(event.message_obj.group_id)
        enabled = event.command == "微胖开"
        
        await self.set_group_enabled(group_id, enabled)
        yield event.plain_result(f"已{'启用' if enabled else '禁用'}微胖系列功能")

    def unload(self):
        """清理资源"""
        self.client.aclose()
