from django.shortcuts import render
from board.models import Board
from member.models import Member
from django.db.models import Q,F
from django.db.models import Count
from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse 
from comment.models import Comment
from member.models import Member

def nboard(request):  
    if request.method == "GET":
        # 파라미터 처리
        bselect = request.GET.get("bselect", "전체")
        bgps = request.GET.get("bgps", "서울특별시 강남구")
        list_search = request.GET.get("list_search", "").strip()

        # 기본 QuerySet 정의
        qs = Board.objects.annotate(comment_count=Count("comment", distinct=True))

        # 필터링 조건
        is_popular = bselect == "인기글"

        if bgps:
            qs = qs.filter(bgps__contains=bgps)

        # 제목 검색 조건 추가 (부분 일치 검색)
        if list_search:
            qs = qs.filter(
                Q(btitle__icontains=list_search) | Q(bcontent__icontains=list_search)
            )

        if bselect != "전체" and not is_popular:
            qs = qs.filter(bselect=bselect)

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = list(qs.values("btitle", "bcontent", "bgps", "bselect", "bdate"))
            return JsonResponse({"blist": data})

        # 정렬 순서 설정
        if is_popular:
            qs = qs.order_by("-like_member", "-comment_count")
            print("qs1 : ",qs)
        else:
            qs = qs.order_by("-bgroup", "bstep", "-comment_count")
            print("qs2 : ",qs)
        # 페이지 처리
        npage = int(request.GET.get("npage", 1))
        paginator = Paginator(qs, 10)
        blist = paginator.get_page(npage)

        # 댓글 수 계산
        comment_counts = {
            board.bno: Comment.objects.filter(board=board).count() for board in blist
        }

        # 시도, 시군구 파라미터 분리
        시도, 시군구 = "", ""
        if bgps:
            try:
                시도, 시군구 = bgps.split(" ", 1)
            except ValueError:
                시도, 시군구 = bgps, ""

        # 지역 목록 예시
        areas = [
            "서울특별시 강남구",
            "서울특별시 송파구",
            "경기도 성남시",
            "서울특별시 강서구",
            "경기도 부천시",
            "인천광역시 서구",
            "경기도 남양주시",
        ]

        context = {
        "blist": blist,
        'npage': npage,
        'comment_counts': comment_counts,
        '시도': 시도,
        '시군구': 시군구,
        'areas': areas,
        'current_bgps': bgps,
        'bselect': bselect,
        "list_search": list_search
    }
        print("qs3 : ",qs)
        print("bselect : ",bselect)
        print("blist : ",blist)
        return render(request, 'nboard.html', context)

    else:
        # 폼에서 검색어를 가져옵니다.
        search_keyword = request.POST.get('list_search', '').strip()  # search_keyword는 공백 제거한 검색어입니다.
        print(search_keyword)

        if search_keyword:
            # btitle에 검색어가 포함된 게시물들을 필터링합니다.
            blist = Board.objects.filter(btitle=search_keyword)  # 대소문자 구분 없이 검색
            num = '1'
        else:
            # 검색어가 없으면 모든 게시물을 가져옵니다.
            blist = Board.objects.all()
            num = '0'

        context = {'blist': blist, 'num': num, 'search_keyword':search_keyword}

    return render(request, 'nboard.html', context)

def bwrite(request):    # 1. 게시판글작성 호출 / 2. 게시판 글 작성 저장
  if request.method == 'GET':
    return render(request, 'bwrite.html')
  else:
    id = request.session.get('session_id')
    member = Member.objects.get(id=id)

    btitle = request.POST.get('btitle')
    bselect = request.POST.get('bselect')
    bcontent = request.POST.get('bcontent')
    bgps = request.POST.get('bgps')
    bfile = request.FILES.get("bfile","")

    qs = Board.objects.create(member=member,btitle=btitle,bselect=bselect,bcontent=bcontent,bgps=bgps,bfile=bfile)
    qs.bgroup = qs.bno
    qs.save()

    context = {'wmsg':'1'}
    return render(request,'bwrite.html',context)

def gps_test(request):    # gps테스트 호출(테스트)
  return render(request, 'gps_test.html')

