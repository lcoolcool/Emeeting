//插件中自带，直接复制粘贴：
    // 对Date的扩展，将 Date 转化为指定格式的String
    // 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
    // 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
    // 例子：
    // (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
    // (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
    Date.prototype.Format = function (fmt) { //author: zhaishuaishuai
        var o = {
            "M+": this.getMonth() + 1, //月份
            "d+": this.getDate(), //日
            "h+": this.getHours(), //小时
            "m+": this.getMinutes(), //分
            "s+": this.getSeconds(), //秒
            "q+": Math.floor((this.getMonth() + 3) / 3), //季度
            "S": this.getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    };

//自定义的全局变量：
    SELECTED_ROOM = {del: {}, add: {}};
    CHOSEN_DATE = new Date().Format('yyyy-MM-dd');//转成字符串格式后的今日日期
//网页加载完成后执行的js脚本内容：
    $(function () {
        initDatepicker();//初始化日期插件
//初始化房间信息，将今日日期发给后端,利用ajax从后台获得房间预订信息
        initBookingInfo(new Date().Format('yyyy-MM-dd'));
        bindTdEvent();//绑定预定会议室事件
        bindSaveEvent();//保存按钮
    });
//处理csrftoken:
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            }
        }
    });
//初始化日期插件内容：
    function initDatepicker() {
        $('#datetimepicker11').datetimepicker({
            minView: "month",//最小可视是到月份，即最小选择是到day
            language: "zh-CN",
            sideBySide: true,
            format: 'yyyy-mm-dd',
            bootcssVer: 3,//bootstrap3必写
            startDate: new Date(),//起始日为今日
            autoclose: true,//自动关闭，不需要可删
        }).on('changeDate', changeDate);//绑定改日期后的事件
    }
//绑定的改日期后的事件:
    function changeDate(ev) {
        CHOSEN_DATE = ev.date.Format('yyyy-MM-dd');//日期变为选择后的日期
        initBookingInfo(CHOSEN_DATE);//初始化预定信息

    }
//初始化房间信息（利用ajax从后台获得房间预订信息）
    function initBookingInfo(date) {
        SELECTED_ROOM = {del: {}, add: {}};

        $('#shade,#loading').removeClass('hide');//遮罩层
        $.ajax({
            url: '/booking/',
            type: 'get',
            data: {date: date},//字符串转义后的今日日期
            dataType: 'JSON',
            success: function (arg) {
                $('#shade,#loading').addClass('hide');//遮罩层去除
                if (arg.code === 1000) {//表示后台操作成功
                    $('#tBody').empty();
                    $.each(arg.data, function (i, item) {
                        var tr = document.createElement('tr');//此为js操作，等同于jQuery的$('<tr>')
                        $.each(item, function (j, row) {
                            var td = $('<td>');
                            $(td).text(row.text).attr('class','everytd');

                            $.each(row.attrs, function (k, v) {
                                $(td).attr(k, v);
                            });
                            if (row.chosen) {
                                $(td).addClass('chosen');
                            }
                            $(tr).append(td)
                        });
                        $('#tBody').append(tr);
                    })
                } else {
                    alert(arg.msg);
                }
            },
            error: function () {
                $('#shade,#loading').addClass('hide');
                alert('请求异常');
            }
        })
    }

    /*
     绑定预定会议室事件，事件委派
     */
    function bindTdEvent() {
        $('#tBody').on('click', 'td[time-id][disable!="true"]', function () {

            var roomId = $(this).attr('room-id');
            var timeId = $(this).attr('time-id');

            //var item = {'roomId': $(this).attr('room-id'), 'timeId': $(this).attr('time-id')};
            // 取消原来的预定：
            if ($(this).hasClass('chosen')) {
                $(this).removeClass('chosen').empty();

                //SELECTED_ROOM['del'].push(item);
                if (SELECTED_ROOM.del[roomId]) {
                    SELECTED_ROOM.del[roomId].push(timeId);
                } else {
                    SELECTED_ROOM.del[roomId] = [timeId];
                }

            } else if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
                // 取消选择
                var timeIndex = SELECTED_ROOM.add[roomId].indexOf(timeId);
                if (timeIndex !== -1) {
                    SELECTED_ROOM.add[roomId].splice(timeIndex, 1);
                }
            } else {
                $(this).addClass('selected');
                // 选择
                if (SELECTED_ROOM.add[roomId]) {
                    SELECTED_ROOM.add[roomId].push(timeId);
                } else {
                    SELECTED_ROOM.add[roomId] = [timeId];
                }
            }
        })
    }

    /*
     保存按钮
     */
    function bindSaveEvent() {
        $('#errors').text('');

        $('#save').click(function () {
            $('#shade,#loading').removeClass('hide');
            $.ajax({
                url: '/booking/',
                type: 'POST',
                data: {date: CHOSEN_DATE, data: JSON.stringify(SELECTED_ROOM)},
                dataType: 'JSON',
                success: function (arg) {
                    $('#shade,#loading').addClass('hide');
                    if (arg.code === 1000) {
                        initBookingInfo(CHOSEN_DATE);

                    } else {
                        $('#errors').text(arg.msg);
                    }
                    swal(
                      '保存成功',
                      '会议室预定状态已刷新',
                      'success'
                    )
                }
            });
        });

    }


//鼠标悬浮变色功能（美化）
    $(document).ready(function(){
        $('body').on('mouseover','.everytd',function () {
            $(this).addClass('mycolor')
        })
        $('body').on('mouseout','.everytd',function () {
            $(this).removeClass('mycolor')
        })
    });