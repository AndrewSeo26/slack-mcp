import requests
from typing import Dict, List, Optional, Any, Tuple
import json
import re
from collections import Counter


class SlackAPIClient:
    """Slack API와 상호작용하기 위한 클라이언트 클래스"""
   
    def __init__(self, bot_token: str):
        """
        Slack API 클라이언트 초기화
       
        Args:
            bot_token: Slack Bot User OAuth Token
        """
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            'Authorization': f'Bearer {bot_token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
   
    def _make_request(
            self, endpoint: str, method: str = "GET", 
            data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Slack API에 HTTP 요청을 보내는 헬퍼 메서드
       
        Args:
            endpoint: API 엔드포인트
            method: HTTP 메서드 (GET, POST)
            data: 요청 데이터
           
        Returns:
            API 응답 딕셔너리
           
        Raises:
            Exception: API 요청 실패 시
        """
        url = f"{self.base_url}/{endpoint}"
       
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            else:
                response = requests.post(url, headers=self.headers, json=data)
           
            response.raise_for_status()
            result = response.json()
           
            if not result.get('ok', False):
                error_msg = result.get('error', 'Unknown error')
                raise Exception(f"Slack API 오류: {error_msg}")
           
            return result
           
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP 요청 실패: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON 파싱 실패: {str(e)}")
   
    def send_message(self, channel: str, text: str) -> Dict[str, Any]:
        """
        지정된 채널에 메시지 전송
       
        Args:
            channel: 채널 ID 또는 채널명 (예: #general, C1234567890)
            text: 전송할 메시지 내용
           
        Returns:
            전송된 메시지 정보
        """
        data = {
            'channel': channel,
            'text': text
        }
        return self._make_request('chat.postMessage', 'POST', data)
   
    def get_channels(self) -> List[Dict[str, Any]]:
        """
        접근 가능한 모든 채널 목록 조회
       
        Returns:
            채널 정보 리스트
        """
        data = {
            'types': 'public_channel,private_channel',
            'exclude_archived': True
        }
        result = self._make_request('conversations.list', 'GET', data)
        return result.get('channels', [])
   
    def get_channel_history(
            self, channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        지정된 채널의 메시지 히스토리 조회
       
        Args:
            channel_id: 조회할 채널의 ID
            limit: 조회할 메시지 수 (기본값: 10, 최대: 100)
           
        Returns:
            메시지 리스트
        """
        if limit > 100:
            limit = 100
       
        data = {
            'channel': channel_id,
            'limit': limit
        }
        result = self._make_request('conversations.history', 'GET', data)
        return result.get('messages', [])
   
    def open_dm_channel(self, user_id: str) -> str:
        """
        사용자와의 DM 채널 열기
       
        Args:
            user_id: 사용자 ID
           
        Returns:
            DM 채널 ID
        """
        data = {
            'users': user_id
        }
        result = self._make_request('conversations.open', 'POST', data)
        return result['channel']['id']
   
    def send_direct_message(self, user_id: str, text: str) -> Dict[str, Any]:
        """
        특정 사용자에게 다이렉트 메시지 전송
       
        Args:
            user_id: 메시지를 받을 사용자의 ID
            text: 전송할 메시지 내용
           
        Returns:
            전송된 메시지 정보
        """
        dm_channel_id = self.open_dm_channel(user_id)
        return self.send_message(dm_channel_id, text)
   
    def get_users(self) -> List[Dict[str, Any]]:
        """
        워크스페이스의 모든 사용자 정보 조회
       
        Returns:
            사용자 정보 리스트
        """
        result = self._make_request('users.list', 'GET')
        return result.get('members', [])
   
    def _extract_words_from_text(self, text: str) -> List[str]:
        """
        텍스트에서 단어를 추출하는 헬퍼 메서드
       
        Args:
            text: 분석할 텍스트
           
        Returns:
            추출된 단어 리스트
        """
        if not text:
            return []
       
        # 한글, 영문, 숫자만 남기고 나머지는 공백으로 치환
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        # 여러 공백을 하나로 통일
        text = re.sub(r'\s+', ' ', text)
        # 소문자로 변환하고 단어 분리
        words = text.lower().split()
        
        # 의미 없는 단어들 제거 (불용어)
        stop_words = {
            '의', '가', '이', '은', '는', '을', '를', '에', '에서', '으로', '로', 
            '과', '와', '한', '하는', '하고', '해서', '하여', '하면', '됩니다', 
            '있습니다', '입니다', '그', '그런', '이런', '저런', '것', '수', '등',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 
            'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # 불용어 제거 및 2자 이상 단어만 유지
        filtered_words = [
            word for word in words 
            if len(word) >= 2 and word not in stop_words
        ]
        
        return filtered_words
   
    def analyze_channel_word_frequency(
            self, channel_id: str, limit: int = 100) -> List[Tuple[str, int]]:
        """
        채널의 메시지 히스토리를 분석하여 가장 많이 사용된 단어들을 반환
       
        Args:
            channel_id: 분석할 채널의 ID
            limit: 조회할 메시지 수 (기본값: 100, 최대: 1000)
           
        Returns:
            (단어, 빈도수) 튜플의 리스트 (빈도순으로 정렬)
        """
        if limit > 1000:
            limit = 1000
            
        # 메시지 히스토리 조회
        messages = self.get_channel_history(channel_id, min(limit, 100))
        
        # 모든 메시지 텍스트 수집
        all_words = []
        for message in messages:
            if 'text' in message and message.get('type') == 'message':
                # 봇 메시지나 시스템 메시지 제외
                if not message.get('bot_id') and not message.get('subtype'):
                    words = self._extract_words_from_text(message['text'])
                    all_words.extend(words)
        
        # 단어 빈도 계산
        word_counter = Counter(all_words)
        
        # 빈도순으로 정렬하여 반환
        return word_counter.most_common()
   
    def get_top_words_in_channel(self, channel_id: str, 
                                 top_n: int = 10, 
                                 message_limit: int = 100) -> Dict[str, Any]:
        """
        채널에서 가장 많이 사용된 상위 N개 단어 조회
       
        Args:
            channel_id: 분석할 채널의 ID
            top_n: 반환할 상위 단어 개수 (기본값: 10)
            message_limit: 분석할 메시지 수 (기본값: 100)
           
        Returns:
            분석 결과 딕셔너리 (채널 정보, 상위 단어들, 통계 정보 포함)
        """
        try:
            # 단어 빈도 분석
            word_frequency = self.analyze_channel_word_frequency(
                channel_id, message_limit)
            
            # 상위 N개 단어 추출
            top_words = word_frequency[:top_n]
            
            # 전체 통계
            total_words = sum(count for _, count in word_frequency)
            unique_words = len(word_frequency)
            
            return {
                'success': True,
                'channel_id': channel_id,
                'analysis_stats': {
                    'total_words_analyzed': total_words,
                    'unique_words': unique_words,
                    'message_limit': message_limit
                },
                'top_words': [
                    {
                        'word': word,
                        'count': count,
                        'percentage': (round((count / total_words) * 100, 2) 
                                       if total_words > 0 else 0)
                    }
                    for word, count in top_words
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"단어 분석 실패: {str(e)}",
                'channel_id': channel_id
            } 