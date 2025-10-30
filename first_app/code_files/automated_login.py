from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyotp import TOTP
import json
import time
from datetime import datetime
from pathlib import Path
from first_app.constants import *
# Import your config
from first_app.zerodha_config import *


class ZerodhaAutoLogin:
    """
    Automated login class for Zerodha Kite platform.
    Handles login, TOTP, and token generation/storage.
    """
    
    def __init__(self, 
                 api_key, 
                 api_secret, 
                 user_id, 
                 password, 
                 totp_key, 
                 headless=False):
        """
        Initialize ZerodhaAutoLogin
        
        Args:
            api_key (str): Zerodha API key
            api_secret (str): Zerodha API secret
            user_id (str): Zerodha user ID
            password (str): Zerodha password
            totp_key (str): TOTP secret key
            token_file (str): Path to save tokens (default: zerodha_tokens.json)
            headless (bool): Run browser in headless mode (default: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        self.password = password
        self.totp_key = totp_key
        self.token_file = zerodha_token_file
        self.headless = headless
        
        # Initialize KiteConnect
        self.kite = KiteConnect(api_key=self.api_key)
        
        # Initialize driver as None
        self.driver = None
        self.request_token = None
        self.access_token = None
    
    def _setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        print("Chrome driver initialized")
    
    def _generate_totp(self):
        """Generate TOTP code"""
        totp_obj = TOTP(self.totp_key)
        return totp_obj.now()
    
    def _enter_credentials(self, wait):
        """Enter user ID and password"""
        # Enter User ID
        userid_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        userid_field.clear()
        userid_field.send_keys(self.user_id)
        print("User ID entered")
        
        # Enter Password
        password_field = self.driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(self.password)
        print("Password entered")
        
        # Click Login button
        login_button = self.driver.find_element(By.CSS_SELECTOR, "button.button-orange.wide")
        login_button.click()
        print("Login button clicked")
    
    def _enter_totp(self, wait):
        """Enter TOTP code"""
        # Wait for TOTP page
        print("Waiting for TOTP page...")
        totp_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        
        # Generate and enter TOTP
        totp = self._generate_totp()
        print(f"Generated TOTP: {totp}")
        
        totp_field.clear()
        totp_field.send_keys(totp)
        print("TOTP entered")
        
        # Wait for auto-submission or submit manually
        time.sleep(2)
        
        try:
            if "request_token" in self.driver.current_url:
                print("TOTP auto-submitted successfully")
            else:
                totp_field.send_keys(Keys.RETURN)
                print("TOTP submitted using Enter key")
        except Exception as e:
            print(f"TOTP submission: {e}")
    
    def _extract_request_token(self):
        """Extract request token from URL"""
        print("Waiting for login to complete...")
        time.sleep(3)
        
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        if "request_token" in current_url:
            self.request_token = current_url.split("request_token=")[1].split("&")[0]
            print(f"Request Token: {self.request_token}")
            return True
        else:
            print("Error: Request token not found in URL")
            return False
    
    def _generate_access_token(self):
        """Generate access token from request token"""
        try:
            data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            self.access_token = data['access_token']
            print(f"Access Token: {self.access_token}")
            return True
        except Exception as e:
            print(f"Error generating access token: {e}")
            return False
    
    def _save_tokens(self):
        """Save tokens to JSON file"""
        tokens_data = {
            "request_token": self.request_token,
            "access_token": self.access_token,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(tokens_data, f, indent=4)
        
        print(f"\n✅ Tokens saved to {self.token_file}")
        return tokens_data
    
    def login(self):
        """
        Execute complete login flow
        
        Returns:
            dict: Dictionary containing tokens and metadata, or None if failed
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Get login URL
            login_url = self.kite.login_url()
            print(f"Login URL: {login_url}\n")
            
            # Open login page
            self.driver.get(login_url)
            print("Login page opened")
            
            # Wait object
            wait = WebDriverWait(self.driver, 10)
            
            # Step 1: Enter credentials
            self._enter_credentials(wait)
            
            # Step 2: Enter TOTP
            self._enter_totp(wait)
            
            # Step 3: Extract request token
            if not self._extract_request_token():
                return None
            
            # Step 4: Generate access token
            if not self._generate_access_token():
                return None
            
            # Step 5: Save tokens
            tokens_data = self._save_tokens()
            
            print("\n✅ Login completed successfully!")
            return tokens_data
            
        except Exception as e:
            print(f"\n❌ Login failed: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            # Close browser
            if self.driver:
                self.driver.quit()
                print("\nBrowser closed.")
    
    def set_access_token(self):
        """Set access token to kite instance"""
        if self.access_token:
            self.kite.set_access_token(self.access_token)
            print("Access token set to KiteConnect instance")
        else:
            print("No access token available")
    
    @staticmethod
    def load_tokens():
        """
        Load tokens from JSON file
        
        Args:
            token_file (str): Path to token file
            
        Returns:
            dict: Token data or None if file doesn't exist
        """
        token_path = Path(zerodha_token_file)
        if token_path.exists():
            with open(zerodha_token_file, 'r') as f:
                return json.load(f)
        else:
            print(f"Token file {zerodha_token_file} not found")
            return None
    
    def get_kite_instance(self):
        """
        Get KiteConnect instance with access token set
        
        Returns:
            KiteConnect: Authenticated KiteConnect instance
        """
        if not self.access_token:
            print("Access token not available. Please login first.")
            return None
        
        self.kite.set_access_token(self.access_token)
        return self.kite


# Example usage
if __name__ == "__main__":

    # Initialize login handler
    zerodha = ZerodhaAutoLogin(
        api_key=api_key,
        api_secret=api_secret,
        user_id=user_id,
        password=password,
        totp_key=totp_key,
        headless=True  # Set to True to run without browser window
    )
    
    # Perform login
    tokens = zerodha.login()
    
    if tokens:
        print("\n" + "="*50)
        print("Login Successful!")
        print("="*50)
        print(json.dumps(tokens, indent=2))
        
        # # Get authenticated kite instance
        # kite = zerodha.get_kite_instance()
        
        # # Now you can use kite for trading
        # # profile = kite.profile()
        # # print(profile)