def bbview(request,bno):    # 1. 게시글 상세보기 / 2. 좋아요 클릭 / 3. 이전글, 다음글 / 4. 댓글 리스트 출력 / 5. 조회수 늘리는 방법
  id = request.session["session_id"]
  member = Member.objects.get(id=id)
  
  qs__ = Board.objects.filter(bno=bno)
  if qs__[0].like_member.filter(pk=id).exists():
    result = "1"  # 좋아요 있으면
  else:
    result = "0"  # 좋아요 없으면
  count = qs__[0].like_member.count()
  print(count)
  npage = request.GET.get('npage',1)

    # 지역 목록 예시
  areas = [
      "서울특별시 강남구", 
      "서울특별시 송파구", 
      "경기도 성남시",
      "서울특별시 강서구",
      "경기도 부천시",
      "인천광역시 서구",
      "경기도 남양주시"
  ]

  qs = Board.objects.get(bno=bno)

  next_qs = Board.objects.filter(Q(bgroup__lt=qs.bgroup,bstep__lte=qs.bstep)|Q(bgroup=qs.bgroup,bstep__gt=qs.bstep)).order_by('-bgroup','bstep').first()
  prev_qs = Board.objects.filter(Q(bgroup__gt=qs.bgroup,bstep__gte=qs.bstep)|Q(bgroup=qs.bgroup,bstep__lt=qs.bstep)).order_by('bgroup','-bstep').first()
  
  c_qs = Comment.objects.filter(board=qs).order_by("-cgroup","cstep","cdate")
  print("확인 : ",c_qs,c_qs.count)

  bgps = request.GET.get('bgps', '') 
  시도, 시군구 = '', ''
  if bgps:
      try:
          시도, 시군구 = bgps.split(" ", 1)
      except ValueError:
          시도, 시군구 = bgps, ''
  
  day1 = datetime.replace(datetime.now(),hour=23,minute=59,second=59)
  expires = datetime.strftime(day1,"%a, %d-%b-%Y %H:%M:%S GMT")
  context = {'board':qs,'prev_qs':prev_qs,'next_qs':next_qs,"result":result,"count":count,"clist":c_qs,'areas': areas,'current_bgps': bgps}
  response = render(request,'bbview.html',context)

  if request.COOKIES.get("cookie_boardNo") is not None:
    cookies = request.COOKIES.get("cookie_boardNo")
    cookies_list = cookies.split("|")
    if str(bno) not in cookies_list:
      ## 쿠키저장
      response.set_cookie("cookie_boardNo",cookies+f"|{bno}",expires=expires)
      ## 조회수 1증가
      qs.bhit += 1
      qs.save()
  else:  ## 쿠키저장
    response.set_cookie('cookie_boardNo',bno,expires=expires)
    ## 조회수 1증가
    qs.bhit += 1
    qs.save()
  return response 

def bdelete(request,bno):    # 글 삭제하기
  Board.objects.get(bno=bno).delete()
  context = {"dmsg":bno}
  return render(request,'nboard.html',context)

def bmodify(request,bno):   # 1. 글수정페이지 호출 / 2. 글수정 저장
  if request.method == 'GET':
    qs = Board.objects.get(bno=bno)
    context = {"board":qs}
    return render(request,'bmodify.html',context)
  else:
    btitle = request.POST.get("btitle")
    bcontent = request.POST.get("bcontent")
    bgps = request.POST.get("bgps")
    bselect = request.POST.get("bselect")
    bfile = request.FILES.get("bfile","")   # file 안 넣으면 빈 공백
    print("파일정보 :",bfile)

    ## 게시글 수정 저장 / 입력해야하는 것 : member, btitle, bcontent, bgps, bselect, bfile
    qs = Board.objects.get(bno=bno)
    qs.btitle = btitle
    qs.bcontent = bcontent
    qs.bgps = bgps
    qs.bselect = bselect
    if bfile: qs.bfile = bfile
    qs.save()

    context = {'umsg':bno}
    return render(request,'bmodify.html',context)

def likes(request):   # 좋아요 숫자증가
  id = request.session["session_id"]
  member = Member.objects.get(id=id)
  bno = request.POST.get("bno")
  board = Board.objects.get(bno=bno)

  if board.like_member.filter(pk=id).exists():
    ## 좋아요 클릭했을 때,
    board.like_member.remove(member)
    result = "remove"  # 좋아요 삭제
  else:
    board.like_member.add(member)
    result = "add"  # 좋아요 추가
  print("좋아요 갯수 확인",board.like_member.count())
  context = {"result":result,"count":board.like_member.count()}
  return JsonResponse(context)


# 매달 1일 인기 상위글 5개의 작성자에게 포인트 1000 지급
def reward_points_on_first_day():
  # 1. 현재 날짜가 1일인지 확인
  today = datetime.today()
  # if today.day!= 1:
  if today.day!= 1: # test
    return # 1일이 아니라면 아무작업도 하지 않음
  
  # 2. 좋아요가 많은 상위 5개 게시글 찾기
  top_boards = Board.objects.annotate(like_count=Count('like_member')).order_by('-like_count')[:5]
  print("top_boards: ",top_boards)

  # 3. 게시글 작성자에게 포인트 지급
  rewarded_members = set(board.member for board in top_boards) # 중복을 방지할 집합
  print("rewarded_members : ", rewarded_members)
  
  # 4. F()를 사용해서 포인트를 한번에 업데이트
  # Member.objects.filter()로 해당 유저를 찾아 F()로 포인트 추가
  Member.objects.filter(id__in=[member.id for member in rewarded_members]).update(point=F('point')+1000) # 1000 포인트 지급
    
  print("포인트 지급 완료")


def execute_reward_points(request):
    if request.method == 'POST':
        # reward_points_on_first_day() 함수 실행
        reward_points_on_first_day()
        
        # 성공적으로 처리되었음을 JSON으로 응답
        return JsonResponse({'success': True})
    
    # 잘못된 요청일 경우
    return JsonResponse({'success': False}, status=400)

# def addLike(request):
#     qs = Board.objects.get(bno=26)
#     mem_list = [
#         "aaaa92",
#         "bbbb31",
#         "eeee35",
#         "dddd38",
#         "eeee42",
#         "aaaa46",
#         "cccc49",
#         "cccc52",
#         "bbbb56",
#         "cccc59",
#         "cccc63",
#         "eeee67",
#         "eeee70",
#         "dddd73",
#         "bbbb76",
#         "aaaa79",
#         "dddd82",
#         "aaaa85",
#         "aaaa89",
#         "eeee93",
#         "eeee97",
#         "aaaa100",
#         "bbbb3",
#         "eeee6",
#         "dddd10",
#         "eeee15",
#     ]
#     for mem in mem_list:
#       print(mem)
#       member = Member.objects.get(id=mem)
#       qs.like_member.add(member)
#       print("추가 완료")
#       print(qs.like_member.count())
