import random
import re
import sqlite3
import time
import requests
from colorama import Fore, init, Style
from datetime import datetime

init(autoreset=True)

class AdvancedInstagramUsernameGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.init_db()
        
    def init_db(self):
        """تهيئة قاعدة البيانات لتخزين النتائج"""
        self.conn = sqlite3.connect('usernames.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usernames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                status TEXT,
                length INTEGER,
                pattern TEXT,
                checked_at TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def generate_username(self, length=3, pattern=None):
        """
        توليد اسم مستخدم حسب الطول والنمط المطلوب
        الأنماط المدعومة:
        - 'LDD': حرفين + رقمين (مثال: ab12)
        - 'LLL': أحرف فقط (مثال: abc)
        - 'DDD': أرقام فقط (مثال: 123)
        - None:  خليط عشوائي
        """
        chars = 'abcdefghijklmnopqrstuvwxyz'
        digits = '0123456789'
        underscore = '_'
        dot = '.'
        
        if pattern:
            username = []
            for p in pattern:
                if p == 'L':
                    username.append(random.choice(chars))
                elif p == 'D':
                    username.append(random.choice(digits))
                elif p == '_':
                    username.append(underscore)
                elif p == '.':
                    username.append(dot)
                else:
                    username.append(random.choice(chars + digits + underscore + dot))
            return ''.join(username)[:length]
        else:
            all_chars = chars + digits + underscore + dot
            return ''.join(random.choice(all_chars) for _ in range(length))
    
    def is_valid_username(self, username):
        """التحقق من توافق اسم المستخدم مع شروط إنستجرام"""
        if not re.match(r'^[a-zA-Z0-9._]{3,30}$', username):
            return False
        if username.startswith(('.', '_')):
            return False
        if '__' in username or '..' in username or '._' in username or '_.' in username:
            return False
        return True
    
    def check_username_availability(self, username):
        """فحص توفر اسم المستخدم مع إدارة معدل الطلبات"""
        if not self.is_valid_username(username):
            return {'status': 'invalid', 'message': 'Invalid username format'}
            
        # التحقق من قاعدة البيانات أولاً
        self.cursor.execute('SELECT status FROM usernames WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        if result:
            return {'status': result[0], 'cached': True}
        
        # إذا لم يكن في قاعدة البيانات، نتحقق من إنستجرام
        url = f"https://www.instagram.com/{username}/"
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                status = 'available'
            elif response.status_code == 200:
                status = 'taken'
            else:
                status = 'unknown'
                
            # تخزين النتيجة في قاعدة البيانات
            self.cursor.execute('''
                INSERT INTO usernames (username, status, checked_at)
                VALUES (?, ?, ?)
            ''', (username, status, datetime.now()))
            self.conn.commit()
            
            return {'status': status, 'cached': False}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def batch_generate(self, count=10, length=3, pattern=None, delay=2):
        """توليد مجموعة من أسماء المستخدمين"""
        valid_usernames = []
        attempts = 0
        max_attempts = count * 3  # حد أقصى للمحاولات
        
        print(f"\n{Fore.YELLOW}Generating {count} usernames (length: {length}, pattern: {pattern or 'random'})...")
        
        while len(valid_usernames) < count and attempts < max_attempts:
            attempts += 1
            username = self.generate_username(length, pattern)
            
            if not self.is_valid_username(username):
                continue
                
            result = self.check_username_availability(username)
            
            display_status = {
                'available': f"{Fore.GREEN}✓ Available",
                'taken': f"{Fore.RED}✗ Taken",
                'invalid': f"{Fore.YELLOW}⚠ Invalid",
                'unknown': f"{Fore.BLUE}? Unknown",
                'error': f"{Fore.MAGENTA}⚠ Error"
            }.get(result['status'], f"{Fore.WHITE}? Unknown")
            
            print(f"{Fore.CYAN}{attempts}. {Fore.WHITE}{username.ljust(length+2)} {display_status}")
            
            if result['status'] == 'available':
                valid_usernames.append(username)
            
            time.sleep(delay)
        
        return valid_usernames
    
    def get_stats(self):
        """الحصول على إحصاءات من قاعدة البيانات"""
        self.cursor.execute('SELECT COUNT(*) FROM usernames')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM usernames WHERE status = "available"')
        available = self.cursor.fetchone()[0]
        
        return {'total_checked': total, 'available': available}
    
    def close(self):
        """إغلاق اتصال قاعدة البيانات"""
        self.conn.close()

def show_banner():
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Advanced Instagram Username Generator ===")
    print(f"{Fore.BLUE}Generate available Instagram usernames with custom patterns")
    print(f"{Fore.MAGENTA}Developed for educational purposes only{Style.RESET_ALL}\n")

def main_menu():
    print(f"\n{Fore.YELLOW}Main Menu:")
    print(f"{Fore.GREEN}1. Generate random usernames")
    print(f"{Fore.GREEN}2. Generate usernames with specific pattern")
    print(f"{Fore.GREEN}3. View database statistics")
    print(f"{Fore.GREEN}4. Exit")
    
    choice = input(f"\n{Fore.WHITE}Enter your choice (1-4): ")
    return choice

def pattern_help():
    print(f"\n{Fore.YELLOW}Pattern Guide:")
    print(f"{Fore.CYAN}L = Letter (a-z)")
    print(f"{Fore.CYAN}D = Digit (0-9)")
    print(f"{Fore.CYAN}_ = Underscore")
    print(f"{Fore.CYAN}. = Dot")
    print(f"\n{Fore.WHITE}Example: 'LLDD' generates 2 letters + 2 digits (ab12)")

def main():
    generator = AdvancedInstagramUsernameGenerator()
    show_banner()
    
    try:
        while True:
            choice = main_menu()
            
            if choice == '1':
                length = int(input(f"{Fore.WHITE}Enter username length (3-6): "))
                length = max(3, min(6, length))
                count = int(input(f"{Fore.WHITE}How many available usernames to find? (1-50): "))
                count = max(1, min(50, count))
                
                usernames = generator.batch_generate(count=count, length=length)
                
                if usernames:
                    print(f"\n{Fore.GREEN}Found {len(usernames)} available usernames:")
                    for i, uname in enumerate(usernames, 1):
                        print(f"{i}. {Fore.CYAN}{uname}")
                else:
                    print(f"{Fore.RED}No available usernames found with current settings.")
                
            elif choice == '2':
                pattern_help()
                pattern = input(f"\n{Fore.WHITE}Enter pattern (e.g. 'LLDD'): ").upper()
                count = int(input(f"{Fore.WHITE}How many available usernames to find? (1-50): "))
                count = max(1, min(50, count))
                
                usernames = generator.batch_generate(count=count, length=len(pattern), pattern=pattern)
                
                if usernames:
                    print(f"\n{Fore.GREEN}Found {len(usernames)} available usernames:")
                    for i, uname in enumerate(usernames, 1):
                        print(f"{i}. {Fore.CYAN}{uname}")
                else:
                    print(f"{Fore.RED}No available usernames found with current pattern.")
                
            elif choice == '3':
                stats = generator.get_stats()
                print(f"\n{Fore.YELLOW}Database Statistics:")
                print(f"{Fore.CYAN}Total usernames checked: {stats['total_checked']}")
                print(f"{Fore.CYAN}Available usernames found: {stats['available']}")
                
            elif choice == '4':
                print(f"{Fore.GREEN}Exiting...")
                break
                
            else:
                print(f"{Fore.RED}Invalid choice, please try again.")
                
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Process interrupted by user.")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}")
    finally:
        generator.close()

if __name__ == "__main__":
    main()
