#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import random
from typing import Optional
from astrbot.api.all import AstrMessageEvent, CommandResult, Context
import astrbot.api.event.filter as filter
from astrbot.api.star import register, Star

logger = logging.getLogger("astrbot")

@register("wpxl", "微胖系列", "随机返回微胖系列视频", "1.0.0")
class WpxlPlugin(Star):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.api_url = "https://api.317ak.com/API/sp/wpxl.php"
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.error_msgs = [
            "视频加载失败，请稍后再试~",
            "网络不太顺畅呢...",
            "视频获取出错啦！",
            "服务器开小差了..."
        ]

    async def fetch_video(self) -> Optional[str]:
        """获取随机微胖视频"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.api_url) as resp:
                    if resp.status == 200:
                        return self.api_url  # 直接返回视频URL
                    
                    logger.error(f"API请求失败 HTTP {resp.status}")
                    return None

        except aiohttp.ClientError as e:
            logger.error(f"网络请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"未知异常: {str(e)}", exc_info=True)
            return None

    @filter.command("微胖")
    async def wpxl_video(self, event: AstrMessageEvent):
        '''随机返回一段微胖系列视频'''
        try:
            yield CommandResult().message("🔄 正在获取微胖系列视频...")
            
            video_url = await self.fetch_video()
            if not video_url:
                yield CommandResult().error(random.choice(self.error_msgs))
                return
            
            yield CommandResult().video(video_url)

        except Exception as e:
            logger.error(f"处理指令异常: {str(e)}", exc_info=True)
            yield CommandResult().error("💥 视频服务暂时不可用")

    @filter.command("微胖帮助")
    async def wpxl_help(self, event: AstrMessageEvent):
        """获取帮助信息"""
        help_msg = [
            "📘 微胖系列使用说明：",
            "/微胖 - 随机获取一段微胖系列视频",
            "/微胖帮助 - 显示本帮助信息",
            "━" * 20,
            "注意事项：",
            "🔸 视频内容为随机返回",
            "🔸 如遇失败请稍后重试",
            "🔸 每日调用限制100次"
        ]
        yield CommandResult().message("\n".join(help_msg))
