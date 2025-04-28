# 小蚕抽奖插件

自动完成小蚕抽奖任务链的AstrBot插件

## 功能特性
- 自动完成全部8项日常任务
- 自动执行抽奖
- 支持多账号配置
- 完善的错误处理

## 安装配置
1. 将插件放入`plugins`目录
2. 安装依赖:
   ```bash
   pip install aiohttp
   ```
3. 配置环境变量:
   ```bash
   export XIAOCAN_COOKIE="vayne#teemo#token"
   ```

## 使用命令
| 命令 | 说明 |
|------|------|
| `/小蚕抽奖` | 执行完整任务链 |
| `/小蚕帮助` | 查看帮助信息 |

## 接口说明
```python
API端点: POST https://gwh.xiaocantech.com/rpc
请求头: 需要x-vayne/x-teemo/x-sivir等认证参数
```

## 注意事项
1. 每个账号每小时最多执行3次
2. 需要自行获取有效cookie
3. 非官方插件，请合理使用
