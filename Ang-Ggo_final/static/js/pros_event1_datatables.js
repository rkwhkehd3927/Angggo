let csrfToken = $('meta[name="csrf-token"]').attr('content');
let recordsTotal = $('#recordsTotal').val();
var flag = 0;
$(document).ready(function () {
    var originalData = []; // 수정 취소시 원본 데이터 저장
    var table = $('#layoutTable').dataTable({
        width: '100%',
        responsive: true, // 반응형 설정
        autoWidth: true, // 자동 너비 조정 활성화
        processing: false, // 처리 중 표시 활성화
        serverSide: false, // 서버 사이드 처리 활성화
        searching: true, // 검색란 표시 설정
        search: '<input type="text" id="dt-search-0" class="form-control form-control-sm" aria-controls="layoutTable">', // 검색창 추가
        ordering: true, // 컬럼별 정렬기능
        paging: true, // 페이징 표시 설정
        pageLength: 10, // 기본 데이터건수
        lengthChange: false, // 데이터건수 변경
        order: [1, 'desc'], // 기본 정렬칼럼
        scrollX: true, // 가로 스크롤
        dom: "<'row'<'col-sm-12 col-md-6'B><'col-sm-12 col-md-6'f>>" +
            "<'row'<'col-sm-12'tr>>" +
            "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>", // DOM 배열(구조) 순서 B(버튼)f(검색)r(처리중)t(테이블 본문)i(정보요약)p(페이징)
        language: { // 언어 설정(한국어)
            "emptyTable": "데이터가 없습니다.",
            "lengthMenu": "페이지당 _MENU_ 개씩 보기",
            "info": "현재 _START_ - _END_ / _TOTAL_건",
            "infoEmpty": "데이터 없음",
            "infoFiltered": "( _MAX_건의 데이터에서 필터링됨 )",
            "search": "검색 : ",
            "zeroRecords": "일치하는 데이터가 없습니다.",
            "loadingRecords": "로딩중...",
            "processing": "잠시만 기다려 주세요...",
            "paginate": {
                "next": "다음",
                "previous": "이전"
            },
            "select": {
                "rows": ""
            }
        }, // language
        buttons: ['copy', 'excel', 'pdf', 'print',
            {
                text: '데이터 추가', className: 'addDataBtn', action: function () {
                    alert('추가 버튼이 클릭되었습니다!');
                    var tr = $('<tr>').prependTo($('#layoutTable tbody'));
                    // 이미 input이 추가된 상태에서 추가 버튼을 클릭하면 새로운 input을 추가하지 않
                    if (flag == 1) {
                        alert('데이터 추가가 진행중입니다.')
                        return false;
                    }
                    
                    // 없으면 tr의 td에 input 추가(1,6,7번째 column은 제외)
                    else {


                        for (var i = 0; i < 7; i++) {
                            var td = $('<td>').appendTo(tr);
                            var cellValue = "";
                            var input = $('<input type="text" value="' + cellValue + '" class="mx-auto pl-1 form-control " />');
                            input.attr('style', $('#layoutTable thead tr th').eq(i).attr('style')); // th의 css 스타일 복사
                            input.appendTo(td);
                            // 0번째 column은 readonly
                            if (i == 0) {
                                input.attr('readonly', true);
                            }
                            // 0번째 column은 qs.count+1
                            if (i == 0) {
                                input.val(Number(recordsTotal)+1)
                            }
                            // 5번째 column은 0
                            if (i == 5) {
                                input.val(0);
                            }
                            // 6번째 column은 추가, 취소 버튼 추가
                            if (i == 6) {
                                var lastCell = tr.find('td').eq(6);
                                lastCell.html('<button class="btn btn-success tx-12 mx-2 addDataBtn" value="0" data-target="" data-toggle="">추가</button>');
                                lastCell.append('<button class="btn btn-danger tx-12 mx-2 canBtn2" value="0" data-target="" data-toggle="">취소</button>');
                            }
                        }
                    }
                    flag = 1;
                }
            }], // 버튼 추가
        ajax: {
            url: "/pros/getEventList/",
            headers: { "X-CSRFToken": csrfToken },
            type: "POST",
            data: data => JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            dataSrc: 'data'
        },
        columns: [
            { data: "aNo" },
            { data: "ID" },
            { data: "Count" },
            { data: "aTicket" },
            { data: "UsedTicket" },
            { data: "Point" },
            {
                title: "수정/삭제", data: "SEQ", // 수정,삭제 버튼 column
                render: function (data) {
                    return '<button class="btn btn-primary tx-12 mx-2 modiBtn" value="0" data-target="" data-toggle="">수정</button>'
                        + '<button class="btn btn-danger tx-12 mx-2 DelBtn" value="0" data-target="" data-toggle="">삭제</button>';
                }
            }
        ],
        columnDefs: [
            { width: 'auto', height: 'auto', targets: '_all' },// 모든 column의 너비를 동일하게 유지
        ],
    });
    

    // row 선택
    $('#layoutTable').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            $(this).addClass('selected');
        }
    });
    
    //table의 수정 버튼 클릭
    $('#layoutTable').on('click', '.modiBtn', function () {
        
        var row = $(this).closest('tr')
        var row_data = $(this).closest('tr').find('td').map(function () {
            return $(this).text();
        }).get();
        
        originalData = row_data // 수정 취소시 원본 데이터 저장 


        // alert(row_data[0]);
        
        // td의 style(css)를 변경하지 않고 td의 내용을 input으로 변경(mx-2)
        for (var i = 0; i < 6; i++) { // 0,1,6,7번째는 제외
            if (i == 0 || i == 1) {
                continue;
            }
            var cell = row.find('td').eq(i);
            var cellValue = row_data[i];
            cell.html('<input type="text" value="' + cellValue + '" class="mx-auto pl-1 form-control " />');
        }

        // td 6번째(제일 마지막)의 '수정' 버튼을 '저장' 버튼으로 변경, '삭제' 버튼을 '취소' 버튼으로 변경
        var lastCell = row.find('td').eq(6);
        lastCell.html('<button class="btn btn-success tx-12 mx-2 svBtn" value="0" data-target="" data-toggle="" onclick="">저장</button>');
        lastCell.append('<button class="btn btn-danger tx-12 mx-2 canBtn" value="0" data-target="" data-toggle="" onclick="">취소</button>');
    });




    // table의 저장 버튼 클릭
    $('#layoutTable').on('click', '.svBtn', function () {
        // table row 의 데이터 가져오기
        var row = $(this).closest('tr');
        var input_data = row.find('td input').map(function () { return $(this).val(); }).get();

        // table 2,3,4,5번째 row의 데이터가 비어있으면 alert 
        for (i = 0; i < 4; i++) {
            if (input_data[i] == "") {
                alert("빈칸을 채워주세요");
                row.find('td').eq(i).find('input').focus();
                return false;
            }
            else if (!/^[0-9]*$/.test(input_data[i])) {
                alert("숫자만 입력해주세요");
                row.find('td').eq(i).find('input').focus();
                return false;
            }
        }
                // DB에서 수정
                $.ajax({
                    headers: { "X-CSRFToken": csrfToken },
                    url: "/pros/updateEventList/",
                    type: "POST",
                    data: {
                        'aNo': row.find('td').eq(0).text(),
                        'Count': input_data[0],
                        'aTicket': input_data[1],
                        'usedTicket': input_data[2],
                        'Point': input_data[3],
                    },
                    success: function (data) {
                        if (data.result == 'vacant') {
                            alert("빈 칸을 채워주세요.")
                            return false;
                        }
                        else if (data.result == 'fail') {
                            alert("수정에 실패하였습니다.");
                            return false;
                        }
                        else if (data.result == 'success') {
                            alert("수정되었습니다.");
                            location.href = "/pros/event1";
                        }
                    }
                });
           });
         
    // table의 취소 버튼 클릭
    $('#layoutTable').on('click', '.canBtn', function () {
        // input 값을 삭제하고 td값에 원래 데이터 추가
        var row = $(this).closest('tr');
        for (var i = 2; i < 6; i++) {
            var cell = row.find('td').eq(i);
            cell.html(originalData[i]);
        }

        // td 6번째(제일 마지막)의 '저장' 버튼을 '수정' 버튼으로 변경, '취소' 버튼을 '삭제' 버튼으로 변경
        var lastCell = row.find('td').eq(6);
        lastCell.html('<button class="btn btn-primary tx-12 mx-2 modiBtn" value="0" data-target="" data-toggle="" onclick="">수정</button>');
        lastCell.append('<button class="btn btn-danger tx-12 mx-2 DelBtn" value="0" data-target="" data-toggle="" onclick="">삭제</button>');
    });

    // table의 추가 버튼 클릭 후 취소 버튼 클릭
    $('#layoutTable').on('click', '.canBtn2', function () {
        $(this).closest('tr').remove();
        flag = 0;
    });

    // table의 추가 버튼 클릭
    
    $('#layoutTable').on('click', '.addDataBtn', function () {
            // table row 의 데이터 가져오기
            var row = $(this).closest('tr');
            var input_data = row.find('td input').map(function () { return $(this).val(); }).get();
        console.log(input_data);
            // table row의 데이터가 비어있으면 alert 
            for (var i = 0; i < 5; i++) {
                alert(input_data[i]);
                if (input_data[i] == "") {
                    alert("빈칸을 채워주세요");
                    row.find('td').eq(i).find('input').focus();
                    return false;
                }
            }
            // 1번째 열(id)는 영어+숫자만 가능
            if (!/^[a-zA-Z0-9]*$/.test(input_data[1])) {
                alert("영어/숫자만 입력해주세요.");
                row.find('td').eq(0).find('input').focus();
                return false;
            }
            //2~5번째 열을 숫자만 가능
            for (i = 2; i < 6; i++) { 
                if (!/^[0-9]*$/.test(input_data[i])) {
                    alert("숫자만 입력해주세요");
                    row.find('td').eq(i).find('input').focus();
                    return false;
                }
            }    
            // DB에서 추가
            $.ajax({
                headers: { "X-CSRFToken": csrfToken },
                url: "/pros/addEventList/",
                type: "POST",
                data: {
                    'ID': input_data[1],
                    'Count': input_data[2],
                    'aTicket': input_data[3],
                    'usedTicket': input_data[4],
                    'Point': input_data[5],
                },
                success: function (data) {
                    if (data.result == 'vacant') {
                        alert("빈 칸을 채워주세요.")
                        return false;
                    }
                    else if (data.result == 'fail') {
                        alert("추가에 실패하였습니다.");
                        return false;
                    }
                    else if (data.result == 'success') {
                        alert("추가되었습니다.");
                        location.href = "/pros/event1";
                    }
                }
            });
    });
    
    // // table의 검색 창에 data 입력 후 enter key 입력
    // $('#dt-search-0').keypress(function (e) {
        //     if (e.keyCode == 13) {
            //         if ($('#dt-search-0').val() == "") {
                //             alert("검색어를 입력해주세요.");
                //             return false;
                //         }
                //         else if (!/^[a-zA-Z0-9]*$/.test($('#dt-search-0').val())) {
                    //             alert("영어/숫자만 입력해주세요.");
                    //             return false;
                    //         }
                    //         else {
        //             alert('검색중입니다.');
        //             var keyword = $('#dt-search-0').val();
        //             var length = $('#layoutTable tbody tr').length;
        
        //             // 모든 행의 배경색 초기화
        //             $('#layoutTable tbody tr').css('background-color', '');
        
        //             setTimeout(function () {
            //                 for (i = 0; i < length; i++) {
                //                     var search_data = $('#layoutTable tbody tr').eq(i).find('td').eq(1).text();
                //                     // keyword가 search_data에 포함되어 있으면 배경색을 노란색으로 변경
                //                     if (search_data.includes(keyword)) {
                    //                         $('#layoutTable tbody tr').eq(i).css('background-color', 'yellow');
                    //                     }
                    //                 }
                    //                 alert('검색이 완료되었습니다.');
                    //             }, 100); // 100밀리초 지연
                    //         }
                    //     }
        // });
        
        // table의 삭제 버튼 클릭
        $('#layoutTable').on('click', '.DelBtn', function () {
            
            var row_data = $(this).closest('tr').find('td').map(function () {
                return $(this).text();
            }).get();
            if (confirm(row_data[0] + " 데이터를 삭제하시겠습니까?")) {
                $.ajax({
                    headers: { "X-CSRFToken": csrfToken },
                    url: "/pros/delEventList/",
                    type: "POST",
                    data: {
                        'ID': row_data[0]
                    },
                    success: function (data) {
                        if (data.result == 'fail') {
                            alert("삭제에 실패하였습니다.");
                            return false;
                        }
                        else if (data.result == 'success') {
                            alert("삭제되었습니다.");
                            location.href = "/pros/event1/";
                        }
                    }
                });
            };
        });
    });