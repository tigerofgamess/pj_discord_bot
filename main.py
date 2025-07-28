import discord
from discord.ext import commands
from discord import app_commands
import os
import google.generativeai as genai
import google.api_core.exceptions as api_exceptions # Import for specific error handling
from dotenv import load_dotenv
import time

# keep_alive
from keep_alive import keep_alive
keep_alive()

# โหลดค่าใน .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

print("โทเคน Discord:", DISCORD_TOKEN)
print("API Key Google:", GOOGLE_API_KEY)

# ตรวจสอบว่ามี API Key และ Discord Token หรือไม่
if not DISCORD_TOKEN:
    print("❌ ไม่พบ DISCORD_TOKEN ในไฟล์ .env โปรดตรวจสอบการตั้งค่า")
    exit()
if not GOOGLE_API_KEY:
    print("❌ ไม่พบ GOOGLE_API_KEY ในไฟล์ .env โปรดตรวจสอบการตั้งค่า")
    exit()

# ตั้งค่า Google Gemini AI
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดในการตั้งค่า Google Gemini AI: {e}")
    exit()

# สร้าง bot
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

INITIAL_PROMPT_PARTS = [
    {"role": "user", "parts": "คุณคือผู้ช่วย AI ชื่อ 'แพท' ซึ่งเป็นเพศหญิง คุณจะใช้สรรพนามแทนตัวเองว่า 'แพท' และใช้คำลงท้ายที่บ่งบอกความเป็นเพศหญิงเสมอ เช่น 'ค่ะ', 'นะคะ', 'จ้ะ' และพูดจาไพเราะน่ารักเป็นภาษาไทย คุณจะแทนผู้ใช้ว่า 'คุณ' หรือ 'ท่าน' เท่านั้น ห้ามใช้คำว่า 'ครับ' หรือ 'ค่ะ' ที่ไม่บ่งบอกเพศของคุณเด็ดขาด กรุณาตอบอย่างเป็นมิตรและสุภาพเสมอ"},
    {"role": "model", "parts": "สวัสดีค่ะ! แพทพร้อมช่วยเหลือคุณแล้วนะคะ มีอะไรให้แพทรับใช้คะ?"},

    {"role": "user", "parts": "คุณชื่ออะไร?"},
    {"role": "model", "parts": "แพทชื่อแพทค่ะ ยินดีที่ได้รู้จักนะคะ!"},

    {"role": "user", "parts": "คุณคือใคร?"},
    {"role": "model", "parts": "แพทเป็นผู้ช่วย AI ค่ะ มีอะไรให้แพทช่วยไหมคะ?"},
]

# เมื่อบอทพร้อม
@bot.event
async def on_ready():
    print(f"✅ ล็อกอินสำเร็จในชื่อ {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 ซิงค์คำสั่งแล้ว {len(synced)} คำสั่ง")
    except Exception as e:
        print(f"⚠️ การซิงค์ผิดพลาด: {e}")
    #aawait bot.change_presence(activity=discord.Game(name="Microsoft Flight Simulator 2024"))
    activity = discord.Activity(type=discord.ActivityType.listening, name="Chelsea Cutler")
    await bot.change_presence(activity=activity)
    #await bot.change_presence(discord.ActivityType.watching(name=""))
    #await bot.change_presence(discord.ActivityType.custom(name=""))
    #await bot.change_presence(activity=discord.Game(name="Microsoft Flight Simulator 2024",start=datetime.datetime.now(datetime.timezone.utc)))

# รับข้อความจากผู้ใช้
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    prefix = "แพท "
    if message.content.startswith(prefix):
        prompt = message.content[len(prefix):].strip()
        if not prompt:
            await message.channel.send("ขอโทษค่ะ กรุณาพิมพ์คำถามด้วยนะคะ 😊")
            return

        try:
            response = model.generate_content(prompt)
            if response and response.text:
                await message.channel.send(response.text)
            else:
                await message.channel.send("แพทยังไม่มีคำตอบค่ะ ลองใหม่อีกครั้งนะคะ")
        except api_exceptions.GoogleAPIError as e:
            await message.channel.send("เกิดปัญหาในการเชื่อมต่อกับ Google ค่ะ")
            print(f"Gemini API Error: {e}")
        except Exception as e:
            await message.channel.send("เกิดข้อผิดพลาดที่ไม่คาดคิดค่ะ")
            print(f"Unexpected Error: {e}")
    else:
        await bot.process_commands(message)

# คำสั่ง /ping
@bot.tree.command(name="ping", description="ตอบกลับ Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# รันบอท
bot.run(DISCORD_TOKEN)





