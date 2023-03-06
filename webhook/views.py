from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json,datetime
from function import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
     TextSendMessage,TemplateSendMessage, ButtonsTemplate, URIAction
)
import xlsxwriter


def template():
    # Create a URIAction for the file
    uri_action = URIAction(
        label='Open File',
        uri='https://b8f5-184-82-234-66.ap.ngrok.io/media/export_data.xlsx'
    )

    # Create a ButtonsTemplate with the URIAction
    template = ButtonsTemplate(
        thumbnail_image_url='https://secure.zortout.com/Home/DisplayProductImage?pid=13636476',
        title='File Template',
        text='Click the button to open the file',
        actions=[uri_action]
    )

    # Create a TemplateSendMessage with the ButtonsTemplate
    template_message = TemplateSendMessage(
        alt_text='File template',
        template=template
    )
    return template_message

def export():
    task = 'select DATE_ADD(date, INTERVAL 7 HOUR),id,image,name from muslin.qc_data'
    result = db.query(task)
    result = list(result.fetchall())
    for i in result:
        with open(f"{settings.MEDIA_ROOT}/{i[1]}.jpg",'wb') as f:
            f.write(i[2])

    workbook = xlsxwriter.Workbook(f'{settings.MEDIA_ROOT}/export_data.xlsx')
    # Create an new Excel file and add a worksheet.
    worksheet = workbook.add_worksheet()
    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 30)
    for i in range(len(result)):
        row_index = i + 1
        
        row = (row_index - 1) * 20
        if i == 0:
            row = row_index

        # Insert an image.
        worksheet.write(f'A{row}', str(result[i][0]))
        worksheet.write(f'B{row}', result[i][3])
        worksheet.insert_image(f'C{row}', f'{settings.MEDIA_ROOT}/{result[i][1]}.jpg', {'x_scale': 0.2, 'y_scale': 0.2})

    workbook.close()

    for i in result:
        os.remove(f"{settings.MEDIA_ROOT}/{i[1]}.jpg")

channel_secret = 'ec27c5632b4fd85f0d88650fa19e29d1'
channel_access_token = 'jZYUZseFejcfL1U9K3CFEKqfLBCD/qc9g9BF1ljrZUArRTzU22t1OfIDCAzABSnHIZA4fIPOWUXkznfzzp8dhQfFW1EH5JdueEsL+c3LT0Ce9pAwUmAhNGBXit72zjBH7et2y6+4iAQBqy8h1LTDvQdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
class QC:
    def __init__(self) -> None:
        self.image = ''
        self.name = ''
        self.check = False

qc = QC()

@csrf_exempt
def callback(request):
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    # handle webhook body
    try:
        handler.handle(body, signature)
    except:
        print('error')
    return render(request,'webhook.html')
    
