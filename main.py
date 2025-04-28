#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import hashlib
import uuid
import json
import aiohttp
import asyncio
from enum import Enum
from typing import List, Dict, Optional
from astrbot.api.all import AstrMessageEvent, CommandResult, Context
import astrbot.api.event.filter as filter
from astrbot.api.star import register, Star

logger = logging.getLogger("astrbot")

class Emoji(Enum):
    ACCOUNT = "👤"
    SUCCESS = "🎉"
    FAILURE = "❌"
    TASK = "✅"
    LOTTERY = "🎰"
    GIFT = "🎁"
    WARNING = "⚠️"
    HEART = "❤️"
    TROPHY = "🏆"

@register("xiaocan", "小蚕助手", "小蚕抽奖任务自动化插件", "1.0.0")
class XiaoCanPlugin(Star):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.api_url = "https://gwh.xiaocantech.com/rpc"
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.task_ids = [1, 2, 4, 5, 8, 9, 10, 11]
        
    def _generate_headers(self, cookie: str) -> Dict[str, str]:
        """生成请求头"""
        vayne, teemo, token = cookie.split('#')
        return {
            "x-vayne": vayne,
            "x-teemo": teemo,
            "x-sivir": token,
            "x-platform": "mini",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            "servername": "SilkwormLottery",
            "methodname": "SilkwormLotteryMobile.Lottery"
        }

    async def _make_request(self, headers: Dict, data: Dict) -> Optional[Dict]:
        """发送API请求"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(self.api_url, headers=headers, json=data) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.error(f"API请求失败 HTTP {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            return None

    async def complete_task(self, cookie: str, task_id: int) -> str:
        """完成单个任务"""
        headers = self._generate_headers(cookie)
        headers["methodname"] = "SilkwormLotteryMobile.AddLotteryTimes"
        data = {"silk_id": int(headers["x-teemo"]), "type": task_id}
        
        result = await self._make_request(headers, data)
        if result and result.get('status', {}).get('code') == 0:
            return f"{Emoji.TASK.value} 任务ID[{task_id}]完成成功"
        return f"{Emoji.FAILURE.value} 任务ID[{task_id}]失败"

    async def perform_lottery(self, cookie: str) -> str:
        """执行抽奖"""
        headers = self._generate_headers(cookie)
        headers["methodname"] = "SilkwormLotteryMobile.Lottery"
        data = {"silk_id": int(headers["x-teemo"]), "prize_type": 1}
        
        result = await self._make_request(headers, data)
        if result and result.get('status', {}).get('code') == 0:
            prize = result.get('prize', {}).get('name', '未知奖品')
            return f"{Emoji.LOTTERY.value} 抽奖成功: {prize}"
        return f"{Emoji.FAILURE.value} 抽奖失败"

    @filter.command("小蚕抽奖")
    async def xiaocan_lottery(self, event: AstrMessageEvent) -> CommandResult:
        '''执行小蚕抽奖任务 (需要配置COOKIE)'''
        cookie = os.getenv("XIAOCAN_COOKIE")
        if not cookie:
            return CommandResult().error(f"{Emoji.WARNING.value} 未配置COOKIE")
            
        try:
            yield CommandResult().message(f"{Emoji.HEART.value} 开始执行小蚕任务...")
            
            # 执行所有任务
            for task_id in self.task_ids:
                msg = await self.complete_task(cookie, task_id)
                yield CommandResult().message(msg)
                await asyncio.sleep(random.uniform(5, 8))
                
            # 执行抽奖
            result = await self.perform_lottery(cookie)
            yield CommandResult().message(f"{Emoji.TROPHY.value} {result}")
            
        except Exception as e:
            logger.error(f"执行异常: {str(e)}")
            return CommandResult().error(f"{Emoji.FAILURE.value} 任务执行失败")

    @filter.command("小蚕帮助")
    async def xiaocan_help(self, event: AstrMessageEvent) -> CommandResult:
        """获取帮助信息"""
        help_msg = [
            f"{Emoji.ACCOUNT.value} 小蚕抽奖插件使用说明",
            "━" * 20,
            "/小蚕抽奖 - 执行抽奖任务链",
            "/小蚕帮助 - 显示本帮助",
            "━" * 20,
            f"{Emoji.WARNING.value} 需要先配置环境变量XIAOCAN_COOKIE",
            "格式: vayne#teemo#token"
        ]
        return CommandResult().message("\n".join(help_msg))
