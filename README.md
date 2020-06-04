# webtoon_comment
네이버 웹툰 댓글을 크롤링 한 후 LDA로 분석하였습니다.

### 네이버 웹툰 댓글 크롤링은 오로지 연구목적으로만 이용하셔야 됩니다.
### 상업적인 용도로는 절대 사용하셔서는 안됩니다.


**webtoon_comment_crawler.py** : 네이버 웹툰 댓글을 크롤링 하는 파일입니다.  
CMD나 anaconda prompt에서 해당 파일이 있는 위치로 가셔서 다음을 입력하시면 됩니다.   
**python webtoon_comment_crawler.py --number_of_episode=원하는 에피소드 개수**  

예를들어

python webtoon_comment_crawler.py --number_of_episode=3

위와 같이 입력할시 하나의 웹툰마다 최신 에피소드를포함한 이전 3화까지의 댓글들을 수집하게됩니다.  
기본값은 50화입니다. 

### 참고사항

- mysql  
기본적으로 ./data/naver_webtoon_comments.txt파일에 댓글들을 저장하고 있습니다.  
mysql에 댓글을 저장하고 싶으실경우 mysql서버를 켜신 상태에서  
1. naver라는 DB와 comment라는 table을 생성  
2. webtoon_comment_crawler.py에 있는 mysql관련 코드의 주석을 해제  
3. ./config/mysql_config.py라는 파일을 생성 후 아래의 항목을 입력해주시면 되겠습니다.  

mysql_info = {  
    "host": "127.0.0.1",  
    "user": "유저명",  
    "passwd": "비밀번호",  
    "db": 'mysql'  
}  
  
user와 passwd 항목에 mysql서버 실행시 사용된 "유저명"과 "비밀번호"를 입력하면 되겠습니다.   
그 후 python webtoon_comment_crawler.py로 댓글을 수집하시면 되겠습니다.   

- ajax link  
python webtoon_comment_crawler.py 의 get_commentList 함수에   
ajax_link라는 변수가 있습니다.   
여기에 할당된 url은 어떤 하나의 웹툰의 에피소드의 댓글페이지에서 댓글을 수집한 후 다음 댓글의 페이지로 넘어갈때  
요청하는 url입니다. ajax로 비동기통신을 이용하고 있습니다.  
간혹 이 url이 작동하지 않을때가 있습니다. 그런 경우 어떤 하나의 네이버 웹툰 댓글 페이지에 가셔서   
개발자 도구를 켜신 상태에서 댓글 페이지를 옮길때 발생하는 네트워크 통신 항목의 Request URL을 확인하신 후  
코드를 직접 수정하시면 되겠습니다.  
