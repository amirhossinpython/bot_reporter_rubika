import random
import asyncio
import os
import sys
import  subprocess
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    from rubpy import Client, filters
    from rubpy.enums import ReportType
    from rubpy.types import Updates
except ImportError :
    install("rubpy")
    
bot = Client(name='reporting')
info = """
# توضیحات ربات

این ربات به کاربران اجازه می‌دهد تا گزارشی از یک کاربر دیگر یا محتوای خاصی را ارسال کنند. فرآیند ارسال گزارش به صورت مرحله به مرحله انجام می‌شود. کاربر باید ابتدا یک شناسه ارسال کند و سپس نوع تخلف را مشخص کند. در نهایت ربات گزارشات را ارسال می‌کند.

## مراحل عملکرد ربات

1. **شروع مکالمه با ربات**:
   - هنگامی که کاربر دستور /start را ارسال می‌کند، ربات شروع به کار می‌کند.
   - ربات از کاربر می‌خواهد که شناسه (object_guid) مربوط به فرد یا محتوایی که قصد گزارش آن را دارد، وارد کند.

2. **دریافت شناسه و انتخاب نوع تخلف**:
   - پس از دریافت شناسه، ربات از کاربر می‌خواهد که نوع تخلف را انتخاب کند. کاربر می‌تواند یکی از 7 گزینه زیر را انتخاب کند:
     1. محتوای مستهجن
     2. خشونت
     3. اسپم
     4. کودک‌آزاری
     5. نقض حق‌نشر
     6. فیشینگ
     7. سایر
     8. انتخاب تصادفی (راندم)

3. **توضیح تخلف "سایر"**:
   - اگر کاربر گزینه "سایر" یا "تصادفی" را انتخاب کند، ربات از او می‌خواهد توضیح مختصری در مورد نوع تخلف وارد کند.

4. **دریافت تعداد گزارش‌ها**:
   - بعد از انتخاب نوع تخلف، ربات از کاربر درخواست می‌کند که تعداد گزارش‌هایی که می‌خواهد ارسال شود را وارد کند.

5. **ارسال گزارش‌ها**:
   - پس از دریافت تعداد گزارش‌ها، ربات به تعداد درخواست‌شده گزارش‌ها را ارسال می‌کند.
   - پس از موفقیت در ارسال، به کاربر اطلاع داده می‌شود.

6. **حذف اطلاعات کاربر**:
   - پس از ارسال گزارش، تمامی داده‌های مربوط به کاربر از حافظه ربات پاک می‌شود تا اطلاعات کاربر ذخیره نشود.

7. **حذف دستی اطلاعات با دستور /delete**:
   - کاربر می‌تواند در هر مرحله با ارسال دستور /delete تمامی اطلاعات خود را از حافظه ربات پاک کرده و فرآیند را از ابتدا شروع کند.
"""

with open("robot_description.txt", "w", encoding="utf-8") as file:
    file.write(info)

# متغیرهای ذخیره‌سازی موقت برای اطلاعات کاربران
user_data = {}

