#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖✨ NOVA.X - RAQAMLI YECHIMLAR BOTI ✨🤖
🎯 To'liq Admin Panel + CRM tizimi
"""

import logging
import json
import os
import re
import csv
import asyncio
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== WEB SERVER (RENDER KEEP-ALIVE) ====================
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "NOVA.X Bot is alive!", 200

@web_app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    # Render avtomatik PORT beradi, agar bo'lmasa 8080 ishlatiladi
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Web server {port}-portda ishga tushmoqda...")
    try:
        web_app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Web serverda xato: {e}")

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()
    logger.info("Keep-alive tizimi yoqildi.")

# ==================== KONFIGURATSIYA ====================
# Render Environment Variables-dan o'qiydi, agar bo'lmasa pastdagini ishlatadi
BOT_TOKEN = os.environ.get('BOT_TOKEN', "7847069401:AAGGgVQlS5WHgfsxF5yrAfxGFxTCn6DabCU")
ADMIN_PHONE = os.environ.get('ADMIN_PHONE', "+998997236222")
ADMIN_TELEGRAM = os.environ.get('ADMIN_TELEGRAM', "@nnoovvaaxx")

# ADMIN_IDS ni vergul bilan ajratilgan string shaklida olib, listga aylantiramiz
admin_ids_raw = os.environ.get('ADMIN_IDS', "6616832324")
ADMIN_IDS = [int(i.strip()) for i in admin_ids_raw.split(',') if i.strip().isdigit()]

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('nova_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("=" * 70)

# ==================== TRANSLATIONS ====================
TRANSLATIONS = {
    'uz_lat': {
        'select_lang': "🌍 Iltimos, tilni tanlang:\n🇷🇺 Пожалуйста, выберите язык:\n🇺🇸 Please select a language:",
        'welcome': "🌟✨ **ASSALOMU ALAYKUM, AZIZ {name} {username}!** 👋✨\n\n🎉 **NOVA.X — Raqamli imkoniyatlar olamiga xush kelibsiz!**\nSizni bu yerda ko‘rib turganimizdan behad mamnunmiz! 🤩 Bugun o‘zgarishlar va yangi g‘alabalar uchun ajoyib kun.\n\n🚀 **Siz ayni vaqtida, to‘g‘ri joydasiz!**\nBiz shunchaki xizmat ko‘rsatmaymiz, biz sizning orzularingizni raqamli voqelikka aylantiramiz. Sizning biznesingiz eng yuqori cho‘qqilarni zabt etishga loyiq va biz bunga yordam berishga tayyormiz! 💪\n\n� **Biz bilan nimalarga ega bo'lasiz?**\n• � _Betakror Dizayn_ — Mijozlaringiz bir ko'rishda sevib qoladi.\n• ⚡️ _Kuchli Texnologiyalar_ — Biznesingiz soat kabi aniq ishlaydi.\n• 🤝 _Ishonchli Hamkorlik_ — Biz doim yoningizdamiz.\n\n🔥 *Keling, birgalikda tarix yozamiz! Muvaffaqiyat sari ilk qadamni hoziroq tashlang.*\n\n👇 **Marhamat, quyidagi maxsus menyudan kerakli bo'limni tanlang:**",
        'menu_about': "ℹ️ BIZ HAQIMIZDA",
        'menu_services': "🛠️ XIZMATLAR",
        'menu_prices': "💰 NARXLAR",
        'menu_apply': "📝 ARIZA QOLDIRISH",
        'menu_phone': "📱 TELEFON QOLDIRISH",
        'menu_rate': "⭐ BAHO BERISH",
        'menu_contact': "📞 ALOQA",
        'menu_help': "❓ YORDAM",
        'menu_main': "🏠 ASOSIY MENYU",
        'about_text': "🏢✨ *NOVA.X - RAQAMLI YECHIMLAR JAMOASI* ✨🏢\n\n🌟 *BIZ KIMMIZ?*\nNOVA.X - bu zamonaviy texnologiyalar va kreativ yondashuvlar orqali biznes va shaxsiy brendlarni raqamli dunyoga olib chiqishga ixtisoslashgan yuqori malakali mutaxassislar jamoasi.\n\n📞 *ALOQA:*\nTelefon: {phone}\nTelegram: {telegram}",
        'services_text': "🛠️✨ *NOVA.X XIZMATLARI* ✨🛠️\n\n🎨 *1. DIZAYN XIZMATLARI:*\n• UI/UX Dizayn\n• Logo va brend identifikatsiyasi\n• Veb va mobil dizayn\n\n🌐 *2. VEB-DASTURLASH:*\n• Landing Page\n• Korporativ veb-saytlar\n• Onlayn do'konlar\n• Portfoliolar\n\n📱 *3. MOBIL DASTURLASH:*\n• iOS va Android ilovalari\n• Kross-platform ilovalar\n\n🔍 *4. SEO VA MARKETING:*\n• SEO Optimizatsiya\n• Digital Marketing\n\n☁️ *5. HOSTING VA SERVER:*\n• Domen va hosting\n• VPS va Cloud serverlar\n\n🛡️ *6. XAVFSIZLIK VA SUPPORT:*\n• 24/7 texnik yordam\n• Xavfsizlik himoyasi\n\n👇 *Xizmat turini tanlang:*",
        'prices_text': "💰✨ *NOVA.X NARXLARI* ✨💰\n\n📊 *ASOSIY PAKETLAR:*\n\n🎯 *STARTUP PAKETI - 1 500 000 – 2 000 000 so‘m*\n• Responsive veb-sayt (5 sahifa)\n• Domain va hosting (1 yil)\n• SSL sertifikati\n\n🚀 *BUSINESS PAKETI - 4 000 000 – 6 000 000 so‘m*\n• Full functional veb-sayt (10 sahifa)\n• Admin panel\n• CRM tizimi\n\n🏆 *PREMIUM PAKETI - 8 000 000 – 12 000 000 so‘m*\n• Maxsus veb-ilova\n• Full CMS yoki CRM\n• Mobil ilova\n\n📞 *BATAFSIL MALUMMOT VA BEPUL MASLAHAT:*\n{phone}",
        'contact_text': "📞✨ *NOVA.X BILAN ALOQA* ✨📞\n\n📱 *ASOSIY TELEFON:*\n{phone}\n\n(24/7 qo'llab-quvvatlash)\n\n💬 *TELEGRAM:*\n{telegram}\n\n🎯 *TEZKOR JAVOB:*\nHar qanday savolga 15 daqiqa ichida javob beramiz",
        'help_text': "❓✨ *YORDAM VA KO'P BERILADIGAN SAVOLLAR* ✨❓\n\n🤔 *QANDAY ARIZA QOLDIRISH MUMKIN?*\n1. \"📝 Ariza qoldirish\" tugmasini bosing\n2. Ma'lumotlarni to'ldiring\n3. Xizmat turini tanlang\n\n📞 *QANCHADA JAVOB BERASIZLAR?*\n• Ish vaqtida: 15 daqiqa ichida\n\n💰 *TO'LOV QANDAY AMALGA OSHIRILADI?*\n1. 30% avans to'lov\n2. 40% ish davomida\n3. 30% topshirilganda\n\n⏰ *LOYIHA QANCHADA TAYYOR BO'LADI?*\n• Landing Page: 3-7 kun\n• Veb-sayt: 7-14 kun\n• Mobil ilova: 14-30 kun\n\n📱 *QAYSI TELEFON RAQAMLARIGA MUROJAAT QILISH KERAK?*\nAsosiy raqam: {phone}\n\n💬 *TELEGRAMDA QAYSI PROFILLAR ORQALI BOG'LANISH MUMKIN?*\n{telegram} - Asosiy profil\n\n⭐ *QANDAY BAHO BERISH MUMKIN?*\n\"⭐ Baho berish\" tugmasini bosing va 1 dan 5 gacha baholang\n\n👇 *SAVOLINGIZ QAOLSA, HOZIR BOG'LANING!*",
        'app_start_text': "📝✨ *ARIZA QOLDIRISH* ✨📝\n\n🚀 *LOYIHANGIZNI BOSHLANG!*\n\n📋 *KERAKLI MA'LUMOTLAR:*\n\n👤 *SHU FORMATDA YUBORING:*\nIsm:     [To'liq ismingiz]\nTelefon: [998 XX YYY YY YY]\nXizmat: [Xizmat turi]\n\n👇 *MA'LUMOTLARINGIZNI YUBORING:*",
        'app_success': "✅ *Arizangiz qabul qilindi!*\n\n🆔 *ID:* {id}\n👤 *Ism:* {name}\n📞 *Telefon:* {phone}\n🛠️ *Xizmat:* {service}\n\n⏰ *Operator 1 soat ichida aloqaga chiqadi.*\n📞 *Tezkor javob:* {admin_phone}",
        'phone_start_text': "📱✨ *TELEFON RAQAMINGIZNI QOLDIRING* ✨📱\n\n🎯 *BU NIMA UCHUN KERAK?*\n• Siz bilan bog'lanish\n• Bepul konsultatsiya\n• Aksiya va chegirmalar haqida xabar berish\n\n📞 *QANDAY QOLDIRISH MUMKIN?*\nOddiygina telefon raqamingizni yuboring:\n\n    +998 XX XXX XX XX\n\n👇 *TELEFON RAQAMINGIZNI YUBORING:*",
        'phone_success': "✅ *Raqamingiz qabul qilindi!*\n\n👤 *Ism:* {name}\n📞 *Telefon:* {phone}\n\n⏰ *Operator 15 daqiqa ichida aloqaga chiqadi.*\n📞 *Tezkor javob:* {admin_phone}",
        'rating_start_text': "⭐✨ *BAHO BERISH* ✨⭐\n\n🎯 *BIZNING ISHIMIZNI BAHOLANG!*\n\n5 yulduz tizimi orqali bizning xizmatlarimizni baholang:\n\n⭐⭐⭐⭐⭐ (5) - A'lo, juda mamnun\n⭐⭐⭐⭐ (4) - Yaxshi, mamnun\n⭐⭐⭐ (3) - O'rtacha, yaxshi\n⭐⭐ (2) - Qoniqarsiz, yaxshilash kerak\n⭐ (1) - Yomon, juda norozi\n\n👇 *1 DAN 5 GACHA BAHOLANG:*",
        'rating_success': "✅ *{rating} yulduzli baho qoldirdingiz!*\n\nRahmat, qadringizni bildirganingiz uchun!\n💫 Bahoingiz bizni yanada yaxshilanishimizga yordam beradi.\n\n📞 Agar takliflaringiz bo'lsa: {phone}",
        'error_no_phone': "❌ Telefon raqami aniqlanmadi. Iltimos, qayta yuboring.",
        'service_selected': "🎯 *Siz tanlagan xizmat:* {name}\n\nUshbu xizmat bo'yicha ariza qoldirish uchun ma'lumotlaringizni yuboring.",
        'cancel_btn': "❌ Bekor qilish",
        'back_btn': "🔙 Orqaga",
        'service_website': "🌐 Veb-sayt yaratish",
        'service_mobile': "📱 Mobil ilova",
        'service_design': "🎨 UI/UX Dizayn",
        'service_seo': "🔍 SEO Optimizatsiya",
        'service_hosting': "☁️ Hosting va Server",
        'service_other': "⚡ Boshqa xizmat",
        'lang_changed': "✅ Til muvaffaqiyatli o'zgartirildi!",
        'menu_lang': "🌐 Tilni o'zgartirish"
    },
    'uz_cyr': {
        'select_lang': "🌍 Илтимос, тилни танланг:",
        'welcome': "🌟✨ **АССАЛОМУ АЛАЙКУМ, АЗИЗ {name} {username}!** 👋✨\n\n🎉 **NOVA.X — Рақамли имкониятлар оламига хуш келибсиз!**\nСизни бу ерда кўриб турганимиздан беҳад мамнунмиз! 🤩 Бугун ўзгаришлар ва янги ғалабалар учун ажойиб кун.\n\n🚀 **Сиз айни вақтида, тўғри жойдасиз!**\nБиз шунчаки хизмат кўрсатмаймиз, биз сизнинг орзуларингизни рақамли воқеликка айлантирамиз. Сизнинг бизнесингиз энг юқори чўққиларни забт этишга лойиқ ва биз бунга ёрдам беришга тайёрмиз! 💪\n\n� **Биз билан нималарга эга бўласиз?**\n• � _Бетакрор Дизайн_ — Мижозларингиз бир кўришда севиб қолади.\n• ⚡️ _Кучли Технологиялар_ — Бизнесингиз соат каби аниқ ишлайди.\n• 🤝 _Ишончли Ҳамкорлик_ — Биз доим ёнингиздамиз.\n\n🔥 *Келинг, биргаликда тарих ёзамиз! Муваффақият сари илк қадамни ҳозироқ ташланг.*\n\n👇 **Марҳамат, қуйидаги махсус менюдан керакли бўлимни танланг:**",
        'menu_about': "ℹ️ БИЗ ҲАҚИМИЗДА",
        'menu_services': "🛠️ ХИЗМАТЛАР",
        'menu_prices': "💰 НАРХЛАР",
        'menu_apply': "📝 АРИЗА ҚОЛДИРИШ",
        'menu_phone': "📱 ТЕЛЕФОН ҚОЛДИРИШ",
        'menu_rate': "⭐ БАҲО БЕРИШ",
        'menu_contact': "📞 АЛОҚА",
        'menu_help': "❓ ЁРДАМ",
        'menu_main': "🏠 АСОСИЙ МЕНЮ",
        'about_text': "🏢✨ *NOVA.X - РАҚАМЛИ ЕЧИМЛАР ЖАМОАСИ* ✨🏢\n\n🌟 *БИЗ КИММИЗ?*\nNOVA.X - бу замонавий технологиялар ва креатив ёндашувлар орқали бизнес ва шахсий брендларни рақамли дунёга олиб чиқишга ихтисослашган юқори малакали мутахассислар жамоаси.\n\n📞 *АЛОҚА:*\nТелефон: {phone}\nТелеграм: {telegram}",
        'services_text': "🛠️✨ *NOVA.X ХИЗМАТЛАРИ* ✨🛠️\n\n🎨 *1. ДИЗАЙН ХИЗМАТЛАРИ:*\n• UI/UX Дизайн\n• Лого ва бренд идентификацияси\n• Веб ва мобил дизайн\n\n🌐 *2. ВЕБ-ДАСТУРЛАШ:*\n• Landing Page\n• Корпоратив веб-сайтлар\n• Онлайн дўконлар\n• Портфолиолар\n\n📱 *3. МОБИЛ ДАСТУРЛАШ:*\n• iOS ва Android иловалари\n• Кросс-платформ иловалар\n\n🔍 *4. SEO ВА МАРКЕТИНГ:*\n• SEO Оптимизация\n• Digital Marketing\n\n☁️ *5. ХОСТИНГ ВА СЕРВЕР:*\n• Домен ва хостинг\n• VPS ва Cloud серверлар\n\n🛡️ *6. ХАВФСИЗЛИК ВА SUPPORT:*\n• 24/7 техник ёрдам\n• Хавфсизлик ҳимояси\n\n👇 *Хизмат турини танланг:*",
        'prices_text': "💰✨ *NOVA.X НАРХЛАРИ* ✨💰\n\n📊 *АСОСИЙ ПАКЕТЛАР:*\n\n🎯 *STARTUP ПАКЕТИ - 1 500 000 – 2 000 000 сўм*\n• Responsive веб-сайт (5 саҳифа)\n• Домаин ва хостинг (1 йил)\n• SSL сертификати\n\n🚀 *BUSINESS ПАКЕТI - 4 000 000 – 6 000 000 сўм*\n• Full functional веб-сайт (10 саҳифа)\n• Админ панел\n• CRM тизими\n\n🏆 *PREMIUM ПАКЕТИ - 8 000 000 – 12 000 000 сўм*\n• Махсус веб-илова\n• Full CMS ёки CRM\n• Мобил илова\n\n📞 *БАТАФСИЛ МАЪЛУМОТ ВА БЕПУЛ МАСЛАҲАТ:*\n{phone}",
        'contact_text': "📞✨ *NOVA.X БИЛАН АЛОҚА* ✨📞\n\n📱 *АСОСИЙ ТЕЛЕФОН:*\n{phone}\n\n(24/7 қўллаб-қувватлаш)\n\n💬 *ТЕЛЕГРАМ:*\n{telegram}\n\n🎯 *ТЕЗКОР ЖАВОБ:*\nҲар қандай саволга 15 дақиқа ичида жавоб берамиз",
        'help_text': "❓✨ *ЁРДАМ ВА КЎП БЕРИЛАДИГАН САВОЛЛАР* ✨❓\n\n🤔 *ҚАНДАЙ АРИЗА ҚОЛДИРИШ МУМКИН?*\n1. \"📝 Ариза қолдириш\" тугмасини босинг\n2. Маълумотларни тўлдиринг\n3. Хизмат турини танланг\n\n📞 *ҚАНЧАДА ЖАВОБ БЕРАСИЗЛАР?*\n• Иш вақтида: 15 дақиқа ичида\n\n💰 *ТЎЛОВ ҚАНДАЙ АМАЛГА ОШИРИЛАДИ?*\n1. 30% аванс тўлов\n2. 40% иш давомида\n3. 30% топширилганда\n\n⏰ *ЛОЙИҲА ҚАНЧАДА ТАЙЁР БЎЛАДИ?*\n• Landing Page: 3-7 кун\n• Веб-сайт: 7-14 кун\n• Мобил илова: 14-30 кун\n\n📱 *ҚАЙСИ ТЕЛЕФОН РАҚАМЛАРИГА МУРОЖААТ ҚИЛИШ КЕРАК?*\nАсосий рақам: {phone}\n\n💬 *ТЕЛЕГРАМДА ҚАЙСИ ПРОФИЛЛАР ОРҚАЛИ БОҒЛАНИШ МУМКИН?*\n{telegram} - Асосий профил\n\n⭐ *ҚАНДАЙ БАҲО БЕРИШ МУМКИН?*\n\"⭐ Баҳо бериш\" тугмасини босинг ва 1 дан 5 гача баҳоланг\n\n👇 *САВОЛИНГИЗ ҚОЛСА, ҲОЗИР БОҒЛАНИНГ!*",
        'app_start_text': "📝✨ *АРИЗА ҚОЛДИРИШ* ✨📝\n\n🚀 *ЛОЙИҲАНГИЗНИ БОШЛАНГ!*\n\n📋 *КЕРАКЛИ МАЪЛУМOTЛАР:*\n\n👤 *ШУ ФОРМАТДА ЮБОРИНГ:*\nИсм:     [Тўлиқ исмингиз]\nТелефон: [998 XX YYY YY YY]\nХизмат: [Хизмат тури]\n\n👇 *МАЪЛУМОТЛАРИНГИНГИЗНИ ЮБОРИНГ:*",
        'app_success': "✅ *Аризангиз қабул қилинди!*\n\n🆔 *ＩＤ:* {id}\n👤 *Исм:* {name}\n📞 *Телефон:* {phone}\n🛠️ *Хизмат:* {service}\n\n⏰ *Оператор 1 соат ичида алоқага чиқади.*\n📞 *Тезкор жавоб:* {admin_phone}",
        'phone_start_text': "📱✨ *ТЕЛЕФОН РАҚАМИНГИЗНИ ҚОЛДИРИНГ* ✨📱\n\n🎯 *БУ НИМА УЧУН КЕРАК?*\n• Сиз билан боғланиш\n• Бепул консультация\n• Акция ва чегирмалар ҳақида хабар бериш\n\n📞 *ҚАНДАЙ ҚОЛДИРИШ МУМКИН?*\nОддийгина телефон рақамингизни юборинг:\n\n    +998 XX XXX XX XX\n\n👇 *ТЕЛЕФОН РАҚАМИНГИЗНИ ЮБОРИНГ:*",
        'phone_success': "✅ *Рақамингиз қабул қилинди!*\n\n👤 *Исм:* {name}\n📞 *Телефон:* {phone}\n\n⏰ *Оператор 15 дақиқа ичида алоқага чиқади.*\n📞 *Тезкор жавоб:* {admin_phone}",
        'rating_start_text': "⭐✨ *БАҲО БЕРИШ* ✨⭐\n\n🎯 *БИЗНИНГ ИШИМИЗНИ БАҲОЛАНГ!*\n\n5 юлдуз тизими орқали бизнинг хизматларимизни баҳоланг:\n\n⭐⭐⭐⭐⭐ (5) - Аъло, жуда мамнун\n⭐⭐⭐⭐ (4) - Яхши, мамнун\n⭐⭐⭐ (3) - Ўртача, яхши\n⭐⭐ (2) - Қониқарсиз, яхшилаш керак\n⭐ (1) - Ёмон, жуда норози\n\n👇 *1 ДАН 5 ГАЧА БАҲОЛАНГ:*",
        'rating_success': "✅ *{rating} юлдузли баҳо қолдирдингиз!*\n\nРаҳмат, қадрингизни билдирганингиз учун!\n💫 Баҳойингиз бизни янада яхшиланишимизга ёрдам беради.\n\n📞 Агар таклифларингиз бўлса: {phone}",
        'error_no_phone': "❌ Телефон рақами аниқланмади. Илтимос, қайта юборинг.",
        'service_selected': "🎯 *Сиз танлаган хизмат:* {name}\n\nУшбу хизмат бўйича ариза қолдириш учун маълумотларингизни юборинг.",
        'cancel_btn': "❌ Бекор қилиш",
        'back_btn': "🔙 Орқага",
        'service_website': "🌐 Веб-сайт яратиш",
        'service_mobile': "📱 Мобил илова",
        'service_design': "🎨 UI/UX Дизайн",
        'service_seo': "🔍 SEO Оптимизация",
        'service_hosting': "☁️ Хостинг ва Сервер",
        'service_other': "⚡ Бошқа хизмат",
        'lang_changed': "✅ Тил муваффақиятли ўзгартирилди!",
        'menu_lang': "🌐 Тилни ўзгартириш"
    },
    'ru': {
        'select_lang': "🌍 Пожалуйста, выберите язык:",
        'welcome': "🌟✨ **ПРИВЕТСТВУЕМ ВАС, {name} {username}!** 👋✨\n\n🎉 **Добро пожаловать в мир цифровых возможностей NOVA.X!**\nМы безумно рады видеть вас здесь! 🤩 Сегодня прекрасный день для перемен и новых побед.\n\n🚀 **Вы в нужном месте и в нужное время!**\nМы не просто предоставляем услуги, мы превращаем ваши мечты в цифровую реальность. Ваш бизнес заслуживает того, чтобы быть на вершине, и мы готовы помочь вам в этом! 💪\n\n� **Что вы получите с нами?**\n• � _Неповторимый Дизайн_ — Ваши клиенты влюбятся с первого взгляда.\n• ⚡️ _Мощные Технологии_ — Ваш бизнес будет работать точно, как часы.\n• 🤝 _Надежное Партнерство_ — Мы всегда рядом с вами.\n\n🔥 *Давайте творить историю вместе! Сделайте первый шаг к успеху прямо сейчас.*\n\n👇 **Пожалуйста, выберите нужный раздел из специального меню:**",
        'menu_about': "ℹ️ О НАС",
        'menu_services': "🛠️ УСЛУГИ",
        'menu_prices': "💰 ЦЕНЫ",
        'menu_apply': "📝 ОСТАВИТЬ ЗАЯВКУ",
        'menu_phone': "📱 ОСТАВИТЬ НОМЕР",
        'menu_rate': "⭐ ОЦЕНИТЬ",
        'menu_contact': "📞 КОНТАКТЫ",
        'menu_help': "❓ ПОМОЩЬ",
        'menu_main': "🏠 ГЛАВНОЕ МЕНЮ",
        'about_text': "🏢✨ *NOVA.X - КОМАНДА ЦИФРОВЫХ РЕШЕНИЙ* ✨🏢\n\n🌟 *КТО МЫ?*\nNOVA.X - это команда высококвалифицированных специалистов, специализирующаяся на выводе бизнеса и личных брендов в цифровой мир с помощью современных технологий и креативных подходов.\n\n📞 *КОНТАКТЫ:*\nТелефон: {phone}\nTelegram: {telegram}",
        'services_text': "🛠️✨ *УСЛУГИ NOVA.X* ✨🛠️\n\n🎨 *1. ДИЗАЙН:*\n• UI/UX Дизайн\n• Логотип и брендинг\n• Веб и мобильный дизайн\n\n🌐 *2. ВЕБ-РАЗРАБОТКА:*\n• Landing Page\n• Корпоративные сайты\n• Онлайн магазины\n• Портфолио\n\n📱 *3. МОБИЛЬНАЯ РАЗРАБОТКА:*\n• Приложения для iOS и Android\n• Кроссплатформенные приложения\n\n🔍 *4. SEO И МАРКЕТИНГ:*\n• SEO Оптимизация\n• Digital Marketing\n\n☁️ *5. ХОСТИНГ И СЕРВЕР:*\n• Домен и хостинг\n• VPS и Cloud серверы\n\n🛡️ *6. БЕЗОПАСНОСТЬ И ПОДДЕРЖКА:*\n• Техподдержка 24/7\n• Защита безопасности\n\n👇 *Выберите тип услуги:*",
        'prices_text': "💰✨ *ЦЕНЫ NOVA.X* ✨💰\n\n📊 *ОСНОВНЫЕ ПАКЕТЫ:*\n\n🎯 *STARTUP ПАКЕТ - 1 500 000 – 2 000 000 сум*\n• Адаптивный сайт (5 страниц)\n• Домен и хостинг (1 год)\n• SSL сертификат\n\n🚀 *BUSINESS ПАКЕТ - 4 000 000 – 6 000 000 сум*\n• Полнофункциональный сайт (10 страниц)\n• Админ панель\n• CRM система\n\n🏆 *PREMIUM ПАКЕТ - 8 000 000 – 12 000 000 сум*\n• Специальное веб-приложение\n• Full CMS или CRM\n• Мобильное приложение\n\n📞 *ПОДРОБНУЮ ИНФОРМАЦИЮ МОЖНО ПОЛУЧИТЬ ПО ТЕЛЕФОНУ:*\n{phone}",
        'contact_text': "📞✨ *СВЯЗЬ С NOVA.X* ✨📞\n\n📱 *ОСНОВНОЙ ТЕЛЕФОН:*\n{phone}\n\n(Поддержка 24/7)\n\n💬 *TELEGRAM:*\n{telegram}\n\n🎯 *БЫСТРЫЙ ОТВЕТ:*\nОтвечаем на любые вопросы в течение 15 минут",
        'help_text': "❓✨ *ПОМОЩЬ И ОТВЕТЫ НА ВОПРОСЫ* ✨❓\n\n🤔 *КАК ОСТАВИТЬ ЗАЯВКУ?*\n1. Нажмите кнопку \"📝 Оставить заявку\"\n2. Заполните данные\n3. Выберите тип услуги\n\n📞 *КАК БЫСТРО ВЫ ОТВЕЧАЕТЕ?*\n• В рабочее время: в течение 15 минут\n\n💰 *КАК ОСУЩЕСТВЛЯЕТСЯ ОПЛАТА?*\n1. 30% аванс\n2. 40% во время работы\n3. 30% при сдаче\n\n⏰ *СРОКИ ВЫПОЛНЕНИЯ?*\n• Landing Page: 3-7 дней\n• Веб-сайт: 7-14 дней\n• Мобильное приложение: 14-30 дней\n\n📱 *ПО КАКИМ НОМЕРАМ ОБРАЩАТЬСЯ?*\nОсновной номер: {phone}\n\n💬 *ПО КАКИМ ПРОФИЛЯМ СВЯЗАТЬСЯ В TELEGRAM?*\n{telegram} - Основной профиль\n\n⭐ *КАК ОСТАВИТЬ ОТЗЫВ?*\nНажмите кнопку \"⭐ Оценить\" и поставьте от 1 до 5 звезд\n\n👇 *ЕСЛИ ОСТАЛИСЬ ВОПРОСЫ, СВЯЖИТЕСЬ СЕЙЧАС!*",
        'app_start_text': "📝✨ *ОСТАВИТЬ ЗАЯВКУ* ✨📝\n\n🚀 *НАЧНИТЕ СВОЙ ПРОЕКТ!*\n\n📋 *НЕОБХОДИМЫЕ ДАННЫЕ:*\n\n👤 *ОТПРАВЬТЕ В ТАКОМ ФОРМАТЕ:*\nИмя:     [Ваше полное имя]\nТелефон: [998 XX YYY YY YY]\nУслуга:  [Тип услуги]\n\n👇 *ОТПРАВЬТЕ ВАШИ ДАННЫЕ:*",
        'app_success': "✅ *Ваша заявка принята!*\n\n🆔 *ＩＤ:* {id}\n👤 *Имя:* {name}\n📞 *Телефон:* {phone}\n🛠️ *Услуга:* {service}\n\n⏰ *Оператор свяжется с вами в течение 1 часа.*\n📞 *Быстрый ответ:* {admin_phone}",
        'phone_start_text': "📱✨ *ОСТАВЬТЕ СВОЙ НОМЕР* ✨📱\n\n🎯 *ДЛЯ ЧЕГО ЭТО НУЖНО?*\n• Чтобы связаться с вами\n• Бесплатная консультация\n• Уведомления об акциях и скидках\n\n📞 *КАК ОСТАВИТЬ?*\nПросто отправьте свой номер телефона:\n\n    +998 XX XXX XX XX\n\n👇 *ОТПРАВЬТЕ ВАШ НОМЕР ТЕЛЕФОНА:*",
        'phone_success': "✅ *Ваш номер принят!*\n\n👤 *Имя:* {name}\n📞 *Телефон:* {phone}\n\n⏰ *Оператор свяжется с вами в течение 15 минут.*\n📞 *Быстрый ответ:* {admin_phone}",
        'rating_start_text': "⭐✨ *ОЦЕНКА КАЧЕСТВА* ✨⭐\n\n🎯 *ОЦЕНИТЕ НАШУ РАБОТУ!*\n\nОцените наши услуги по 5-балльной шкале:\n\n⭐⭐⭐⭐⭐ (5) - Отлично, очень доволен\n⭐⭐⭐⭐ (4) - Хорошо, доволен\n⭐⭐⭐ (3) - Средне, нормально\n⭐⭐ (2) - Неудовлетворительно, нужно улучшить\n⭐ (1) - Плохо, очень недоволен\n\n👇 *ОЦЕНИТЕ ОТ 1 ДО 5:*",
        'rating_success': "✅ *Вы оставили оценку {rating} звезд!*\n\nСпасибо, что цените нашу работу!\n💫 Ваш отзыв поможет нам стать еще лучше.\n\n📞 Если есть предложения: {phone}",
        'error_no_phone': "❌ Номер телефона не определен. Пожалуйста, отправьте еще раз.",
        'service_selected': "🎯 *Выбранная услуга:* {name}\n\nОтправьте свои данные, чтобы оставить заявку на эту услугу.",
        'cancel_btn': "❌ Отмена",
        'back_btn': "🔙 Назад",
        'service_website': "🌐 Создание веб-сайтов",
        'service_mobile': "📱 Мобильные приложения",
        'service_design': "🎨 UI/UX Дизайн",
        'service_seo': "🔍 SEO Оптимизация",
        'service_hosting': "☁️ Хостинг и Серверы",
        'service_other': "⚡ Другие услуги",
        'lang_changed': "✅ Язык успешно изменен!",
        'menu_lang': "🌐 Изменить язык"
    },
    'en': {
        'select_lang': "🌍 Please select a language:",
        'welcome': "🌟✨ **HELLO, DEAR {name} {username}!** 👋✨\n\n🎉 **Welcome to the World of Digital Opportunities with NOVA.X!**\nWe are absolutely thrilled to have you here! 🤩 Today is a wonderful day for changes and new victories.\n\n🚀 **You are in the right place at the right time!**\nWe don't just provide services; we turn your dreams into digital reality. Your business deserves to be at the top, and we are ready to help you get there! 💪\n\n� **What will you get with us?**\n• � _Unique Design_ — Your customers will fall in love at first sight.\n• ⚡️ _Powerful Technologies_ — Your business will run like clockwork.\n• 🤝 _Reliable Partnership_ — We are always by your side.\n\n� *Let's make history together! Take the first step towards success right now.*\n\n👇 **Please, select the desired section from the special menu:**",
        'menu_about': "ℹ️ ABOUT US",
        'menu_services': "🛠️ SERVICES",
        'menu_prices': "💰 PRICES",
        'menu_apply': "📝 LEAVE APPLICATION",
        'menu_phone': "📱 LEAVE PHONE",
        'menu_rate': "⭐ RATE US",
        'menu_contact': "📞 CONTACT",
        'menu_help': "❓ HELP",
        'menu_main': "🏠 MAIN MENU",
        'about_text': "🏢✨ *NOVA.X - DIGITAL SOLUTIONS TEAM* ✨🏢\n\n🌟 *WHO ARE WE?*\nNOVA.X is a team of highly qualified specialists dedicated to bringing businesses and personal brands into the digital world through modern technologies and creative approaches.\n\n📞 *CONTACT:*\nPhone: {phone}\nTelegram: {telegram}",
        'services_text': "🛠️✨ *NOVA.X SERVICES* ✨🛠️\n\n🎨 *1. DESIGN SERVICES:*\n• UI/UX Design\n• Logo and brand identity\n• Web and mobile design\n\n🌐 *2. WEB DEVELOPMENT:*\n• Landing Page\n• Corporate websites\n• Online stores\n• Portfolios\n\n📱 *3. MOBILE DEVELOPMENT:*\n• iOS and Android apps\n• Cross-platform apps\n\n🔍 *4. SEO AND MARKETING:*\n• SEO Optimization\n• Digital Marketing\n\n☁️ *5. HOSTING AND SERVER:*\n• Domain and hosting\n• VPS and Cloud servers\n\n🛡️ *6. SECURITY AND SUPPORT:*\n• 24/7 technical support\n• Security protection\n\n👇 *Select a service type:*",
        'prices_text': "💰✨ *NOVA.X PRICES* ✨💰\n\n📊 *MAIN PACKAGES:*\n\n🎯 *STARTUP PACKAGE - 1,500,000 – 2,000,000 UZS*\n• Responsive website (5 pages)\n• Domain and hosting (1 year)\n• SSL certificate\n\n🚀 *BUSINESS PACKAGE - 4,000,000 – 6,000,000 UZS*\n• Full functional website (10 pages)\n• Admin panel\n• CRM system\n\n🏆 *PREMIUM PACKAGE - 8,000,000 – 12,000,000 UZS*\n• Special web application\n• Full CMS or CRM\n• Mobile application\n\n📞 *FOR MORE INFORMATION AND FREE CONSULTATION:* \n{phone}",
        'contact_text': "📞✨ *CONTACT NOVA.X* ✨📞\n\n📱 *MAIN PHONE:*\n{phone}\n\n(24/7 Support)\n\n💬 *TELEGRAM:*\n{telegram}\n\n🎯 *QUICK RESPONSE:*\nWe answer any questions within 15 minutes",
        'help_text': "❓✨ *HELP AND FAQ* ✨❓\n\n🤔 *HOW TO LEAVE AN APPLICATION?*\n1. Press the \"📝 Leave application\" button\n2. Fill in the information\n3. Select the service type\n\n📞 *HOW FAST DO YOU RESPOND?*\n• During working hours: within 15 minutes\n\n💰 *HOW IS PAYMENT MADE?*\n1. 30% advance payment\n2. 40% during work\n3. 30% upon delivery\n\n⏰ *HOW LONG DOES THE PROJECT TAKE?*\n• Landing Page: 3-7 days\n• Website: 7-14 days\n• Mobile App: 14-30 days\n\n📱 *WHICH PHONE NUMBERS TO CONTACT?*\nMain number: {phone}\n\n💬 *WHICH TELEGRAM PROFILES TO CONTACT?*\n{telegram} - Main profile\n\n⭐ *HOW TO RATE US?*\nPress the \"⭐ Rate us\" button and rate from 1 to 5\n\n👇 *IF YOU HAVE ANY QUESTIONS, CONTACT US NOW!*",
        'app_start_text': "📝✨ *LEAVE APPLICATION* ✨📝\n\n🚀 *START YOUR PROJECT!*\n\n📋 *REQUIRED INFORMATION:*\n\n👤 *SEND IN THIS FORMAT:*\nName:    [Your full name]\nPhone:   [998 XX YYY YY YY]\nService: [Service type]\n\n👇 *SEND YOUR INFORMATION:*",
        'app_success': "✅ *Your application has been accepted!*\n\n🆔 *ＩＤ:* {id}\n👤 *Name:* {name}\n📞 *Phone:* {phone}\n🛠️ *Service:* {service}\n\n⏰ *Operator will contact you within 1 hour.*\n📞 *Quick response:* {admin_phone}",
        'phone_start_text': "📱✨ *LEAVE YOUR PHONE NUMBER* ✨📱\n\n🎯 *WHY IS THIS NEEDED?*\n• To contact you\n• Free consultation\n• Notification about promotions and discounts\n\n📞 *HOW TO LEAVE?*\nSimply send your phone number:\n\n    +998 XX XXX XX XX\n\n👇 *SEND YOUR PHONE NUMBER:*",
        'phone_success': "✅ *Your number has been accepted!*\n\n👤 *Name:* {name}\n📞 *Phone:* {phone}\n\n⏰ *Operator will contact you within 15 minutes.*\n📞 *Quick response:* {admin_phone}",
        'rating_start_text': "⭐✨ *RATE US* ✨⭐\n\n🎯 *RATE OUR WORK!*\n\nRate our services through the 5-star system:\n\n⭐⭐⭐⭐⭐ (5) - Excellent, very satisfied\n⭐⭐⭐⭐ (4) - Good, satisfied\n⭐⭐⭐ (3) - Average, okay\n⭐⭐ (2) - Unsatisfactory, need improvement\n⭐ (1) - Poor, very dissatisfied\n\n👇 *RATE FROM 1 TO 5:*",
        'rating_success': "✅ *You gave a {rating}-star rating!*\n\nThank you for valuing our work!\n💫 Your rating helps us to improve further.\n\n📞 If you have suggestions: {phone}",
        'error_no_phone': "❌ Phone number not detected. Please send again.",
        'service_selected': "🎯 *Your selected service:* {name}\n\nSend your information to leave an application for this service.",
        'cancel_btn': "❌ Cancel",
        'back_btn': "🔙 Back",
        'service_website': "🌐 Website Creation",
        'service_mobile': "📱 Mobile App",
        'service_design': "🎨 UI/UX Design",
        'service_seo': "🔍 SEO Optimization",
        'service_hosting': "☁️ Hosting and Server",
        'service_other': "⚡ Other service",
        'lang_changed': "✅ Language successfully changed!",
        'menu_lang': "🌐 Change Language"
    }
}

def t(key, lang, **kwargs):
    """Tarjima yordamchisi"""
    if not lang:
        lang = 'uz_lat'
    
    text = TRANSLATIONS.get(lang, TRANSLATIONS['uz_lat']).get(key, TRANSLATIONS['uz_lat'].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            return text
    return text

print("=" * 70)

# ==================== DATABASE ====================
class NovaDatabase:
    """Ma'lumotlar bazasi"""
    
    def __init__(self):
        self.data_file = "nova_x_database.json"
        self.backup_dir = "backups"
        self.load_data()
    
    def load_data(self):
        """Ma'lumotlarni yuklash"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "applications": [],
                    "contacts": [],
                    "ratings": [],
                    "users": {},
                    "stats": {
                        "total_applications": 0,
                        "total_contacts": 0,
                        "total_ratings": 0,
                        "average_rating": 0,
                        "today_applications": 0,
                        "weekly_applications": 0,
                        "monthly_applications": 0
                    }
                }
                self.save_data()
        except Exception as e:
            logger.error(f"Ma'lumotlarni yuklashda xato: {e}")
            self.data = {
                "applications": [],
                "contacts": [],
                "ratings": [],
                "users": {},
                "stats": {
                    "total_applications": 0,
                    "total_contacts": 0,
                    "total_ratings": 0,
                    "average_rating": 0,
                    "today_applications": 0,
                    "weekly_applications": 0,
                    "monthly_applications": 0
                }
            }
    
    def set_user_lang(self, user_id: int, lang: str):
        """Foydalanuvchi tilini saqlash"""
        if "users" not in self.data:
            self.data["users"] = {}
        
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {}
            
        self.data["users"][user_id_str]["lang"] = lang
        self.save_data()

    def get_user_lang(self, user_id: int):
        """Foydalanuvchi tilini olish"""
        if "users" not in self.data:
            return None
        return self.data.get("users", {}).get(str(user_id), {}).get("lang")
    
    def save_data(self):
        """Ma'lumotlarni saqlash"""
        try:
            self.update_stats()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ma'lumotlarni saqlashda xato: {e}")
            return False
    
    def update_stats(self):
        """Statistikani yangilash"""
        today = datetime.now().strftime("%d.%m.%Y")
        
        # Bugungi arizalar
        today_apps = [app for app in self.data["applications"] if app["date"].startswith(today)]
        
        # Reytinglar
        ratings = self.data.get("ratings", [])
        total_ratings = len(ratings)
        avg_rating = 0
        if total_ratings > 0:
            avg_rating = sum(r["rating"] for r in ratings) / total_ratings
        
        self.data["stats"] = {
            "total_applications": len(self.data["applications"]),
            "total_contacts": len(self.data["contacts"]),
            "total_ratings": total_ratings,
            "average_rating": round(avg_rating, 1),
            "today_applications": len(today_apps),
            "last_updated": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
    
    def add_application(self, user_id: int, name: str, phone: str, service: str, message: str = ""):
        """Yangi ariza qo'shish"""
        app_id = len(self.data["applications"]) + 1
        
        application = {
            "id": app_id,
            "user_id": user_id,
            "name": name,
            "phone": phone,
            "service": service,
            "message": message,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "status": "yangi",
            "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
        
        self.data["applications"].append(application)
        self.save_data()
        return application
    
    def update_application_status(self, app_id: int, status: str):
        """Ariza holatini yangilash"""
        for app in self.data["applications"]:
            if app["id"] == app_id:
                app["status"] = status
                app["updated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                self.save_data()
                return True
        return False
    
    def add_contact(self, user_id: int, name: str, phone: str, message: str = ""):
        """Yangi kontakt qo'shish"""
        contact_id = len(self.data["contacts"]) + 1
        
        contact = {
            "id": contact_id,
            "user_id": user_id,
            "name": name,
            "phone": phone,
            "message": message,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "contacted": False
        }
        
        self.data["contacts"].append(contact)
        self.save_data()
        return contact
    
    def add_rating(self, user_id: int, rating: int, feedback: str = ""):
        """Yangi baho qo'shish"""
        rating_id = len(self.data["ratings"]) + 1
        
        rating_data = {
            "id": rating_id,
            "user_id": user_id,
            "rating": rating,
            "feedback": feedback,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        }
        
        self.data["ratings"].append(rating_data)
        self.save_data()
        return rating_data
    
    def get_all_applications(self):
        """Barcha arizalarni olish"""
        return self.data["applications"]
    
    def get_applications_by_status(self, status: str):
        """Holat bo'yicha arizalarni olish"""
        if status == "all":
            return self.data["applications"]
        return [app for app in self.data["applications"] if app.get("status") == status]
    
    def get_today_applications(self):
        """Bugungi arizalarni olish"""
        today = datetime.now().strftime("%d.%m.%Y")
        return [app for app in self.data["applications"] if app["date"].startswith(today)]
    
    def get_all_contacts(self):
        """Barcha kontaktlarni olish"""
        return self.data["contacts"]
    
    def get_all_ratings(self):
        """Barcha baholarni olish"""
        return self.data["ratings"]
    
    def get_stats(self):
        """Statistikani olish"""
        return self.data["stats"]

# Global database obyekti
db = NovaDatabase()

# ==================== MENYULAR ====================
def get_language_keyboard():
    """Tilni tanlash uchun inline keyboard"""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek (Lotin)", callback_data="set_lang_uz_lat")],
        [InlineKeyboardButton("🇺🇿 Ўзбек (Кирилл)", callback_data="set_lang_uz_cyr")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu(is_admin: bool = False, lang: str = 'uz_lat'):
    """Asosiy menyu"""
    if is_admin:
        buttons = [
            ["📊 STATISTIKA", "📋 ARIZALAR"],
            ["📅 BUGUNGI", "📞 KONTAKTLAR"],
            ["⭐ BAHOLAR", "📤 EXPORT"],
            ["⚙️ SOZLAMALAR", "🏠 ASOSIY MENYU"]
        ]
    else:
        buttons = [
            [t('menu_about', lang), t('menu_services', lang)],
            [t('menu_prices', lang), t('menu_apply', lang)],
            [t('menu_phone', lang), t('menu_rate', lang)],
            [t('menu_contact', lang), t('menu_help', lang)],
            [t('menu_lang', lang)]
        ]
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def get_admin_applications_menu():
    """Admin arizalar menyusi"""
    keyboard = [
        [InlineKeyboardButton("🆕 Yangi arizalar", callback_data="admin_apps_new")],
        [InlineKeyboardButton("⏳ Jarayonda", callback_data="admin_apps_progress")],
        [InlineKeyboardButton("✅ Bajarilgan", callback_data="admin_apps_completed")],
        [InlineKeyboardButton("❌ Bekor qilingan", callback_data="admin_apps_cancelled")],
        [InlineKeyboardButton("📊 Barchasi", callback_data="admin_apps_all")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_export_menu():
    """Admin export menyusi"""
    keyboard = [
        [InlineKeyboardButton("📋 Arizalar (CSV)", callback_data="export_apps_csv")],
        [InlineKeyboardButton("📞 Kontaktlar (CSV)", callback_data="export_contacts_csv")],
        [InlineKeyboardButton("⭐ Baholar (CSV)", callback_data="export_ratings_csv")],
        [InlineKeyboardButton("📊 Statistika (TXT)", callback_data="export_stats_txt")],
        [InlineKeyboardButton("📁 Hammasi (ZIP)", callback_data="export_all_zip")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_application_actions(app_id: int):
    """Ariza uchun amallar"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Bajarildi", callback_data=f"app_complete_{app_id}"),
            InlineKeyboardButton("⏳ Jarayonda", callback_data=f"app_progress_{app_id}")
        ],
        [
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"app_cancel_{app_id}"),
            InlineKeyboardButton("📞 Bog'lanish", callback_data=f"app_contact_{app_id}")
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_apps_all")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_rating_keyboard():
    """Baho berish uchun inline keyboard"""
    keyboard = []
    for i in range(1, 6):
        stars = "⭐" * i
        keyboard.append([InlineKeyboardButton(f"{stars} ({i}/5)", callback_data=f"rate_{i}")])
    
    keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_rate")])
    return InlineKeyboardMarkup(keyboard)

def get_service_keyboard():
    """Xizmatlar uchun inline keyboard"""
    buttons = [
        [InlineKeyboardButton("🌐 Veb-sayt yaratish", callback_data="service_website")],
        [InlineKeyboardButton("📱 Mobil ilova", callback_data="service_mobile")],
        [InlineKeyboardButton("🎨 UI/UX Dizayn", callback_data="service_design")],
        [InlineKeyboardButton("🔍 SEO Optimizatsiya", callback_data="service_seo")],
        [InlineKeyboardButton("☁️ Hosting va Server", callback_data="service_hosting")],
        [InlineKeyboardButton("⚡ Boshqa xizmat", callback_data="service_other")]
    ]
    return InlineKeyboardMarkup(buttons)

# ==================== USER FUNCTIONS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    
    lang = db.get_user_lang(user_id)
    
    if not lang:
        await context.bot.send_message(
            chat_id=chat_id,
            text=t('select_lang', 'uz_lat'),
            reply_markup=get_language_keyboard()
        )
        return

    # Usernameni aniqlash (agar bo'lsa @ bilan, bo'lmasa bo'sh)
    username = f"(@{user.username})" if user.username else ""
    
    welcome_message = t('welcome', lang, name=user.first_name, username=username)
    
    # Admin tekshiruvi
    is_admin = user_id in ADMIN_IDS
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=welcome_message,
        parse_mode='Markdown',
        reply_markup=get_main_menu(is_admin, lang)
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Biz haqimizda"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    about_text = t('about_text', lang, phone=ADMIN_PHONE, telegram=ADMIN_TELEGRAM)
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xizmatlar"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    services_text = t('services_text', lang)
    
    # Custom keyboard for services with translations
    buttons = [
        [InlineKeyboardButton(t('service_website', lang), callback_data="service_website")],
        [InlineKeyboardButton(t('service_mobile', lang), callback_data="service_mobile")],
        [InlineKeyboardButton(t('service_design', lang), callback_data="service_design")],
        [InlineKeyboardButton(t('service_seo', lang), callback_data="service_seo")],
        [InlineKeyboardButton(t('service_hosting', lang), callback_data="service_hosting")],
        [InlineKeyboardButton(t('service_other', lang), callback_data="service_other")]
    ]
    
    await update.message.reply_text(
        services_text, 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Narxlar"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    prices_text = t('prices_text', lang, phone=ADMIN_PHONE)
    await update.message.reply_text(prices_text, parse_mode='Markdown')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aloqa"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    contact_text = t('contact_text', lang, phone=ADMIN_PHONE, telegram=ADMIN_TELEGRAM)
    await update.message.reply_text(contact_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    help_text = t('help_text', lang, phone=ADMIN_PHONE, telegram=ADMIN_TELEGRAM)
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ==================== APPLICATION FUNCTIONS ====================
async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ariza boshlash"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    application_text = t('app_start_text', lang)
    await update.message.reply_text(application_text, parse_mode='Markdown')
    context.user_data['awaiting_application'] = True

async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ariza ma'lumotlarini qayta ishlash"""
    if not context.user_data.get('awaiting_application'):
        return
    
    user = update.effective_user
    text = update.message.text
    lang = db.get_user_lang(user.id) or 'uz_lat'
    
    # Ma'lumotlarni ajratish
    name = user.first_name or "Noma'lum"
    phone = ""
    service = "Noma'lum"
    
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if 'ism' in key or 'name' in key or 'исм' in key:
                name = value
            elif 'tel' in key or 'phone' in key or 'тел' in key:
                phone = value
            elif 'xizmat' in key or 'service' in key or 'хизмат' in key or 'услуга' in key:
                service = value
    
    # Raqamni topish
    if not phone:
        numbers = re.findall(r'[\+\d\s\-\(\)]{10,}', text)
        if numbers:
            phone = numbers[0]
        elif text.replace('+', '').replace(' ', '').isdigit():
            phone = text
    
    if not phone:
        await update.message.reply_text(t('error_no_phone', lang))
        return
    
    # Saqlash
    app = db.add_application(user.id, name, phone, service, text)
    
    # Foydalanuvchiga javob
    await update.message.reply_text(
        t('app_success', lang, id=app['id'], name=name, phone=phone, service=service, admin_phone=ADMIN_PHONE),
        parse_mode='Markdown',
        reply_markup=get_main_menu(lang=lang)
    )
    
    # Adminlarga xabar
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📥 *YANGI ARIZA #{app['id']}*\n\n"
                     f"👤 *Ism:* {name}\n"
                     f"📞 *Telefon:* {phone}\n"
                     f"🛠️ *Xizmat:* {service}\n"
                     f"📅 *Vaqt:* {app['date']}\n"
                     f"🆔 *User ID:* {user.id}\n"
                     f"🌐 *Til:* {lang}",
                parse_mode='Markdown'
            )
        except:
            pass
    
    context.user_data.pop('awaiting_application', None)

# ==================== PHONE CONTACT FUNCTIONS ====================
async def start_phone_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon qoldirish"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    phone_text = t('phone_start_text', lang)
    await update.message.reply_text(phone_text, parse_mode='Markdown')
    context.user_data['awaiting_phone'] = True

async def handle_phone_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon kontaktini qayta ishlash"""
    if not context.user_data.get('awaiting_phone'):
        return
    
    user = update.effective_user
    text = update.message.text
    lang = db.get_user_lang(user.id) or 'uz_lat'
    
    # Telefon raqamini topish
    phone = ""
    numbers = re.findall(r'[\+\d\s\-\(\)]{10,}', text)
    if numbers:
        phone = numbers[0]
    elif text.replace('+', '').replace(' ', '').isdigit():
        phone = text
    
    if not phone:
        await update.message.reply_text(t('error_no_phone', lang))
        return
    
    name = user.first_name or "Noma'lum"
    
    # Saqlash
    contact = db.add_contact(user.id, name, phone, text)
    
    # Foydalanuvchiga javob
    await update.message.reply_text(
        t('phone_success', lang, name=name, phone=phone, admin_phone=ADMIN_PHONE),
        parse_mode='Markdown',
        reply_markup=get_main_menu(lang=lang)
    )
    
    # Adminlarga xabar
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📞 *YANGI TELEFON*\n\n"
                     f"👤 *Ism:* {name}\n"
                     f"📞 *Telefon:* {phone}\n"
                     f"📅 *Vaqt:* {contact['date']}\n"
                     f"🆔 *User ID:* {user.id}\n"
                     f"🌐 *Til:* {lang}",
                parse_mode='Markdown'
            )
        except:
            pass
    
    context.user_data.pop('awaiting_phone', None)

# ==================== RATING FUNCTIONS ====================
async def start_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Baho berishni boshlash"""
    lang = db.get_user_lang(update.effective_user.id) or 'uz_lat'
    rating_text = t('rating_start_text', lang)
    
    # Custom rating keyboard with translations
    keyboard = []
    for i in range(1, 6):
        stars = "⭐" * i
        keyboard.append([InlineKeyboardButton(f"{stars} ({i}/5)", callback_data=f"rate_{i}")])
    
    keyboard.append([InlineKeyboardButton(t('cancel_btn', lang), callback_data="cancel_rate")])
    
    await update.message.reply_text(
        rating_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_rating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Baho berish callback"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db.get_user_lang(user.id) or 'uz_lat'
    
    if query.data == "cancel_rate":
        await query.edit_message_text(
            f"❌ *{t('cancel_btn', lang)}*."
        )
        return
    
    if query.data.startswith("rate_"):
        rating = int(query.data.split("_")[1])
        
        # Bahoni saqlash
        db.add_rating(user.id, rating)
        
        # Bahoga javob
        stars = "⭐" * rating
        empty_stars = "☆" * (5 - rating)
        
        await query.edit_message_text(
            f"{stars}{empty_stars}\n\n"
            f"{t('rating_success', lang, rating=rating, phone=ADMIN_PHONE)}",
            parse_mode='Markdown'
        )
        
        # Adminlarga xabar
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"⭐ *YANGI BAHO: {rating}/5*\n\n"
                         f"👤 *Foydalanuvchi:* {user.first_name}\n"
                         f"🆔 *User ID:* {user.id}\n"
                         f"📅 *Vaqt:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                         f"📊 *O'rtacha reyting:* {db.get_stats()['average_rating']}/5",
                    parse_mode='Markdown'
                )
            except:
                pass

# ==================== YANGI ADMIN FUNCTIONS ====================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin statistikasi"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    stats = db.get_stats()
    
    # Baholarni hisoblash
    ratings = db.get_all_ratings()
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for rating in ratings:
        r = rating.get("rating", 0)
        if r in rating_counts:
            rating_counts[r] += 1
    
    text = f"""
📊✨ *ADMIN STATISTIKASI* ✨📊

📈 *UMUMIY KO'RSATKICHLAR:*
📋 Arizalar: {stats['total_applications']} ta
📞 Kontaktlar: {stats['total_contacts']} ta
⭐ Baholar: {stats['total_ratings']} ta
🌟 O'rtacha baho: {stats['average_rating']}/5

📅 *BUGUNGI STATISTIKA:*
📥 Yangi arizalar: {stats['today_applications']} ta

📊 *HOLATLAR BO'YICHA:*
🆕 Yangi: {len([a for a in db.get_all_applications() if a.get('status') == 'yangi'])} ta
⏳ Jarayonda: {len([a for a in db.get_all_applications() if a.get('status') == 'jarayonda'])} ta
✅ Bajarilgan: {len([a for a in db.get_all_applications() if a.get('status') == 'completed'])} ta
❌ Bekor: {len([a for a in db.get_all_applications() if a.get('status') == 'cancelled'])} ta

📊 *BAHOLAR TAQSIMOTI:*
"""
    
    for stars in range(5, 0, -1):
        count = rating_counts[stars]
        percentage = (count / len(ratings) * 100) if ratings else 0
        text += f"⭐{'⭐' * (stars-1)} {stars}/5: {count} ta ({percentage:.1f}%)\n"
    
    text += f"\n🕒 *Oxirgi yangilanish:* {stats['last_updated']}"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_applications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Arizalar menyusi"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    await update.message.reply_text(
        "📋✨ *ARIZALAR BOSHQARUVI* ✨📋\n\nHolat bo'yicha tanlang:",
        parse_mode='Markdown',
        reply_markup=get_admin_applications_menu()
    )

async def admin_show_applications(update: Update, context: ContextTypes.DEFAULT_TYPE, status: str):
    """Holat bo'yicha arizalarni ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    if status == "all":
        applications = db.get_all_applications()
    else:
        applications = [app for app in db.get_all_applications() if app.get("status") == status]
    
    status_names = {
        "new": "🆕 Yangi arizalar",
        "progress": "⏳ Jarayonda",
        "completed": "✅ Bajarilgan",
        "cancelled": "❌ Bekor qilingan",
        "all": "📊 Barcha arizalar"
    }
    
    if not applications:
        await query.edit_message_text(
            f"{status_names.get(status, 'Arizalar')}\n\n📭 Hech qanday ariza topilmadi.",
            parse_mode='Markdown',
            reply_markup=get_admin_applications_menu()
        )
        return
    
    text = f"{status_names.get(status, 'Arizalar')} ({len(applications)} ta)\n\n"
    
    # So'nggi 10 ta ariza
    for app in applications[-10:]:
        status_emoji = {
            "yangi": "🆕",
            "jarayonda": "⏳",
            "completed": "✅",
            "cancelled": "❌"
        }.get(app.get("status", "yangi"), "📝")
        
        text += f"""
{status_emoji} *#{app['id']}* - {app['name']}
📞 {app['phone']}
🛠️ {app['service']}
📅 {app['date']}
{'='*30}
"""
    
    if len(applications) > 10:
        text += f"\n... va yana {len(applications) - 10} ta ariza"
    
    # Inline tugmalar
    keyboard = []
    for app in applications[-5:]:
        keyboard.append([
            InlineKeyboardButton(
                f"#{app['id']} - {app['name'][:15]}...", 
                callback_data=f"admin_app_detail_{app['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="admin_apps_all")])
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_application_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, app_id: int):
    """Ariza tafsilotlari"""
    query = update.callback_query
    await query.answer()
    
    applications = db.get_all_applications()
    app = next((a for a in applications if a["id"] == app_id), None)
    
    if not app:
        await query.edit_message_text("❌ Ariza topilmadi!")
        return
    
    status_emoji = {
        "yangi": "🆕",
        "jarayonda": "⏳",
        "completed": "✅",
        "cancelled": "❌"
    }.get(app.get("status", "yangi"), "📝")
    
    text = f"""
{status_emoji} *ARIZA #{app['id']}*

👤 *MIJOZ:*
• Ism: {app['name']}
• Telefon: {app['phone']}
• User ID: {app.get('user_id', 'N/A')}

🎯 *LOYIHA:*
• Xizmat: {app['service']}
• Holat: {app.get('status', 'yangi')}
• Vaqt: {app['date']}
• Yangilangan: {app.get('updated_at', 'N/A')}

📝 *XABAR:*
{app.get('message', 'Izoh yo\'q')}

👇 *AMALLAR:*
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=get_application_actions(app_id)
    )

async def admin_today_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bugungi arizalar"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    today_apps = db.get_today_applications()
    
    if not today_apps:
        await update.message.reply_text("📭 Bugun hali ariza yo'q")
        return
    
    text = f"📅 *BUGUNGI ARIZALAR* ({len(today_apps)} ta)\n\n"
    
    for app in today_apps:
        text += f"""
🆔 #{app['id']} - {app['name']}
📞 {app['phone']}
🛠️ {app['service']}
⏰ {app['date'][11:16]}
{'─'*25}
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kontaktlarni ko'rsatish"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    contacts = db.get_all_contacts()
    
    if not contacts:
        await update.message.reply_text("📭 Hozircha kontaktlar yo'q")
        return
    
    text = f"📞 *KONTAKTLAR* ({len(contacts)} ta)\n\n"
    
    for contact in contacts[-15:]:
        text += f"""
👤 {contact['name']}
📞 {contact['phone']}
📅 {contact['date']}
{'─'*25}
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_ratings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Baholarni ko'rsatish"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    ratings = db.get_all_ratings()
    
    if not ratings:
        await update.message.reply_text("⭐ Hozircha baholar yo'q")
        return
    
    stats = db.get_stats()
    
    text = f"""
⭐✨ *BAHOLAR* ✨⭐

📊 *UMUMIY:*
• Jami baholar: {stats['total_ratings']} ta
• O'rtacha baho: {stats['average_rating']}/5
• Mijoz mamnuniyati: {stats['average_rating'] * 20:.0f}%

📋 *SO'NGI 10 BAHO:*
"""
    
    for rating in ratings[-10:]:
        stars = "⭐" * rating['rating']
        empty_stars = "☆" * (5 - rating['rating'])
        text += f"""
{stars}{empty_stars} ({rating['rating']}/5)
👤 ID: {rating.get('user_id', 'Noma\'lum')}
📅 {rating['date']}
{'─'*20}
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export menyusi"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    await update.message.reply_text(
        "📤✨ *MA'LUMOTLAR EXPORTI* ✨📤\n\nEksport qilmoqchi bo'lgan ma'lumotlarni tanlang:",
        parse_mode='Markdown',
        reply_markup=get_admin_export_menu()
    )

async def admin_export_data(update: Update, context: ContextTypes.DEFAULT_TYPE, export_type: str):
    """Ma'lumotlarni export qilish"""
    query = update.callback_query
    await query.answer()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        if export_type == "apps_csv":
            filename = f"arizalar_{timestamp}.csv"
            applications = db.get_all_applications()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ism', 'Telefon', 'Xizmat', 'Holat', 'Sana', 'Xabar'])
                for app in applications:
                    writer.writerow([
                        app['id'],
                        app['name'],
                        app['phone'],
                        app['service'],
                        app.get('status', 'yangi'),
                        app['date'],
                        app.get('message', '')[:100]
                    ])
            
            await query.message.reply_document(
                document=open(filename, 'rb'),
                caption=f"📋 Arizalar ro'yxati ({len(applications)} ta)"
            )
            os.remove(filename)
        
        elif export_type == "contacts_csv":
            filename = f"kontaktlar_{timestamp}.csv"
            contacts = db.get_all_contacts()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ism', 'Telefon', 'Sana', 'Xabar'])
                for contact in contacts:
                    writer.writerow([
                        contact['id'],
                        contact['name'],
                        contact['phone'],
                        contact['date'],
                        contact.get('message', '')[:100]
                    ])
            
            await query.message.reply_document(
                document=open(filename, 'rb'),
                caption=f"📞 Kontaktlar ro'yxati ({len(contacts)} ta)"
            )
            os.remove(filename)
        
        elif export_type == "ratings_csv":
            filename = f"baholar_{timestamp}.csv"
            ratings = db.get_all_ratings()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'User ID', 'Baho', 'Sana', 'Izoh'])
                for rating in ratings:
                    writer.writerow([
                        rating['id'],
                        rating.get('user_id', ''),
                        rating['rating'],
                        rating['date'],
                        rating.get('feedback', '')
                    ])
            
            await query.message.reply_document(
                document=open(filename, 'rb'),
                caption=f"⭐ Baholar ro'yxati ({len(ratings)} ta)"
            )
            os.remove(filename)
        
        elif export_type == "stats_txt":
            filename = f"statistika_{timestamp}.txt"
            stats = db.get_stats()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write("NOVA.X STATISTIKA\n")
                f.write("="*50 + "\n\n")
                f.write(f"📅 Export vaqti: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
                f.write(f"📋 Jami arizalar: {stats['total_applications']} ta\n")
                f.write(f"📞 Jami kontaktlar: {stats['total_contacts']} ta\n")
                f.write(f"⭐ Jami baholar: {stats['total_ratings']} ta\n")
                f.write(f"🌟 O'rtacha baho: {stats['average_rating']}/5\n")
                f.write(f"📅 Bugungi arizalar: {stats['today_applications']} ta\n")
                f.write(f"🕒 Oxirgi yangilanish: {stats['last_updated']}\n")
            
            await query.message.reply_document(
                document=open(filename, 'rb'),
                caption=f"📊 Statistika hisoboti"
            )
            os.remove(filename)
        
        elif export_type == "all_zip":
            # ZIP fayl yaratish
            import zipfile
            
            zip_filename = f"nova_export_{timestamp}.zip"
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                # Arizalar
                apps_file = f"arizalar_{timestamp}.csv"
                applications = db.get_all_applications()
                with open(apps_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Ism', 'Telefon', 'Xizmat', 'Holat', 'Sana', 'Xabar'])
                    for app in applications:
                        writer.writerow([
                            app['id'],
                            app['name'],
                            app['phone'],
                            app['service'],
                            app.get('status', 'yangi'),
                            app['date'],
                            app.get('message', '')[:100]
                        ])
                zipf.write(apps_file)
                os.remove(apps_file)
                
                # Kontaktlar
                contacts_file = f"kontaktlar_{timestamp}.csv"
                contacts = db.get_all_contacts()
                with open(contacts_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Ism', 'Telefon', 'Sana', 'Xabar'])
                    for contact in contacts:
                        writer.writerow([
                            contact['id'],
                            contact['name'],
                            contact['phone'],
                            contact['date'],
                            contact.get('message', '')[:100]
                        ])
                zipf.write(contacts_file)
                os.remove(contacts_file)
                
                # Baholar
                ratings_file = f"baholar_{timestamp}.csv"
                ratings = db.get_all_ratings()
                with open(ratings_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'User ID', 'Baho', 'Sana', 'Izoh'])
                    for rating in ratings:
                        writer.writerow([
                            rating['id'],
                            rating.get('user_id', ''),
                            rating['rating'],
                            rating['date'],
                            rating.get('feedback', '')
                        ])
                zipf.write(ratings_file)
                os.remove(ratings_file)
                
                # Statistika
                stats_file = f"statistika_{timestamp}.txt"
                stats = db.get_stats()
                with open(stats_file, 'w', encoding='utf-8') as f:
                    f.write("="*50 + "\n")
                    f.write("NOVA.X STATISTIKA\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"📅 Export vaqti: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
                    for key, value in stats.items():
                        f.write(f"{key}: {value}\n")
                zipf.write(stats_file)
                os.remove(stats_file)
            
            await query.message.reply_document(
                document=open(zip_filename, 'rb'),
                caption="📁 Barcha ma'lumotlar"
            )
            os.remove(zip_filename)
        
        await query.message.reply_text(
            "✅ Export muvaffaqiyatli yakunlandi!",
            reply_markup=get_main_menu(is_admin=True)
        )
    
    except Exception as e:
        logger.error(f"Exportda xato: {e}")
        await query.message.reply_text(
            f"❌ Exportda xato: {str(e)}",
            reply_markup=get_main_menu(is_admin=True)
        )

async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalar"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    text = f"""
⚙️ *ADMIN PANEL SOZLAMALARI*

👑 *Adminlar:* {len(ADMIN_IDS)} ta
📊 *Ma'lumotlar bazasi:* {os.path.getsize('nova_x_database.json') if os.path.exists('nova_x_database.json') else 0} bayt
🕒 *Server vaqti:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
📈 *Bot holati:* 🟢 Faol

🔧 *SOZLAMALAR:*
• Bildirishnomalar: Yoqilgan
• Avtomatik backup: Yoqilgan
• Logging: INFO
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== CALLBACK HANDLER ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback query larni qayta ishlash"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    # Tilni sozlash
    if data.startswith("set_lang_"):
        lang_code = data.replace("set_lang_", "")
        db.set_user_lang(user.id, lang_code)
        
        try:
            await query.message.delete()
        except:
            pass
        
        # Start command xabarini yuborish
        await start_command(update, context)
        return

    # Admin callback lar
    if data.startswith("admin_"):
        if data == "admin_back":
            await admin_stats(update, context)
        
        elif data.startswith("admin_apps_"):
            status = data.split("_")[2]
            await admin_show_applications(update, context, status)
        
        elif data.startswith("admin_app_detail_"):
            app_id = int(data.split("_")[3])
            await admin_application_detail(update, context, app_id)
        
        elif data.startswith("app_complete_"):
            app_id = int(data.split("_")[2])
            db.update_application_status(app_id, "completed")
            await query.edit_message_text(
                f"✅ Ariza #{app_id} bajarildi deb belgilandi!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=f"admin_app_detail_{app_id}")]])
            )
        
        elif data.startswith("app_progress_"):
            app_id = int(data.split("_")[2])
            db.update_application_status(app_id, "jarayonda")
            await query.edit_message_text(
                f"⏳ Ariza #{app_id} jarayonda deb belgilandi!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=f"admin_app_detail_{app_id}")]])
            )
        
        elif data.startswith("app_cancel_"):
            app_id = int(data.split("_")[2])
            db.update_application_status(app_id, "cancelled")
            await query.edit_message_text(
                f"❌ Ariza #{app_id} bekor qilindi!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data=f"admin_app_detail_{app_id}")]])
            )
        
        elif data.startswith("app_contact_"):
            app_id = int(data.split("_")[2])
            apps = db.get_all_applications()
            app = next((a for a in apps if a["id"] == app_id), None)
            if app:
                await query.edit_message_text(
                    f"📞 *QO'NG'IROQ QILISH:*\n\n"
                    f"👤 Mijoz: {app['name']}\n"
                    f"📞 Telefon: {app['phone']}\n\n"
                    f"💬 Ish turi: {app['service']}",
                    parse_mode='Markdown'
                )
    
    # Export callback lar
    elif data.startswith("export_"):
        export_type = data.split("_")[1]
        await admin_export_data(update, context, export_type)
    
    # User rating callback
    elif data.startswith("rate_"):
        await handle_rating_callback(update, context)
    
    elif data.startswith("service_"):
        user_lang = db.get_user_lang(user.id) or 'uz_lat'
        service_names = {
            "website": t('service_website', user_lang),
            "mobile": t('service_mobile', user_lang),
            "design": t('service_design', user_lang),
            "seo": t('service_seo', user_lang),
            "hosting": t('service_hosting', user_lang),
            "other": t('service_other', user_lang)
        }
        service_type = data.split("_")[1]
        name = service_names.get(service_type, "Noma'lum xizmat")
        
        await query.message.reply_text(
            t('service_selected', user_lang, name=name),
            parse_mode='Markdown',
            reply_markup=get_main_menu(lang=user_lang)
        )
        # Arizani boshlash
        await start_application(update, context)

    elif data == "cancel_rate":
        user_lang = db.get_user_lang(user.id) or 'uz_lat'
        await query.edit_message_text(
            f"❌ *{t('cancel_btn', user_lang)}*"
        )

# ==================== MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xabarlarni qayta ishlash"""
    user = update.effective_user
    text = update.message.text
    lang = db.get_user_lang(user.id) or 'uz_lat'
    
    # Admin bo'lsa (admin panel tugmalari o'zgarmaydi)
    if user.id in ADMIN_IDS:
        if text == "📊 STATISTIKA":
            await admin_stats(update, context)
            return
        elif text == "📋 ARIZALAR":
            await admin_applications(update, context)
            return
        elif text == "📅 BUGUNGI":
            await admin_today_apps(update, context)
            return
        elif text == "📞 KONTAKTLAR":
            await admin_contacts(update, context)
            return
        elif text == "⭐ BAHOLAR":
            await admin_ratings(update, context)
            return
        elif text == "📤 EXPORT":
            await admin_export(update, context)
            return
        elif text == "⚙️ SOZLAMALAR":
            await admin_settings(update, context)
            return
        elif text == "🏠 ASOSIY MENYU":
            await start_command(update, context)
            return

    # User tugmalarini tekshirish (barcha tillarda)
    def check_btn(key):
        for l in TRANSLATIONS:
            if TRANSLATIONS[l].get(key) == text:
                return True
        return False

    if check_btn('menu_about'):
        await about_command(update, context)
    elif check_btn('menu_services'):
        await services_command(update, context)
    elif check_btn('menu_prices'):
        await prices_command(update, context)
    elif check_btn('menu_apply'):
        await start_application(update, context)
    elif check_btn('menu_phone'):
        await start_phone_contact(update, context)
    elif check_btn('menu_rate'):
        await start_rating(update, context)
    elif check_btn('menu_contact'):
        await contact_command(update, context)
    elif check_btn('menu_help'):
        await help_command(update, context)
    elif check_btn('menu_main'):
        await start_command(update, context)
    elif check_btn('menu_lang'):
        await update.message.reply_text(
            t('select_lang', lang),
            reply_markup=get_language_keyboard()
        )
    else:
        # Agar ariza yoki telefon kutilayotgan bo'lsa
        if context.user_data.get('awaiting_application'):
            await handle_application(update, context)
        elif context.user_data.get('awaiting_phone'):
            await handle_phone_contact(update, context)
        else:
            # Boshqa har qanday xabar uchun
            await update.message.reply_text(
                "🤖 *...*\n\n"
                f"{t('menu_help', lang)}: {ADMIN_PHONE}",
                parse_mode='Markdown',
                reply_markup=get_main_menu(lang=lang)

            )

# ==================== MAIN FUNCTION ====================
def main():
    """Asosiy funksiya"""
    print(f"📞 Admin telefon: {ADMIN_PHONE}")
    print(f"💬 Telegram: {ADMIN_TELEGRAM}")
    print(f"👑 Adminlar soni: {len(ADMIN_IDS)}")
    print("=" * 60)
    print("✅ Bot konfiguratsiyasi muvaffaqiyatli!")
    
    # Botni yaratish
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    print("📱 Telegramda botni oching va /start buyrug'ini yuboring")
    print("=" * 60)
    
    # Render uchun web serverni ishga tushirish
    keep_alive()
    
    # Botni ishga tushirish
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()