@csrf_exempt
def editorder(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['status'] == 'Voided':
                task =f"""update {dep}.deli_zort
                    set status = '{str(res['status'])}',customername='{str(res['customername'])}',trackingno='{str(res['trackingno'])}',shippingtime='{datetime.datetime.now()}',
                    paymentstatus='{str(res['paymentstatus'])}'
                    where idorder = {res['id']}"""
                
                db.query_commit(task)
                db.query_commit(f"delete from {dep}.order_main where IDorder = '{res['id']}'")
                for i in res['list']:
                    db.query_commit(f"insert into {dep}.order_main\
                        values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')")
            else:
                db.query_commit(f"delete from {dep}.deli_zort\
                    where idorder = {res['id']}")
        except Exception as e:
            print(e)
    return render(req,'webhook.html')

@csrf_exempt
def addorder(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['trackingno']:
                res['trackingno'] = ''
            task = f"insert into {dep}.deli_zort\
                values ('{res['id']}','{res['number']}','{res['status']}','{res['customername']}','{datetime.datetime.now()}','{str(res['trackingno'])}',0,NULL,NULL,\
                 '{str(res['paymentstatus'])}','{str(res['shippingaddress'])}','{str(res['shippingphone'])}')"
            
            db.query_commit(task)
            for i in res['list']:
                task = f"insert into {dep}.order_main\
                    values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')"
                db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def updatetracking(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            task = f"""update {dep}.deli_zort\
                set trackingno='{str(res['trackingno'])}'
                where idorder = {res['id']}"""
            
            db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def editproduct(req):
    def get_amount(sku,amount):
        result = db.query(f"select amount from muslin.stock where sku = '{sku}'")
        result = list(result.fetchall())[0][0]
        result = int(result)
        new_amount = 3 - amount
        if result - new_amount >= 0:
            return 3,result - new_amount
        else:
            return amount + result,0

    dep = "muslin"
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    try:
        sku = req.POST.get("datas")
        res = json.loads(sku)
    except:
        return render(req,'webhook.html')
    if req.method == 'POST':
        try:
            if int(res['available']) < 3:
                send_line('start')
                zort_amount,stock_amount = get_amount(res['sku'],res['available'])
                send_line(f"zort will have {zort_amount} stock amount will have {stock_amount}")
                db.query_commit(f"update {dep}.stock set amount = {stock_amount} where sku = '{res['sku']}'")
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",res['sku'],zort_amount)
        except Exception as e:
            print(e)
        db.query_commit(f'update {dep}.stock_main set descript = "{res["name"]}" where sku = "{res["sku"]}"')
    return render(req,'webhook.html')


@csrf_exempt
def editorder_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['status'] == 'Voided':
                task =f"""update maruay.deli_zort\
                    set status = '{str(res['status'])}',customername='{str(res['customername'])}',trackingno='{str(res['trackingno'])}',shippingtime='{datetime.datetime.now()}',paymentstatus=>
                    where idorder = {res['id']}"""
                
                db.query_commit(task)
                db.query_commit(f"delete from maruay.order_main where IDorder = '{res['id']}'")
                for i in res['list']:
                    db.query_commit(f"insert into maruay.order_main\
                        values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')")
            else:
                db.query_commit(f"delete from maruay.deli_zort\
                    where idorder = {res['id']}")
        except Exception as e:
            print(e)
    return render(req,'webhook.html')

@csrf_exempt
def addorder_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['trackingno']:
                res['trackingno'] = ''
            task = f"insert into maruay.deli_zort\
                values ('{res['id']}','{res['number']}','{res['status']}','{res['customername']}','{datetime.datetime.now()}','{str(res['trackingno'])}',0,NULL,NULL,\
                 '{str(res['paymentstatus'])}','{str(res['shippingaddress'])}','{str(res['shippingphone'])}')"
            
            db.query_commit(task)
            for i in res['list']:
                task = f"insert into maruay.order_main\
                    values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')"
                db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def updatetracking_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            task = f"""update maruay.deli_zort\
                set trackingno='{str(res['trackingno'])}'
                where idorder = {res['id']}"""
            db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def editproduct_maruay(req):
    dep = 'maruay'
    def get_amount(sku,amount):
        result = db.query(f"select amount from {dep}.stock where sku = '{sku}'")
        result = list(result.fetchall())[0][0]
        result = int(result)
        new_amount = 3 - amount
        if result - new_amount >= 0:
            return 3,result - new_amount
        else:
            return amount + result,0

    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    try:
        sku = req.POST.get("datas")
        res = json.loads(sku)
    except:
        return render(req,'webhook.html')
    if req.method == 'POST':
        try:
            if int(res['available']) < 3:
                send_line('start')
                zort_amount,stock_amount = get_amount(res['sku'],res['available'])
                send_line(f"zort will have {zort_amount} stock amount will have {stock_amount}")
                db.query_commit(f"update {dep}.stock set amount = {stock_amount} where sku = '{res['sku']}'")
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",res['sku'],zort_amount)
        except Exception as e:
            print(e)
        db.query_commit(f'update {dep}.stock_main set descript = "{res["name"]}" where sku = "{res["sku"]}"')
    return render(req,'webhook.html')

# @handler.add(MessageEvent, message=TextMessage)    
@handler.default()
def message_text(event):
    print(event)
    if event.message.type == 'text':

        text = event.message.text
        print(text)
        if text == 'clear':
            qc.check = False
            qc.image = ''
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"clear Success !!")
            )
            qc.check = False
        elif text == 'export excel':
            export()
            template_message = template()
            # Send the message
            line_bot_api.reply_message(
                event.reply_token, 
                template_message)

        else:
            if qc.check:
                task = """ INSERT INTO muslin.qc_data(id, name, image,date)\
                            VALUES (%s,%s,%s,now())"""
                db.query_with_image(task, (0, text, qc.image))
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Record Success !!")
                )
                qc.check = False
            elif not(qc.check):
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Please send an image first")
                )

    elif event.message.type == 'image':
        qc.check = True
        image_content = line_bot_api.get_message_content(event.message.id).content
        qc.image = image_content
        print(type(qc.image))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Enter detail for this image : ')
        )
    
    else:
        qc.check = False
        pass