# تابع شروع گفتگو
@bot.on_message_updates(filters.is_private)
async def start(message: Updates):
    user_id = message.author_guid
    
    if message.text == "/help":
        await message.reply(info)
        return

    # حذف داده‌ها در صورت دستور /delete
    if message.text == "/delete":
        if user_id in user_data:
            user_data.pop(user_id)
        await message.reply("داده‌های شما حذف شد. لطفاً دوباره دستور /start را وارد کنید.")
        return

    # مرحله اول: شروع گفتگو و درخواست شناسه
    if message.text == "/start":
        await message.reply("سلام! لطفاً شناسه مورد نظر برای گزارش را ارسال کنید:")
        user_data[user_id] = {"step": "waiting_for_guid"}  # ذخیره مرحله

    # مرحله دوم: دریافت شناسه و درخواست نوع تخلف
    elif user_data.get(user_id, {}).get("step") == "waiting_for_guid":
        object_guid = message.text
        user_data[user_id]["object_guid"] = object_guid  # ذخیره شناسه
        await message.reply("نوع تخلف را انتخاب کنید:\n1. محتوای مستهجن\n2. خشونت\n3. اسپم\n4. کودک‌آزاری\n5. نقض حق‌نشر\n6. فیشینگ\n7. سایر\n8. تصادفی")
        user_data[user_id]["step"] = "waiting_for_report_type"  # تغییر مرحله

    # مرحله سوم: دریافت نوع تخلف و درخواست توضیحات برای تخلف "سایر" (در صورت انتخاب)
    elif user_data.get(user_id, {}).get("step") == "waiting_for_report_type":
        report_type = message.text
        report_type_enum = None
        
        if report_type == '1':
            report_type_enum = ReportType.PORNOGRAPHY
            report_name = "محتوای مستهجن"
        elif report_type == '2':
            report_type_enum = ReportType.VIOLENCE
            report_name = "خشونت"
        elif report_type == '3':
            report_type_enum = ReportType.SPAM
            report_name = "اسپم"
        elif report_type == '4':
            report_type_enum = ReportType.CHILD_ABUSE
            report_name = "کودک‌آزاری"
        elif report_type == '5':
            report_type_enum = ReportType.COPYRIGHT
            report_name = "نقض حق‌نشر"
        elif report_type == '6':
            report_type_enum = ReportType.FISHING
            report_name = "فیشینگ"
        elif report_type == '7':
            report_type_enum = ReportType.OTHER
            report_name = "سایر"
            await message.reply("لطفاً توضیح مربوط به تخلف 'سایر' را وارد کنید:")
            user_data[user_id]["step"] = "waiting_for_other_description"  # تغییر مرحله به دریافت توضیح
            user_data[user_id]["report_type"] = report_type_enum  # ذخیره نوع تخلف
            return  # صبر تا دریافت توضیحات
        elif report_type == '8':  # انتخاب تصادفی
            random_types = [ReportType.PORNOGRAPHY, ReportType.VIOLENCE, ReportType.SPAM, ReportType.CHILD_ABUSE, ReportType.COPYRIGHT, ReportType.FISHING, ReportType.OTHER]
            report_type_enum = random.choice(random_types)  # انتخاب تصادفی
            report_name = "تصادفی"
        else:
            await message.reply("لطفاً یک عدد معتبر (1 تا 8) انتخاب کنید.")
            return
        
        user_data[user_id]["report_type"] = report_type_enum  # ذخیره نوع تخلف
        await message.reply(f"تخلف انتخاب‌شده: {report_name}. لطفاً تعداد گزارش‌هایی که می‌خواهید ارسال شود را وارد کنید:")
        user_data[user_id]["step"] = "waiting_for_report_count"  # تغییر مرحله

    # مرحله چهارم: دریافت توضیحات برای تخلف "سایر"
    elif user_data.get(user_id, {}).get("step") == "waiting_for_other_description":
        other_description = message.text
        user_data[user_id]["description"] = other_description  # ذخیره توضیح "سایر"
        await message.reply(f"توضیحات ثبت شد: {other_description}. حالا تعداد گزارش‌هایی که می‌خواهید ارسال شود را وارد کنید:")
        user_data[user_id]["step"] = "waiting_for_report_count"  # تغییر مرحله

    # مرحله پنجم: دریافت تعداد گزارش و ارسال نهایی
    elif user_data.get(user_id, {}).get("step") == "waiting_for_report_count":
        try:
            report_count = int(message.text)
            if report_count <= 0:
                raise ValueError("عدد معتبر وارد کنید.")
        except ValueError:
            await message.reply("لطفاً یک عدد معتبر برای تعداد گزارش‌ها وارد کنید.")
            return
        
        # ارسال گزارشات به تعداد درخواست‌شده با فاصله زمانی 2 ثانیه
        object_guid = user_data[user_id]["object_guid"]
        report_type_enum = user_data[user_id]["report_type"]
        description = user_data[user_id].get("description", None)  # بررسی توضیحات "سایر"
        
        try:
            for _ in range(report_count):
                await bot.report_object(object_guid, report_type_enum, description)
                rep = random.uniform(1, 8.5)
                
                await asyncio.sleep(rep)  # فاصله زمانی 2 ثانیه‌ای بین هر گزارش
            await message.reply(f"گزارش با موفقیت ارسال شد. تعداد گزارش‌ها: {report_count}")
        except Exception as e:
            await message.reply(f"خطا در ارسال گزارش: {str(e)}")
        
        # پاک کردن اطلاعات کاربر پس از اتمام
        user_data.pop(user_id)

if __name__ == '__main__':
    bot.run()
