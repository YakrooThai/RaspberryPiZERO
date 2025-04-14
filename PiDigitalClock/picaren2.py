
import tkinter as tk
from tkinter import font, ttk
import datetime
import calendar
from PIL import Image, ImageTk, ImageDraw, UnidentifiedImageError
import os
import requests
import glob
import time

if os.environ.get('DISPLAY', '') == '':
    os.environ.__setitem__('DISPLAY', ':0')

class VerticalMagicMirror:
    def __init__(self, root):
        self.root = root
        self.current_language = 'EN'  # เริ่มต้นเป็นภาษาอังกฤษ
        self.image_files = []  # เก็บรายการไฟล์รูปภาพ
        self.current_image_index = 0  # ดัชนีของรูปภาพปัจจุบัน
        self.configure_window()
        self.create_styles()
        self.load_image_files()  # โหลดรายการไฟล์รูปภาพ
        self.create_widgets()
        self.start_updates()

    def configure_window(self):
        self.root.title("Pi Digital Clock 7.84\" Display")
        self.root.geometry("480x1920")
        self.root.configure(bg='#1a1a1a')
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def create_styles(self):
        self.style = ttk.Style()
        self.style.configure('Calendar.TFrame', 
                           background='#2d2d2d', 
                           borderwidth=2, 
                           relief='flat')
        self.style.configure('Day.TLabel', 
                           font=('Roboto', 14),
                           foreground='#ffffff',
                           background='#2d2d2d',
                           padding=5)
        self.style.map('CurrentDay.TLabel',
                     background=[('active', '#3d5afe')],
                     foreground=[('active', 'white')])

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Clock Section
        self.clock_label = tk.Label(main_frame, 
                                  font=('Roboto', 64),
                                  fg='#ffffff', 
                                  bg='#1a1a1a')
        self.clock_label.pack(pady=10)

        self.date_label = tk.Label(main_frame, 
                                 font=('Roboto', 28),
                                 fg='#b3b3b3', 
                                 bg='#1a1a1a')
        self.date_label.pack()

        # Calendar Section
        self.calendar_frame = ttk.Frame(main_frame, style='Calendar.TFrame')
        self.calendar_frame.pack(pady=15, ipadx=10, ipady=10)

        # Image Section
        self.image_label = tk.Label(main_frame, bg='#1a1a1a')
        self.image_label.pack(pady=10, fill='both', expand=True)

        # Static Text
        self.static_text_label = tk.Label(main_frame,
                                        text="Pi Digital Clock + Python + Tkinter",
                                        font=('Roboto', 16),
                                        fg='#00ffff',
                                        bg='#1a1a1a')
        self.static_text_label.pack(pady=5)

        # Greeting Section
        self.greeting_label = tk.Label(main_frame,
                                     font=('Roboto', 24),
                                     fg='#FFFFFF',
                                     bg='#1a1a1a')
        self.greeting_label.pack(pady=10)

        # AQI Section (เพิ่มส่วนแสดง AQI, PM2.5, อุณหภูมิ, ความชื้น)
        self.aqi_label = tk.Label(main_frame,
                                 font=('Roboto', 16),
                                 fg='#FFFFFF',
                                 bg='#1a1a1a',
                                 justify='left',
                                 anchor='w')
        self.aqi_label.pack(pady=10, fill='x')

    def start_updates(self):
        self.update_clock()
        self.update_calendar()
        self.load_image()  # เริ่มต้นโหลดรูปภาพแรก
        self.update_greeting()
        self.update_aqi()  # เริ่มต้นอัพเดท AQI
        self.root.after(3600000, self.update_calendar)  # อัพเดทปฏิทินทุกชั่วโมง
        self.root.after(10000, self.next_image)  # เปลี่ยนรูปภาพทุก 10 วินาที
        self.root.after(300000, self.update_aqi)  # อัพเดท AQI ทุก 5 นาที

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%d %B %Y\n%A"))
        self.root.after(1000, self.update_clock)

    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        today = datetime.datetime.now()
        cal = calendar.monthcalendar(today.year, today.month)

        # Calendar Headers
        headers = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        for col, day in enumerate(headers):
            ttk.Label(self.calendar_frame, 
                    text=day,
                    style='Day.TLabel',
                    foreground='#808080').grid(row=0, column=col, sticky='nsew')

        # Calendar Days
        for row, week in enumerate(cal, 1):
            for col, day in enumerate(week):
                if day == 0:
                    continue
                
                is_today = (day == today.day)
                day_label = ttk.Label(self.calendar_frame,
                                    text=str(day),
                                    style='CurrentDay.TLabel' if is_today else 'Day.TLabel')
                
                if is_today:
                    day_label.configure(background='#3d5afe', 
                                      relief='ridge',
                                      font=('Roboto', 14, 'bold'))
                
                day_label.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)

        # Grid Configuration
        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1, minsize=50)
        for row in range(len(cal)+1):
            self.calendar_frame.rowconfigure(row, weight=1, minsize=40)

    def update_greeting(self):
        hour = datetime.datetime.now().hour
        greeting = self.get_greeting(hour)
        self.greeting_label.config(text=greeting)
        self.root.after(60000, self.update_greeting)

    def get_greeting(self, hour):
        if 5 <= hour < 12: return 'Good Morning!'
        elif 12 <= hour < 18: return 'Good Afternoon!'
        elif 18 <= hour < 22: return 'Good Evening!'
        else: return 'Good Night!'

    def get_translation(self, key):
        translations = {
            'EN': {
                'city_warning': 'City not found:',
                'updated': 'Updated:'
            },
            'TH': {
                'city_warning': 'ไม่พบเมือง:',
                'updated': 'อัพเดทเมื่อ:'
            }
        }
        return translations[self.current_language][key]

    def get_aqi_data(self, city):
        try:
            api_token = "11cf67867af17cc6d9c186e389f249b807b9f7a7"  # ใส่ API token ของคุณที่นี่
            url = f"https://api.waqi.info/feed/{city}/?token={api_token}"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['status'] == 'ok':
                aqi = data['data']['aqi']
                pm25 = data['data']['iaqi']['pm25']['v'] if 'pm25' in data['data']['iaqi'] else 'N/A'
                city_name = data['data']['city']['name']
                
                # ดึงข้อมูลอุณหภูมิและความชื้น
                temp = data['data']['iaqi']['t']['v'] if 't' in data['data']['iaqi'] else 'N/A'
                humidity = data['data']['iaqi']['h']['v'] if 'h' in data['data']['iaqi'] else 'N/A'
                
                aqi_levels = {
                    (0, 50): ("Good", '#00E400') if self.current_language == 'EN' else ("ดี", '#00E400'),
                    (51, 100): ("Moderate", '#FFFF00') if self.current_language == 'EN' else ("ปานกลาง", '#FFFF00'),
                    (101, 150): ("Unhealthy for Sensitive Groups", '#FF7E00') if self.current_language == 'EN' else ("มีผลต่อกลุ่มเสี่ยง", '#FF7E00'),
                    (151, 200): ("Unhealthy", '#FF0000') if self.current_language == 'EN' else ("ไม่ดีต่อสุขภาพ", '#FF0000'),
                    (201, 300): ("Very Unhealthy", '#8F3F97') if self.current_language == 'EN' else ("อันตราย", '#8F3F97'),
                    (301, float('inf')): ("Hazardous", '#7E0023') if self.current_language == 'EN' else ("อันตรายมาก", '#7E0023')
                }
                
                level, color = next(
                    (v for k, v in aqi_levels.items() if k[0] <= aqi <= k[1]),
                    ("Unknown", '#FFFFFF') if self.current_language == 'EN' else ("ไม่ทราบ", '#FFFFFF')
                )
                
                if self.current_language == 'TH':
                    return "\n".join([
                        f"{city_name}",
                        f"AQI: {aqi} ({level})",
                        f"PM2.5: {pm25} μg/m³",
                        f"อุณหภูมิ: {temp} °C",
                        f"ความชื้น: {humidity} %",
                        f"{self.get_translation('updated')} {data['data']['time']['s']}"
                    ]), color
                else:
                    return "\n".join([
                        f"{city_name}",
                        f"AQI: {aqi} ({level})",
                        f"PM2.5: {pm25} μg/m³",
                        f"Temperature: {temp} °C",
                        f"Humidity: {humidity} %",
                        f"{self.get_translation('updated')} {data['data']['time']['s']}"
                    ]), color
            
            return f"{self.get_translation('city_warning')} {city}", '#FFFFFF'
            
        except Exception as e:
            print(f"Error: {e}")
            return "Connection Error", '#FFFFFF'

    def update_aqi(self):
        city = "bangkok"  # เปลี่ยนเมืองได้ตามต้องการ
        aqi_text, aqi_color = self.get_aqi_data(city)
        self.aqi_label.config(text=aqi_text, fg=aqi_color)
        self.root.after(300000, self.update_aqi)  # อัพเดททุก 5 นาที

    def load_image_files(self):
        # โหลดรายการไฟล์รูปภาพจากโฟลเดอร์ "pic"
        self.image_files = glob.glob("pic/*.png") + glob.glob("pic/*.jpg") + glob.glob("pic/*.jpeg")
        if not self.image_files:
            print("No images found in 'pic' folder")
            self.image_files = ["imageb.png"]  # ใช้รูปภาพเริ่มต้นถ้าไม่พบ

    def load_image(self):
        try:
            if not self.image_files:
                raise FileNotFoundError("No images available")

            image_path = self.image_files[self.current_image_index]
            image = Image.open(image_path)
            
            # ปรับขนาดรูปภาพให้เหมาะสมกับจอ (ถ้าต้องการ)
            max_width = 440  # ความกว้างสูงสุด (480 - padding)
            max_height = 300  # ความสูงสูงสุด (กำหนดตามต้องการ)
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # เพิ่มมุมโค้ง
            mask = Image.new('L', image.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0,0), image.size], radius=20, fill=255)
            
            image.putalpha(mask)
            self.photo_image = ImageTk.PhotoImage(image)
            
            self.image_label.config(image=self.photo_image)
            self.image_label.image = self.photo_image

        except FileNotFoundError:
            self.show_image_error("❌ ไม่พบไฟล์รูปภาพ", '#ff4444')
        except UnidentifiedImageError:
            self.show_image_error("⚠️ ไฟล์รูปภาพไม่ถูกต้อง", '#ff9900')
        except Exception as e:
            self.show_image_error(f"⚠️ ข้อผิดพลาด: {str(e)}", '#ffd700')

    def next_image(self):
        # เปลี่ยนไปรูปภาพถัดไป
        if self.image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.load_image()
        self.root.after(10000, self.next_image)  # เปลี่ยนรูปภาพทุก 10 วินาที

    def show_image_error(self, message, color):
        print(message)
        self.image_label.config(
            text=message,
            fg=color,
            font=('Roboto', 16, 'bold'),
            compound='center'
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = VerticalMagicMirror(root)
    root.mainloop()
