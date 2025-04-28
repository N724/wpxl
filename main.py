# -*- coding: utf-8 -*-
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Video
import logging
import aiohttp
import os
import uuid # For generating unique temporary filenames

logger = logging.getLogger(__name__)

@register(
    name="fatty_video",          # Unique plugin identifier
    trigger="微胖系列",           # User-facing trigger command
    desc="随机微胖系列视频",     # Short description
    version="1.0.0",            # Initial version
    author="Your Name Here"     # Change to your name/ID
)
class FattyVideoPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config  # Plugin configuration
        # Define the API URL
        self.api_url = "https://api.317ak.com/API/sp/wpxl.php"
        # Ensure a temporary directory exists (optional, adjust path as needed)
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp_videos")
        if not os.path.exists(self.temp_dir):
            try:
                os.makedirs(self.temp_dir)
            except OSError as e:
                logger.error(f"无法创建临时目录 {self.temp_dir}: {e}")
                # Fallback to current directory if creation fails
                self.temp_dir = "."

    @filter.command("微胖系列")
    async def get_fatty_video(self, event: AstrMessageEvent):
        # Check if the feature is enabled in the config
        if not self.config.get("enable_fatty_video", True):
            yield event.plain_result("微胖系列视频功能已被管理员关闭。")
            return

        temp_video_path = os.path.join(self.temp_dir, f"temp_video_{uuid.uuid4()}.mp4")
        
        try:
            logger.info(f"收到微胖系列视频请求，来自用户：{event.get_sender_id()}")
            async with aiohttp.ClientSession() as session:
                # Add a reasonable timeout (e.g., 30 seconds)
                async with session.get(self.api_url, timeout=30) as response:
                    # Check if the request was successful (HTTP 200 OK)
                    if response.status == 200:
                        # Check Content-Type if needed, though direct MP4 is expected
                        # content_type = response.headers.get("Content-Type", "")
                        # logger.debug(f"API Content-Type: {content_type}")

                        # Read the video data directly
                        video_data = await response.read()

                        if not video_data:
                             logger.warning("API 返回了空的视频数据。")
                             yield event.plain_result("😥 抱歉，未能获取到视频内容。")
                             return

                        # Save the video data to a temporary file asynchronously
                        # Using standard open for simplicity here, consider aiofiles for full async
                        try:
                            with open(temp_video_path, 'wb') as f:
                                f.write(video_data)
                            logger.info(f"视频已下载到临时文件：{temp_video_path}")
                        except IOError as e:
                            logger.error(f"无法写入临时视频文件 {temp_video_path}: {e}")
                            yield event.plain_result("😥 存储视频文件时出错，请稍后再试。")
                            return

                        # Send the video file
                        yield event.make_result().file_video(temp_video_path)
                        logger.info(f"已发送视频文件：{temp_video_path}")

                    else:
                        # Handle API errors based on status code
                        error_message = f"API 请求失败，状态码：{response.status}"
                        logger.error(error_message + f" URL: {self.api_url}")
                        # Provide user-friendly error message based on common codes
                        if response.status == 403:
                            yield event.plain_result("😥 请求被服务器拒绝，可能需要检查权限或 API 状态。")
                        elif response.status == 500 or response.status == 503:
                            yield event.plain_result("😥 服务器暂时遇到问题，请稍后再试。")
                        else:
                            yield event.plain_result(f"😥 获取视频时遇到错误 ({response.status})。")

        except aiohttp.ClientError as e:
            logger.error(f"请求微胖系列视频 API 时发生网络错误: {e}")
            yield event.plain_result("😥 网络连接失败，请检查网络或稍后再试。")
        except asyncio.TimeoutError:
             logger.error(f"请求微胖系列视频 API 超时: {self.api_url}")
             yield event.plain_result("😥 请求视频超时，请稍后再试。")
        except Exception as e:
            logger.exception(f"处理“微胖系列”命令时发生未知错误: {e}") # Use exception for stack trace
            yield event.plain_result("😥 处理请求时发生内部错误，请联系管理员。")
        finally:
            # Clean up the temporary file regardless of success or failure
            if os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                    logger.info(f"已删除临时视频文件：{temp_video_path}")
                except OSError as e:
                    logger.error(f"无法删除临时视频文件 {temp_video_path}: {e}")

    async def terminate(self):
        # Cleanup if needed when plugin stops
        pass

# You can add a help class like in the template if desired
# class FattyVideoHelp(Star):
#     def __init__(self, context: Context, config: dict):
#         super().__init__(context)
#         self.config = config
#
#     @filter.command("fatty_video帮助") # Or map to a general help command
#     async def help_message(self, event: AstrMessageEvent):
#         yield event.plain_result("发送“微胖系列”获取一个随机的相关视频。")
