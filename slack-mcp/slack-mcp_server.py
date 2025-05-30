import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from fastmcp import FastMCP
from slack_api import SlackAPIClient


# 환경 변수 로드
load_dotenv()


# FastMCP 인스턴스 생성
mcp = FastMCP("Slack MCP Server")


# Slack API 클라이언트 초기화
slack_token = os.getenv('SLACK_BOT_TOKEN')
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")


slack_client = SlackAPIClient(slack_token)




@mcp.tool()
async def send_slack_message(channel: str, text: str) -> Dict[str, Any]:
    """
    지정된 Slack 채널에 메시지를 전송합니다.
   
    Args:
        channel: 채널 ID 또는 채널명 (예: #general, C1234567890)
        text: 전송할 메시지 내용
       
    Returns:
        전송 결과 정보
    """
    try:
        result = slack_client.send_message(channel, text)
        return {
            "success": True,
            "message": "메시지가 성공적으로 전송되었습니다.",
            "channel": result.get('channel'),
            "timestamp": result.get('ts'),
            "text": text
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"메시지 전송 실패: {str(e)}"
        }




@mcp.tool()
async def get_slack_channels() -> Dict[str, Any]:
    """
    접근 가능한 모든 Slack 채널 목록을 조회합니다.
   
    Returns:
        채널 목록 정보
    """
    try:
        channels = slack_client.get_channels()
        channel_list = []
       
        for channel in channels:
            channel_info = {
                "id": channel.get('id'),
                "name": channel.get('name'),
                "is_private": channel.get('is_private', False),
                "is_member": channel.get('is_member', False),
                "topic": channel.get('topic', {}).get('value', ''),
                "purpose": channel.get('purpose', {}).get('value', ''),
                "num_members": channel.get('num_members', 0)
            }
            channel_list.append(channel_info)
       
        return {
            "success": True,
            "channels": channel_list,
            "total_count": len(channel_list)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"채널 목록 조회 실패: {str(e)}"
        }




@mcp.tool()
async def get_slack_channel_history(channel_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    지정된 채널의 최근 메시지 히스토리를 조회합니다.
   
    Args:
        channel_id: 조회할 채널의 ID
        limit: 조회할 메시지 수 (기본값: 10, 최대: 100)
       
    Returns:
        메시지 히스토리 정보
    """
    try:
        messages = slack_client.get_channel_history(channel_id, limit)
        message_list = []
       
        for message in messages:
            message_info = {
                "text": message.get('text', ''),
                "user": message.get('user', ''),
                "timestamp": message.get('ts', ''),
                "type": message.get('type', ''),
                "subtype": message.get('subtype', '')
            }
            message_list.append(message_info)
       
        return {
            "success": True,
            "messages": message_list,
            "channel_id": channel_id,
            "message_count": len(message_list)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"메시지 히스토리 조회 실패: {str(e)}"
        }




@mcp.tool()
async def send_slack_direct_message(user_id: str, text: str) -> Dict[str, Any]:
    """
    특정 사용자에게 1:1 다이렉트 메시지를 전송합니다.
   
    Args:
        user_id: 메시지를 받을 사용자의 ID
        text: 전송할 메시지 내용
       
    Returns:
        전송 결과 정보
    """
    try:
        result = slack_client.send_direct_message(user_id, text)
        return {
            "success": True,
            "message": "다이렉트 메시지가 성공적으로 전송되었습니다.",
            "user_id": user_id,
            "timestamp": result.get('ts'),
            "text": text
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"다이렉트 메시지 전송 실패: {str(e)}"
        }




@mcp.tool()
async def get_slack_users() -> Dict[str, Any]:
    """
    워크스페이스의 모든 사용자 정보를 조회합니다. (선택 기능)
   
    Returns:
        사용자 목록 정보
    """
    try:
        users = slack_client.get_users()
        user_list = []
       
        for user in users:
            if not user.get('deleted', False):  # 삭제되지 않은 사용자만
                user_info = {
                    "id": user.get('id'),
                    "name": user.get('name'),
                    "real_name": user.get('real_name', ''),
                    "display_name": user.get('profile', {}).get('display_name', ''),
                    "email": user.get('profile', {}).get('email', ''),
                    "is_bot": user.get('is_bot', False),
                    "is_admin": user.get('is_admin', False)
                }
                user_list.append(user_info)
       
        return {
            "success": True,
            "users": user_list,
            "total_count": len(user_list)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"사용자 목록 조회 실패: {str(e)}"
        }




if __name__ == "__main__":
    mcp.run() 