from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.core import serializers 
from member.models import Member
from django.core.mail import get_connection, EmailMessage
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib import messages
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from django.contrib.auth.hashers import make_password  # 비밀번호 암호화
from django.contrib.auth.hashers import check_password  # 암호화 된 비밀번호와 원래 비밀번호 비교

# Member.pw에서 hash화 되있지 않은 비밀번호를 hash화 시키는 함수
# hash된 비밀번호는 skip

# def hash_pw(request):
#   print("비밀번호 암호화 시작")
#   members = Member.objects.all()
#   for idx,member in enumerate(members):
#     print(idx,"번째 : ",member.pw)
#     if not member.pw.startswith("pbkdf2_sha256"):
#       member.pw = make_password(member.pw)
#       member.save()
#   print("비밀번호 암호화 완료")
#   return redirect(request, '/')








# -------------------------- 회원 탈퇴 / 비밀번호 확인 -------------------------- 
def forDeleteAccount(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    id = request.session.get("session_id")
    pw = request.POST.get("pw", "")

    # 세션에 저장되어 있는 아이디로 회원 검색
    user = Member.objects.get(id=id)
    
    # 입력된 비밀번호와 저장된 암호화된 비밀번호 비교
    if check_password(pw, user.pw):
      context = {"result": "success", "message": "비밀번호가 확인되었습니다."}  # member 정보를 JSON으로 반환
      user.delete()
      request.session.clear()
      print("회원 삭제 완료.")
    else:
      context = {"result": "fail", "message": "비밀번호가 일치하지 않습니다."}
  
    
    return JsonResponse(context)


def deleteAccount(request):
  return render(request, "deleteAccount.html")

# -------------------------- 비밀번호 확인 --------------------------'
def forPasswordCheck(request):
  if request.method == "GET":
    context = {"result": "error", "message": "잘못된 요청입니다."}
    return JsonResponse(context)
  
  else:
    id = request.session.get("session_id")
    pw = request.POST.get("pw", "")

    # 세션에 저장되어 있는 아이디로 회원 검색
    user = Member.objects.get(id=id)
    
    # 입력된 비밀번호와 저장된 암호화된 비밀번호 비교
    if check_password(pw, user.pw):
      context = {"result": "success", "message": "비밀번호가 확인되었습니다."}  # member 정보를 JSON으로 반환
    else:
      context = {"result": "fail", "message": "비밀번호가 일치하지 않습니다."}

    return JsonResponse(context)

def passwordCheck(request):
  return render(request, "passwordCheck.html")

# -------------------------- 회원정보 수정 --------------------------
def changeInfoNewPwChk(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    mId = request.session.get("session_id")
    
    if not id:
      return JsonResponse({"result": "error", "message": "세션이 만료되었습니다. 다시 시도해주세요."})

    newPw = request.POST.get("newPw", "")
    newPwChk = request.POST.get("newPwChk", "")

    if newPw != newPwChk:
      return JsonResponse({"result": "error", "message": "비밀번호 확인란을 정확히 입력하세요."})

    try:
      # 세션에 저장되어 있는 아이디로 사용자 찾기
      user = Member.objects.get(id=mId)
      
      # 입력된 새 비밀번호와 저장된 암호화된 기존 비밀번호 비교
      if check_password(newPw, user.pw):
        return JsonResponse({"result": "error", "message": "기존 비밀번호와 동일합니다. 다른 비밀번호를 사용해 주세요."})

      # 비밀번호 업데이트
      user.pw = make_password(newPw) # 비밀번호 암호화
      user.save()

      print(f"새 비밀번호 : {newPw}")

      return JsonResponse({"result": "success", "message": "비밀번호가 성공적으로 변경되었습니다."})
    
    except Member.DoesNotExist:
      return JsonResponse({"result": "error", "message": "사용자를 찾을 수 없습니다."})
    except Exception as e:
      return JsonResponse({"result": "error", "message": f"오류 발생: {str(e)}"})

## 회원정보 수정에서 비밀번호 변경할 때 넘어가는 페이지
def changeInfoNewPw(request):
  return render(request, "changeInfoNewPw.html")

### 수정버튼 클릭 시

### 회원정보 수정 페이지
def changeInfo(request):
  mId = request.session.get("session_id")
  mInfo = Member.objects.get(id=mId)

  context = {"member": mInfo}
  print(mInfo)
  
  return render(request, "changeInfo.html", context)

# ------------------------------------------------------------------
## 약관동의에 체크했는지 확인
def joinAgree(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 접근입니다."})
  else:
    agree1 = request.POST.get("agree1")
    agree2 = request.POST.get("agree2","")

    if agree1 == 1:
      request.session['agree1'] = agree1

      Member.objects.create(
        agree1 = "필수약관 동의완료"
      )

    if agree2 == 1:
      request.session['agree2'] = agree2

      Member.objects.create(
        agree2 = "선택약관 동의완료"
      )

    today = datetime.now().strftime("%Y-%m-%d")
    context = {"result": "success", "today":today, "message": "회원약관에 동의하셨습니다"}

    return JsonResponse(context)
    

### 약관동의
def join01(request):
  return render(request, "join01.html")

### ---------------------- 아이디/닉네임/이메일 중복 확인 ----------------------
## 이메일 중복 확인
def emailDupChk(request):
  userEmail = request.POST.get("email")
  if Member.objects.filter(email=userEmail):
    return JsonResponse({"result": "error", "message": "이미 사용 중인 이메일입니다."})
  return JsonResponse({"result": "success", "message": "사용 가능한 이메일입니다."})

## 전화번호 중복 확인
def telDupChk(request):
  userTel = request.POST.get("tel")
  if Member.objects.filter(tel=userTel):
    return JsonResponse({"result": "error", "message": "이미 사용 중인 전화번호입니다."})
  return JsonResponse({"result": "success", "message": "사용 가능한 전화번호입니다."})

## 닉네임 중복 확인
def nicknameDupChk(request):
  userNickname = request.POST.get("nickname")
  if Member.objects.filter(nickname=userNickname):
    return JsonResponse({"result": "error", "message": "이미 사용 중인 닉네임입니다."})
  return JsonResponse({"result": "success", "message": "사용 가능한 닉네임입니다."})

## 아이디 중복 확인
def idDupChk(request):
  userId = request.POST.get("id")
  if Member.objects.filter(id=userId):
    
    return JsonResponse({"result": "error", "message": "이미 사용 중인 아이디입니다."})
  return JsonResponse({"result": "success", "message": "사용 가능한 아이디입니다."})


### 회원정보 저장
def newMember(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    id = request.POST.get("id")
    pw = request.POST.get("pw")
    name = request.POST.get("name")
    nickname = request.POST.get("nickname")
    tel = request.POST.get("tel")
    email = request.POST.get("email")
    addr = request.POST.get("addr")

    hashed_pw = make_password(pw) # 비밀번호 암호화

    Member.objects.create(
      id = id,
      pw = hashed_pw,
      name = name,
      nickname = nickname,
      tel = tel,
      email = email,
      addr = addr,
      mDate = "now" # 가입일
    )

    return JsonResponse({"result": "success", "message": "회원가입이 완료되었습니다."})


### 회원가입 - signup
def signup(request):
  return render(request, "signup.html")
  
### ---------------------------- 새 비밀번호 설정 ----------------------------
def newPasswordCheck(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    verification_code = request.session.get("verification_code")
    verification_email = request.session.get("verification_email")
    
    if not verification_code:
      return JsonResponse({"result": "error", "message": "세션이 만료되었습니다. 다시 시도해주세요."})
    # if not verification_email:
    #   return JsonResponse({"result": "error", "message": "세션이 만료되었습니다. 다시 시도해주세요."})

    newPw = request.POST.get("newPw", "")
    newPwChk = request.POST.get("newPwChk", "")

    if newPw != newPwChk:
      return JsonResponse({"result": "error", "message": "비밀번호 확인란을 정확히 입력하세요."})

    try:
      # 이메일로 사용자 찾기
      user = Member.objects.get(email=verification_email)
      
      # 입력된 새 비밀번호와 저장된 암호화된 기존 비밀번호 비교
      if check_password(newPw, user.pw):
        return JsonResponse({"result": "error", "message": "기존 비밀번호와 동일합니다. 다른 비밀번호를 사용해 주세요."})

      # 비밀번호 업데이트
      user.pw = make_password(newPw) # 비밀번호 암호화
      user.save()

      # 세션 정리(인증 관련 정보 삭제)
      del request.session['verification_email']
      del request.session['verification_code']

      print(f"새 비밀번호 : {newPw}")

      return JsonResponse({"result": "success", "message": "비밀번호가 성공적으로 변경되었습니다."})
    
    except Member.DoesNotExist:
      return JsonResponse({"result": "error", "message": "사용자를 찾을 수 없습니다."})
    except Exception as e:
      return JsonResponse({"result": "error", "message": f"오류 발생: {str(e)}"})


def newPassword(request):
  return render(request, "newPassword.html")
### ---------------------------- 아이디/비밀번호 찾기 ----------------------------
# ---------------------------- 비밀번호 찾기 ----------------------------
# 인증번호 확인 버튼
def verify_code(request):
  if request.method == 'GET':
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    input_code = request.POST.get('chkEmailCode')  # 유저가 입력한 인증번호
    saved_code = request.session.get('verification_code')  # 세션에서 인증번호 가져오기

    if not input_code:
      return JsonResponse({"result": "error", "message": "인증번호를 입력하세요."})
    if not saved_code:
      return JsonResponse({"result": "error", "message": "인증번호를 먼저 요청하세요."})

    # 인증번호 일치 여부 확인
    if input_code == saved_code:
      return JsonResponse({"result": "success", "message": "인증되었습니다."})
    else:
      return JsonResponse({"result": "error", "message": "인증번호가 일치하지 않습니다."})


### 인증번호 보내기
def send_verification_code(request):
  if request.method == "GET":
    return JsonResponse({"result": "error", "message": "잘못된 요청입니다."})
  else:
    name = request.POST.get("name")
    email = request.POST.get('email')

    try:
      # 이름과 이메일이 존재하는지 확인
      member = Member.objects.get(name=name, email=email)
    except Member.DoesNotExist:
      return JsonResponse({"result": "error", "message": "존재하지 않는 회원입니다."})

    # 랜덤 6자리 인증번호 생성
    verification_code = str(random.randint(100000, 999999))

    # 세션에 이메일, 인증번호와 회원 ID 저장
    request.session['verification_email'] = email
    request.session['verification_code'] = verification_code
    request.session['member_id'] = member.id

    # # db에 이메일, 인증번호 저장
    # Member.objects.create(
    #   verification_email = email,
    #   verification_code = verification_code,
    #   created_at = "now" # 가입일
    # )

    # 이메일로 인증번호 전송
    try:
      smtpName = "smtp.naver.com"
      smtpPort = 587
      sendEmail = "bd8860@naver.com"
      pw = "YTZTLRBETCV2"
      recvEmail = email
      title = "비밀번호 찾기용 인증번호"
      content = f"인증번호는 {verification_code} 입니다."

      msg = MIMEText(content)
      msg['Subject'] = title
      msg['From'] = sendEmail
      msg['To'] = recvEmail

      s = smtplib.SMTP(smtpName, smtpPort)
      s.starttls()
      s.login(sendEmail, pw)
      s.sendmail(sendEmail, recvEmail, msg.as_string())
      s.quit()

      return JsonResponse({"result": "success", "message": "인증번호가 이메일로 전송되었습니다."})
    except Exception as e:
      return JsonResponse({"result": "error", "message": f"메일 전송 실패: {str(e)}"})
  
   
### 비밀번호 찾기 버튼 - 이름, 이메일, 인증번호 맞는지 확인
def findPassword(request):
  if not request.session.get("verification_code", None):
    return JsonResponse({"success": "error", "message": "인증번호를 확인해주세요."})
  
  if request.method == "POST":
      ## 사용자가 입력한 정보
      name = request.POST.get("name", "")
      email = request.POST.get("email", "")

      chkEmailCode = request.POST.get("chkEmailCode", "")

      print(f"이름 : {name}\n이메일 주소 : {email}\n인증번호 : {chkEmailCode}")

      if not name or not email:
        return JsonResponse({"result": "error", "message": "이름과 이메일을 모두 입력하세요."})

      # 사용자 조회
      try:
        qs = Member.objects.filter(name=name, email=email)
        if qs.exists():
          user = qs.first()  # 첫 번째 일치하는 사용자
          
          # 인증번호 확인
          if chkEmailCode != request.session.get("verification_code"):
            return JsonResponse({"result": "error", "message": "인증번호가 일치하지 않습니다."})
          
          return JsonResponse({
            "result": "success", "name": user.name, "user_pw": user.pw
          })
        else:
          return JsonResponse({"result": "error", "message": "존재하지 않는 회원입니다."})
      except Exception as e:
        return JsonResponse({"result": "error", "message": f"서버 오류: {str(e)}"})


# ---------------------------- 아이디 찾기 ----------------------------
def findId(request):
  try:
    name = request.POST.get("name", "")
    email = request.POST.get("email", "")

    print(f"이름 : {name}\n이메일 주소 : {email}")

    qs = Member.objects.filter(name=name, email=email)
    if qs.exists():
      user = qs.first()  # 첫 번째 일치하는 사용자
      return JsonResponse({
        "result": "success", "name": user.name, "user_id": user.id
      })
    else:
      return JsonResponse({"result": "fail", "message": "존재하지 않는 회원입니다."})
  except Exception as e:
    print(f"오류 발생 : {e}")
    return JsonResponse({"result": "error", "message": "서버 오류 발생"})

### 아이디/비밀번호 찾기 페이지
def findInfo(request):
    return render(request, "findInfo.html")
### // --------------------------- 아이디/비밀번호 찾기 ----------------------------

### 로그아웃
def logout(request):
  request.session.clear()
  return redirect("/")

# 아이디/비밀번호 일치 확인
def loginChk(request):
  id = request.POST.get("id", "")
  pw = request.POST.get("pw", "")

  # db에서 해당 아이디 검색
  try:
    user = Member.objects.get(id=id)
    
    # 입력된 비밀번호와 저장된 암호화된 비밀번호 비교
    if check_password(pw, user.pw):
      # 로그인 성공, 세션에 사용자 정보 저장
      request.session['session_id'] = user.id
      request.session['session_nickname'] = user.nickname
      list_qs = list(Member.objects.filter(id=id).values())  # 사용자 정보 가져오기
      context = {"result": "success", "member": list_qs}  # member 정보를 JSON으로 반환
    else:
      context = {"result": "fail", "message": "비밀번호가 틀렸습니다."}
  except Member.DoesNotExist:
    context = {"result": "fail", "message": "아이디가 존재하지 않습니다."}

  return JsonResponse(context)


### 로그인페이지
def login(request):
  return render(request, "login.html")
