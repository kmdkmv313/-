import random
import requests
import time
from colorama import Fore, init

init(autoreset=True)  # تهيئة colorama للألوان في الكونسول

class InstagramUsernameGenerator:
    def __init__(self):
        self.used_combinations = set()
        self.generated_count = 0
        self.available_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def generate_3char_combination(self):
        """توليد مجموعة أحرف ثلاثية عشوائية"""
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789_.'
        while True:
            combo = ''.join(random.choices(chars, k=3))
            if combo not in self.used_combinations:
                self.used_combinations.add(combo)
                return combo

    def check_username_availability(self, username):
        """فحص توفر اسم المستخدم على إنستجرام"""
        url = f"https://www.instagram.com/{username}/"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 404:
                return True  # اسم المستخدم متاح
            elif response.status_code == 200:
                return False  # اسم المستخدم محجوز
            else:
                return None  # حالة غير معروفة
        except Exception as e:
            print(f"{Fore.RED}Error checking {username}: {e}")
            return None

    def generate_and_check(self, count=10, delay=2):
        """توليد وفحص أسماء المستخدمين"""
        available_usernames = []
        
        print(f"{Fore.YELLOW}Starting Instagram username generator...\n")
        
        while self.available_count < count:
            username = self.generate_3char_combination()
            self.generated_count += 1
            
            print(f"{Fore.WHITE}Checking: {Fore.CYAN}{username}", end=' ')
            
            is_available = self.check_username_availability(username)
            
            if is_available is True:
                self.available_count += 1
                available_usernames.append(username)
                print(f"{Fore.GREEN}✓ Available")
                print(f"{Fore.MAGENTA}Found: {self.available_count}/{count} | Total checked: {self.generated_count}")
            elif is_available is False:
                print(f"{Fore.RED}✗ Taken")
            else:
                print(f"{Fore.YELLOW}? Unknown")
            
            if self.generated_count % 5 == 0 and self.available_count < count:
                print(f"{Fore.BLUE}Waiting {delay} seconds to avoid rate limiting...")
                time.sleep(delay)
        
        return available_usernames

    def save_to_file(self, usernames, filename="available_usernames.txt"):
        """حفظ الأسماء المتاحة في ملف"""
        with open(filename, 'w') as f:
            for username in usernames:
                f.write(f"{username}\n")
        print(f"\n{Fore.GREEN}Saved {len(usernames)} available usernames to {filename}")

def main():
    generator = InstagramUsernameGenerator()
    
    print(f"{Fore.CYAN}Instagram 3-Character Username Generator")
    print(f"{Fore.CYAN}=====================================\n")
    
    try:
        count = int(input(f"{Fore.WHITE}How many available usernames do you want to find? (1-50): "))
        count = max(1, min(50, count))  # التأكد من أن العدد بين 1 و50
        
        available = generator.generate_and_check(count)
        
        if available:
            print(f"\n{Fore.GREEN}Found {len(available)} available usernames:")
            for i, username in enumerate(available, 1):
                print(f"{i}. {Fore.CYAN}{username}")
            
            save = input(f"\n{Fore.WHITE}Save to file? (y/n): ").lower()
            if save == 'y':
                generator.save_to_file(available)
        
        print(f"\n{Fore.MAGENTA}Total generated: {generator.generated_count}")
        print(f"{Fore.MAGENTA}Total available: {generator.available_count}")
        
    except ValueError:
        print(f"{Fore.RED}Please enter a valid number!")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Process interrupted by user.")
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}")

if __name__ == "__main__":
    main()
