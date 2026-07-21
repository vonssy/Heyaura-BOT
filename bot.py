from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from http.cookies import SimpleCookie
from base64 import urlsafe_b64decode
from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
from eth_utils import to_hex
from datetime import datetime, timedelta, timezone
from colorama import *
import asyncio, textwrap, random, string, time, json, sys, re, os

class heyAura:
    def __init__(self) -> None:
        self.API = {
            "hub": "https://hub.heyaura.com",
            "ai": "https://backend.heyaura.com"
        }

        self.USE_PROXY = False
        self.ROTATE_PROXY = False
        
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.accounts = {}
        self.props = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}heyAura {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.txt"
        try:
            with open(filename, 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            return accounts
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
            return None

    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def get_next_run_time(self, anchor_minute=1):
        now = datetime.now(timezone.utc)
        today_target = now.replace(hour=0, minute=anchor_minute, second=0, microsecond=0)

        if today_target > now:
            return today_target
        else:
            return today_target + timedelta(days=1)
    
    def extract_cookies(self, idx: int, response: object):
        existing = self.accounts[idx].get("cookies", {})
        
        jar = SimpleCookie()
        
        for k, v in existing.items():
            jar[k] = v
        
        for h in response.headers.getall("Set-Cookie", []):
            jar.load(h)
        
        self.accounts[idx]["cookies"] = {
            k: m.value for k, m in jar.items()
        }

        return self.accounts[idx]["cookies"]
    
    def initialize_headers(self, idx: int, type: str = "hub"):
        if type == "ai":
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Origin": "https://app.heyaura.com",
                "Pragma": "no-cache",
                "Referer": "https://app.heyaura.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": self.accounts[idx]["user_agent"]
            }

        else:
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Origin": "https://hub.heyaura.com",
                "Pragma": "no-cache",
                "Referer": "https://hub.heyaura.com/community",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": self.accounts[idx]["user_agent"]
            }
            

        return headers.copy()
    
    def generate_evm_wallet(self, idx: int, private_key: str):
        try:
            keypair = Account.from_key(private_key)
            address = keypair.address
            self.accounts[idx]["keypair"] = keypair
            self.accounts[idx]["address"] = address
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Generate EVM Wallet Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    def generate_hub_payload(self, idx: int, csrf_token: str):
        try:
            keypair = self.accounts[idx]["keypair"]
            address = self.accounts[idx]["address"]

            dt_now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
            issued_at = dt_now.replace("+00:00", "Z")

            raw_message = json.dumps({
                "domain": "hub.heyaura.com",
                "address": address,
                "statement": "Sign in to the app. Powered by Snag Solutions.",
                "uri": "https://hub.heyaura.com",
                "version": "1",
                "chainId": 1,
                "nonce": csrf_token,
                "issuedAt": issued_at
            }, separators=(',', ':'))

            message = (
                "hub.heyaura.com wants you to sign in with your Ethereum account:\n"
                f"{address}\n\n"
                "Sign in to the app. Powered by Snag Solutions.\n\n"
                "URI: https://hub.heyaura.com\n"
                "Version: 1\n"
                "Chain ID: 1\n"
                f"Nonce: {csrf_token}\n"
                f"Issued At: {issued_at}"
            )

            encoded_message = encode_defunct(text=message)
            signed_message = keypair.sign_message(encoded_message)
            signature = to_hex(signed_message.signature)

            payload = {
                "message": raw_message,
                "accessToken": signature,
                "signature": signature,
                "walletConnectorName": "MetaMask",
                "walletAddress": address,
                "redirect": "false",
                "callbackUrl": "/protected",
                "chainType": "evm",
                "walletProvider": "undefined",
                "csrfToken": csrf_token,
                "json": "true"
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    def generate_ai_payload(self, idx: int, auth_message: str):
        try:
            keypair = self.accounts[idx]["keypair"]
            encoded_message = encode_typed_data(full_message=auth_message)
            signed_message = keypair.sign_message(encoded_message)
            signature = to_hex(signed_message.signature)

            payload = {
                "authMsg": auth_message,
                "signature": signature,
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")

    def generate_prompt(self) -> str:
        subjects = {
            "wallet": [
                "wallet balance",
                "wallet address",
                "connected wallet",
                "wallet activity",
                "wallet security",
                "seed phrase safety",
                "hardware wallet status",
                "multi-sig wallet setup",
                "existing token approvals",
                "spending allowance",
            ],
            "network": [
                "Ethereum mainnet",
                "Arbitrum",
                "Optimism",
                "Base",
                "Polygon",
                "BNB Chain",
                "current gas fees",
                "network congestion",
                "chain reorg risk",
                "RPC endpoint status",
            ],
            "web3": [
                "smart contract details",
                "DeFi protocol activity",
                "DEX liquidity pool position",
                "yield farming position",
                "staking position",
                "lending protocol position",
                "governance proposal status",
                "smart contract risk",
                "protocol TVL",
            ],
            "portfolio": [
                "total portfolio value",
                "asset allocation",
                "portfolio performance",
                "profit and loss",
                "portfolio risk exposure",
                "diversification",
                "idle assets",
                "portfolio history",
            ],
            "asset": [
                "ERC-20 token holdings",
                "stablecoin balance",
                "native token balance",
                "NFT collection",
                "token price",
                "token supply",
                "dust token balance",
                "token contract address",
                "airdrop token eligibility",
                "bridged asset status",
            ],
            "transaction": [
                "pending transaction status",
                "transaction fees",
                "transaction history",
                "failed transaction details",
                "transaction confirmation status",
            ],
        }

        predicates = [
            "What is my {subject}?",
            "Show me my {subject}",
            "Check my {subject} right now",
            "Explain how {subject} works",
            "Is my {subject} at risk?",
            "Compare my {subject} across chains",
            "Alert me if {subject} changes significantly",
            "Summarize my {subject} in simple terms",
            "Why did my {subject} change recently?",
            "What's the safest way to think about {subject}?",
            "Track {subject} over the last 7 days",
            "What should I know about {subject}?",
        ]

        general_subjects = [
            "Explain {subject} to a beginner",
            "What's the current status of {subject}?",
            "Any risks I should know about {subject}?",
        ]
        
        category = random.choice(list(subjects.keys()))
        subject = random.choice(subjects[category])

        if category in ("network", "web3"):
            predicate_pool = predicates + general_subjects
        else:
            predicate_pool = predicates

        predicate = random.choice(predicate_pool)
        return predicate.format(subject=subject)
    
    def generate_chat_session_name(self, prompt: str):
        now = datetime.now().strftime("%d/%m/%y %H:%M")
        return prompt[:24] + " - " + now
    
    def generate_random_string(self, length: int = 16) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))
    
    def generate_submit_prompt_payload(self, idx: int, prompt: str, session_id: str):
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        return {
            "prompt": prompt,
            "userPrompt": prompt,
            "threadId": session_id,
            "sessionId": session_id,
            "resourceId": self.accounts[idx]["address"],
            "messages": [
                {
                    "parts": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                    "id": self.generate_random_string(),
                    "role": "user",
                    "metadata": {
                        "createdAt": timestamp
                    }
                }
            ]
        }

    async def parse_event_stream(self, response):
        event_type = None
        data_lines = []

        async for raw_line in response.content:
            line = raw_line.decode("utf-8").rstrip("\r\n")

            if line == "":
                if event_type is not None:
                    yield event_type, "\n".join(data_lines)
                event_type = None
                data_lines = []
                continue

            if line.startswith("event:"):
                event_type = line[len("event:"):].strip()
            elif line.startswith("data:"):
                data_lines.append(line[len("data:"):].lstrip())

    def format_ai_response(self, response: dict, width: int = 100, indent: str = "    "):
        if not response or "actions" not in response:
            return f"{Fore.RED+Style.BRIGHT}No response content{Style.RESET_ALL}"

        lines = []

        for action in response["actions"]:
            content = action.get("content", "")
            suggestions = action.get("suggestions", [])

            lines.append(self.format_content_block(content, width=width, indent=indent))

            if suggestions:
                lines.append("")
                lines.append(f"{indent}{Fore.MAGENTA+Style.BRIGHT}Suggestions:{Style.RESET_ALL}")
                for s in suggestions:
                    lines.append(f"{indent}  {Fore.CYAN}→{Style.RESET_ALL} {s}")

        return "\n".join(lines)

    def format_content_block(self, content: str, width: int, indent: str) -> str:
        paragraphs = content.split("\n\n")
        rendered = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            for line in para.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.startswith("- "):
                    bullet_text = self.apply_bold(line[2:])
                    bullet = f"{indent}{Fore.YELLOW}•{Style.RESET_ALL} {bullet_text}"
                    wrapped = textwrap.fill(
                        bullet,
                        width=width,
                        subsequent_indent=indent + "  ",
                        break_long_words=False,
                        replace_whitespace=False,
                    )
                else:
                    text = self.apply_bold(line)
                    wrapped = textwrap.fill(
                        text,
                        width=width,
                        initial_indent=indent,
                        subsequent_indent=indent,
                        break_long_words=False,
                        replace_whitespace=False,
                    )
                rendered.append(wrapped)

            rendered.append("")

        return "\n".join(rendered).rstrip()

    def apply_bold(self, text: str) -> str:
        return re.sub(
            r"\*\*(.+?)\*\*",
            lambda m: f"{Fore.GREEN+Style.BRIGHT}{m.group(1)}{Style.RESET_ALL}",
            text,
        )
        
    def decode_token(self, idx: int, type: str = "access"):
        try:
            if type == "refresh":
                token = self.accounts[idx]["refresh_token"]
            else:
                token = self.accounts[idx]["access_token"]

            header, payload, signature = token.split(".")
            decoded_payload = urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            exp_time = parsed_payload["exp"]
            
            return exp_time
        except Exception as e:
            return None

    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")
    
    async def ensure_ok(self, response):
        if response.status >= 400:
            error_text = await response.text()
            raise Exception(f"HTTP {response.status}: {error_text}")
    
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"

        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, proxy=proxy, proxy_auth=proxy_auth) as response:
                    await self.ensure_ok(response)
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def websites_props(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/props/websites"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx].get("cookies", {})

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(
                        url=url, headers=headers, cookies=cookies, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        self.extract_cookies(idx, response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Web Props {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def auth_csrf(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/auth/csrf"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx].get("cookies", {})

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(
                        url=url, headers=headers, cookies=cookies, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        self.extract_cookies(idx, response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Csrf Token {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def auth_credentials(self, idx: int, csrf_token: str, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/auth/callback/credentials"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                headers["Content-Type"] = "application/json"
                headers["X-Requested-With"] = "XMLHttpRequest"
                cookies = self.accounts[idx].get("cookies", {})
                payload = self.generate_hub_payload(idx, csrf_token)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, cookies=cookies, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        self.extract_cookies(idx, response)
                        return True
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Login   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Session Token {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None

    async def loyality_accounts(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/loyalty/accounts"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx].get("cookies", {})
                params = {
                    "websiteId": self.props["web_id"], 
                    "organizationId": self.props["org_id"], 
                    "walletAddress": self.accounts[idx]["address"]
                }
                
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(
                        url=url, headers=headers, cookies=cookies, params=params, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Points {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None

    async def loyality_rules(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/loyalty/rules"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx].get("cookies", {})
                params = {
                    "limit": "100",
                    "websiteId": self.props["web_id"], 
                    "organizationId": self.props["org_id"], 
                    "excludeHidden": "true",
                    "excludeExpired": "true",
                    "isActive": "true"
                }
                
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(
                        url=url, headers=headers, cookies=cookies, params=params, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Rules Id {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def complete_checkin(self, idx: int, rules_id: str, proxy_url=None, retries=5):
        url = f"{self.API['hub']}/api/loyalty/rules/{rules_id}/complete"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx)
                headers["Content-Type"] = "application/json"
                cookies = self.accounts[idx].get("cookies", {})
                
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, cookies=cookies, json={}, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        result = await response.json()

                        if response.status == 400:
                            err_msg = result.get("message")
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} {err_msg} {Style.RESET_ALL}"
                            )
                            return None
                        
                        await self.ensure_ok(response)
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def login_message(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['ai']}/auth/login-msg"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx, "ai")
                headers["Content-Type"] = "application/json"
                payload = {
                    "wallet": self.accounts[idx]["address"],
                    "chainId": 1
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Auth Message {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def login_verify(self, idx: int, auth_message: str, proxy_url=None, retries=5):
        url = f"{self.API['ai']}/auth/login-verify"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx, "ai")
                headers["Content-Type"] = "application/json"
                payload = self.generate_ai_payload(idx, auth_message)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Authenticating {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def refresh_token(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.API['ai']}/auth/refresh-token"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx, "ai")
                headers["Content-Type"] = "application/json"
                payload = {
                    "refreshToken": self.accounts[idx]["refresh_token"]
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Refreshing Token {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def chat_sessions(self, idx: int, prompt: str, proxy_url=None, retries=5):
        url = f"{self.API['ai']}/chat-sessions"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx, "ai")
                headers["Authorization"] = f"Bearer {self.accounts[idx]['access_token']}"
                headers["Content-Type"] = "application/json"
                payload = {
                    "name": self.generate_chat_session_name(prompt)
                }

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Session :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Preparing Chat {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def submit_prompt(self, idx: int, prompt: str, session_id: str, proxy_url=None, retries=5):
        url = f"{self.API['ai']}/prompt"
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                headers = self.initialize_headers(idx, "ai")
                headers["Authorization"] = f"Bearer {self.accounts[idx]['access_token']}"
                headers["Content-Type"] = "application/json"
                payload = self.generate_submit_prompt_payload(idx, prompt, session_id)

                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(
                        url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth
                    ) as response:
                        await self.ensure_ok(response)
                        result = None
                        async for event_type, data in self.parse_event_stream(response):
                            if not data:
                                continue
                            if event_type == "done":
                                result = json.loads(data)

                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Response:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Submit Prompt {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, idx: int, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(idx)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.display_proxy(proxy_url)} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True

            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(idx)
                await asyncio.sleep(1)
                continue

            return False
    
    async def process_user_login(self, idx: int, proxy_url=None):
        is_valid = await self.process_check_connection(idx, proxy_url)
        if not is_valid: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(idx)

        props = await self.websites_props(idx, proxy_url)
        if not props: return False

        web_id = props.get("websiteId")
        org_id = props.get("organizationId")

        if not web_id or not org_id:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Web/Org Id Not Found {Style.RESET_ALL}"
            )
            return False
        
        self.props["web_id"] = web_id
        self.props["org_id"] = org_id

        auth_csrf = await self.auth_csrf(idx, proxy_url)
        if not auth_csrf: return False

        csrf_token = auth_csrf.get("csrfToken")

        credentials = await self.auth_credentials(idx, csrf_token, proxy_url)
        if not credentials: return False

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
        )

        return True
    
    async def process_authenticating(self, idx: int, proxy_url=None):
        if not self.accounts[idx].get("access_token"):
            message = await self.login_message(idx, proxy_url)
            if not message: return False

            auth_message = message.get("authMsg")

            verify = await self.login_verify(idx, auth_message, proxy_url)
            if not verify: return False

            self.accounts[idx]["access_token"] = verify.get("accessToken")
            self.accounts[idx]["refresh_token"] = verify.get("refreshToken")

            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Authenticated {Style.RESET_ALL}"
            )

        else:
            access_exp_time = self.decode_token(idx)
            if int(time.time()) > access_exp_time:

                refresh_exp_time = self.decode_token(idx, "refresh")
                if int(time.time()) > refresh_exp_time:

                    message = await self.login_message(idx, proxy_url)
                    if not message: return False

                    auth_message = message.get("authMsg")

                    verify = await self.login_verify(idx, auth_message, proxy_url)
                    if not verify: return False

                    self.accounts[idx]["access_token"] = verify.get("accessToken")
                    self.accounts[idx]["refresh_token"] = verify.get("refreshToken")

                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Authenticated {Style.RESET_ALL}"
                    )

                else:
                    refresh = await self.refresh_token(idx, proxy_url)
                    if not refresh: return False

                    self.accounts[idx]["access_token"] = refresh.get("accessToken")
                    self.accounts[idx]["refresh_token"] = refresh.get("refreshToken")

                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Status  :{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Token Refreshed {Style.RESET_ALL}"
                    )

        return True

    async def process_accounts(self, idx: int, proxy_url=None):
        logined = await self.process_user_login(idx, proxy_url)
        if not logined: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(idx)

        accounts = await self.loyality_accounts(idx, proxy_url)
        if accounts:
            accounts_data = accounts.get("data") or []

            amount = (
                accounts_data[0].get("amount", 0)
                if accounts_data and isinstance(accounts_data[0], dict)
                else 0
            )

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {amount} Points {Style.RESET_ALL}"
            )

        rules = await self.loyality_rules(idx, proxy_url)
        if rules:
            rules_data = rules.get("data") or []

            rules_id = next(
                (r.get("id") for r in rules_data if r.get("type") == "check_in" and r.get("claimType") == "manual"),
                None,
            )

            if rules_id:
                if await self.complete_checkin(idx, rules_id, proxy_url):
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Rules Id Not Found {Style.RESET_ALL}"
                )
        
        self.log(f"{Fore.CYAN+Style.BRIGHT}AI Chat :{Style.RESET_ALL}")

        if await self.process_authenticating(idx, proxy_url):
            prompt = self.generate_prompt()
            self.log(
                f"{Fore.BLUE + Style.BRIGHT}   Prompt  :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {prompt} {Style.RESET_ALL}"
            )

            session = await self.chat_sessions(idx, prompt, proxy_url)
            if session:
                session_id = session.get("_id")

                self.log(
                    f"{Fore.BLUE+Style.BRIGHT}   Session :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {session_id} {Style.RESET_ALL}"
                )

                response = await self.submit_prompt(idx, prompt, session_id, proxy_url)
                if response:
                    self.log(
                        f"{Fore.BLUE + Style.BRIGHT}   Response:{Style.RESET_ALL}\n"
                        f"{Fore.WHITE + Style.BRIGHT}{self.format_ai_response(response)}{Style.RESET_ALL}"
                    )

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                print(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}") 
                return

            self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if self.USE_PROXY: self.load_proxies()

                separator = "=" * 25
                for idx, private_key in enumerate(accounts, start=1):
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    if idx not in self.accounts:
                        self.accounts[idx] = {
                            "user_agent": random.choice(self.USER_AGENTS)
                        }

                    wallet = self.generate_evm_wallet(idx, private_key)
                    if not wallet: continue

                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Address :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(self.accounts[idx]['address'])} {Style.RESET_ALL}"
                    )
                        
                    await self.process_accounts(idx)
                    await asyncio.sleep(random.uniform(2.0, 3.0))

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*60)
                
                next_run = self.get_next_run_time(anchor_minute=1)

                while True:
                    now = datetime.now(timezone.utc)
                    remaining = (next_run - now).total_seconds()

                    if remaining <= 0:
                        break

                    formatted_time = self.format_seconds(remaining)

                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = heyAura()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] heyAura - BOT{Style.RESET_ALL}                                       "                              
        )
        sys.exit(0)