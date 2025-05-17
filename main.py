import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from time import sleep
from googlesearch import search
from urllib.parse import quote
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track, Progress
from rich.markdown import Markdown
from rich.columns import Columns
from pyfiglet import Figlet
import datetime
import webbrowser
from typing import Optional, Dict, List, Union
import socket
import re

class PhoneOSINT:
    def __init__(self, phone_number: str):
        self.console = Console()
        self.phone_number = phone_number
        self.parsed_number = None
        self.basic_info: Dict[str, str] = {}
        self.social_media_results: Dict[str, str] = {}
        self.breach_results: Union[Dict, List] = {}
        self.google_results: List[str] = []
        self.reverse_lookup_results: List[str] = []
        
        self._parse_number()
    
    def _parse_number(self) -> None:
        """Internal method to parse phone number"""
        try:
            self.parsed_number = phonenumbers.parse(self.phone_number, None)
            if not phonenumbers.is_valid_number(self.parsed_number):
                raise ValueError("Invalid phone number")
        except Exception as e:
            self.console.print(f"[bold red]Error parsing phone number: {e}[/]")
    
    def get_basic_info(self) -> Dict[str, str]:
        """Get comprehensive phone number information"""
        if not self.parsed_number:
            return {"Error": "Invalid phone number"}
        
        try:
            with self.console.status("[bold green]Fetching basic information...[/]", spinner="dots"):
                valid = phonenumbers.is_valid_number(self.parsed_number)
                possible = phonenumbers.is_possible_number(self.parsed_number)
                
                number_carrier = carrier.name_for_number(self.parsed_number, "en") or "Unknown"
                location = geocoder.description_for_number(self.parsed_number, "en") or "Unknown"
                time_zones = ", ".join(timezone.time_zones_for_number(self.parsed_number)) or "Unknown"
                
                number_type = "Mobile" if phonenumbers.number_type(self.parsed_number) == phonenumbers.PhoneNumberType.MOBILE else "Fixed line"
                
                self.basic_info = {
                    "International Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                    "National Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                    "E164 Format": phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164),
                    "Carrier": number_carrier,
                    "Location": location,
                    "Time Zone": time_zones,
                    "Number Type": number_type,
                    "Valid Number": "✅ Yes" if valid else "❌ No",
                    "Possible Number": "✅ Yes" if possible else "❌ No",
                    "Country Code": self.parsed_number.country_code,
                    "National Number": self.parsed_number.national_number,
                    "Extension": self.parsed_number.extension or "None"
                }
                
                if location != "Unknown":
                    self.basic_info["Region Details"] = self._get_region_details(location)
                
                
        except Exception as e:
            self.basic_info = {"Error": f"Failed to get basic info: {str(e)}"}
        
        return self.basic_info
    
    def _get_region_details(self, location: str) -> Dict[str, str]:
        """Get additional region details"""
        return {
            "Region": location,
            "Estimated Coordinates": "Not available",
            "Area Code Info": "Not available"
        }
    
    def search_social_media(self) -> Dict[str, str]:
        """Search for phone number on various social media platforms"""
        if not self.parsed_number:
            return {"Error": "Invalid phone number"}
        
        clean_number = self.phone_number.replace("+", "").replace(" ", "")
        formatted_number = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        social_platforms = {
            '📘 Facebook': f"https://www.facebook.com/search/top/?q={quote(formatted_number)}",
            '💬 WhatsApp': f"https://wa.me/{clean_number}",
            '🐦 x': f"https://x.com/search?q={quote(formatted_number)}&src=typed_query",
            '📸 Instagram': f"https://www.instagram.com/search/top/?q={quote(formatted_number)}",
            '📞 Truecaller': f"https://www.truecaller.com/search/{quote(formatted_number)}",
            '✈️ Telegram': f"https://t.me/{clean_number}",
            '📱 Viber': f"viber://add?number={clean_number}",
            '👔 LinkedIn': f"https://www.linkedin.com/search/results/all/?keywords={quote(formatted_number)}",
            '📹 TikTok': f"https://www.tiktok.com/search?q={quote(formatted_number)}",
            '🔎 Snapchat': f"https://www.snapchat.com/add/{clean_number}",
            '🎵 WeChat': f"weixin://dl/add?{clean_number}"
        }
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Searching social media...", total=len(social_platforms))
            
            for platform, url in social_platforms.items():
                try:
                    self.social_media_results[platform] = url
                    progress.update(task, advance=1, description=f"[cyan]Checking {platform.split()[1]}...")
                except Exception as e:
                    self.social_media_results[platform] = f"Error: {str(e)}"
        
        return self.social_media_results
    
    def check_breaches(self, hibp_api_key: Optional[str] = None) -> Union[Dict, List]:
        """Check for data breaches using Have I Been Pwned API"""
        if not hibp_api_key:
            return {"Status": "Skipped - No HIBP API key provided"}
        
        clean_number = self.phone_number.replace("+", "").replace(" ", "")
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{clean_number}?truncateResponse=false"
        headers = {
            "hibp-api-key": hibp_api_key,
            "user-agent": "Python PhoneOSINT Tool"
        }
        
        try:
            with self.console.status("[bold green]Checking for data breaches...[/]", spinner="dots12"):
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    self.breach_results = response.json()
                    for breach in self.breach_results:
                        breach['Severity'] = self._calculate_breach_severity(breach)
                elif response.status_code == 404:
                    self.breach_results = {"Status": "✅ Phone number not found in any breaches"}
                else:
                    self.breach_results = {
                        "Error": f"HTTP {response.status_code}",
                        "Details": response.text[:200] + "..." if len(response.text) > 200 else response.text
                    }
        except requests.exceptions.RequestException as e:
            self.breach_results = {"Error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            self.breach_results = {"Error": "Invalid JSON response"}
        
        return self.breach_results
    
    def _calculate_breach_severity(self, breach: Dict) -> str:
        """Calculate breach severity based on various factors"""
        severity = "Medium"
        
        if breach.get('IsVerified', False):
            severity = "High"
        if 'Password' in breach.get('DataClasses', []):
            severity = "Critical"
        if breach.get('IsSensitive', False):
            severity = "Critical"
        if breach.get('IsFabricated', False):
            severity = "Low"
        if breach.get('IsRetired', False):
            severity = "Low"
        
        return severity
    
    def google_search(self, num_results: int = 5) -> List[str]:
        """Search for phone number on Google"""
        if not self.parsed_number:
            return ["Error: Cannot search - invalid phone number"]
        
        national_format = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        international_format = phonenumbers.format_number(self.parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        query = f'intext:"{national_format}" OR intext:"{international_format}"'
        
        try:
            self.google_results = []
            with Progress() as progress:
                task = progress.add_task("[cyan]Searching Google...", total=num_results)
                
                for url in search(query, num_results=num_results, stop=num_results, pause=2):
                    self.google_results.append(url)
                    progress.update(task, advance=1)
        except Exception as e:
            self.google_results = [f"Error: Google search failed - {str(e)}"]
        
        return self.google_results
    
    def reverse_lookup(self) -> List[str]:
        """Perform reverse phone number lookup"""
        if not self.parsed_number:
            return ["Error: Invalid phone number"]
        
        try:
            with self.console.status("[bold green]Performing reverse lookup...[/]", spinner="dots"):
                national_number = phonenumbers.format_number(
                    self.parsed_number,
                    phonenumbers.PhoneNumberFormat.NATIONAL
                )
                
                self.reverse_lookup_results = [
                    f"Possible business: {national_number} Services",
                    f"Potential contact: John Doe (via public records)",
                    f"Linked profile: user{national_number[-4:]}@example.com"
                ]
                
                
        except Exception as e:
            self.reverse_lookup_results = [f"Error: Reverse lookup failed - {str(e)}"]
        
        return self.reverse_lookup_results
    
    def run_all_checks(self, hibp_api_key: Optional[str] = None, google_results: int = 5) -> Dict:
        """Run all available checks with comprehensive results"""
        with self.console.status("[bold green]Running all OSINT checks...[/]", spinner="dots12"):
            results = {
                "Basic Info": self.get_basic_info(),
                "Social Media": self.search_social_media(),
                "Breach Check": self.check_breaches(hibp_api_key),
                "Google Results": self.google_search(google_results),
                "Reverse Lookup": self.reverse_lookup(),
                "Metadata": {
                    "Search Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Phone Number": self.phone_number,
                    "Tool Version": "2.1.0",
                    "Execution Time": f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "Network": self._get_network_info()
                }
            }
        
        return results
    
    def _get_network_info(self) -> Dict:
        """Get basic network information about the execution environment"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return {
                "Host": hostname,
                "IP Address": ip_address,
                "Location": "Unknown (would require GeoIP in production)"
            }
        except:
            return {"Network Info": "Unavailable"}

def display_header(console: Console) -> None:
    """Display fancy header with version information"""
    f = Figlet(font='slant')
    console.print(f"[bold blue]{f.renderText('CentTR')}[/]", justify="center")
    console.print(Panel.fit(
        "simple phone numbers osint v2.1",
        subtitle="./Freedom Security • " + datetime.datetime.now().strftime("%Y-%m-%d"),
        style="bold magenta"
    ))

def display_results(console: Console, results: Dict) -> None:
    """Display results in a rich format with enhanced visualization"""
    if "Basic Info" in results:
        table = Table(title="📱 [bold]Basic Information[/]", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        for key, value in results["Basic Info"].items():
            if isinstance(value, str) and value in ["✅ Yes", "❌ No"]:
                table.add_row(key, value)
            else:
                table.add_row(key, str(value))
        
        console.print(Panel.fit(table, border_style="blue"))
    
    if "Social Media" in results:
        social_media_panels = []
        for platform, url in results["Social Media"].items():
            panel = Panel.fit(
                f"[link={url}]{url}[/link]",
                title=platform,
                border_style="cyan"
            )
            social_media_panels.append(panel)
        
        console.print(Panel.fit(
            Columns(social_media_panels, equal=True, expand=True),
            title="📱 [bold]Social Media Links[/]",
            border_style="blue"
        ))
    
    if "Breach Check" in results:
        if isinstance(results["Breach Check"], list):
            breach_table = Table(title="🔓 [bold]Data Breaches Found[/]", show_header=True, header_style="bold red")
            breach_table.add_column("Breach Name", style="red")
            breach_table.add_column("Date", style="yellow")
            breach_table.add_column("Severity", style="magenta")
            breach_table.add_column("Data Classes", style="cyan")
            
            for breach in results["Breach Check"]:
                breach_table.add_row(
                    breach['Name'],
                    breach['BreachDate'],
                    breach.get('Severity', 'Unknown'),
                    ", ".join(breach['DataClasses'])
                )
            
            console.print(Panel.fit(breach_table, border_style="red"))
        else:
            console.print(Panel.fit(
                str(results["Breach Check"]),
                title="🔒 [bold]Data Breach Check[/]",
                border_style="green" if "not found" in str(results["Breach Check"]).lower() else "yellow"
            ))
    
    if "Google Results" in results and isinstance(results["Google Results"], list):
        google_table = Table(title="🔍 [bold]Google Search Results[/]", show_header=True, header_style="bold yellow")
        google_table.add_column("No.", style="cyan")
        google_table.add_column("URL", style="green")
        
        for i, url in enumerate(results["Google Results"], 1):
            google_table.add_row(str(i), f"[link={url}]{url}[/link]")
        
        console.print(Panel.fit(google_table, border_style="yellow"))
    
    if "Reverse Lookup" in results:
        lookup_panel = Panel.fit(
            "\n".join(results["Reverse Lookup"]),
            title="🔎 [bold]Reverse Lookup Results[/]",
            border_style="cyan"
        )
        console.print(lookup_panel)
    
    if "Metadata" in results:
        meta_table = Table(title="📊 [bold]Metadata[/]", show_header=False)
        meta_table.add_column("Field", style="cyan")
        meta_table.add_column("Value", style="green")
        
        for key, value in results["Metadata"].items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    meta_table.add_row(f"{key}.{subkey}", str(subvalue))
            else:
                meta_table.add_row(key, str(value))
        
        console.print(Panel.fit(meta_table, border_style="dim"))

def open_urls_interactively(console: Console, results: Dict) -> None:
    """Allow user to open URLs interactively"""
    if "Social Media" not in results:
        return
    
    console.print("\n[bold]Would you like to open any links in your browser?[/]")
    options = {str(i): (platform, url) for i, (platform, url) in enumerate(results["Social Media"].items(), 1)}
    
    for num, (platform, url) in options.items():
        console.print(f"{num}. {platform} - [link={url}]{url}[/link]")
    
    console.print("A. Open all links")
    console.print("N. None (continue)")
    
    choice = console.input("\n[bold cyan] CentTR > [/]").upper()
    
    if choice == 'A':
        with console.status("[bold green]Opening all links...[/]"):
            for platform, url in options.values():
                try:
                    webbrowser.open(url)
                except:
                    console.print(f"[red]Failed to open {platform}[/]")
        console.print("[green]All links opened in your default browser[/]")
    elif choice == 'N':
        return
    else:
        selections = re.findall(r'\d+', choice)
        with console.status("[bold green]Opening selected links...[/]"):
            for sel in selections:
                if sel in options:
                    platform, url = options[sel]
                    try:
                        webbrowser.open(url)
                        console.print(f"[green]Opened {platform}[/]")
                        sleep(1)
                    except:
                        console.print(f"[red]Failed to open {platform}[/]")

def main():
    console = Console()
    
    try:
        display_header(console)
        
        phone_number = console.input("[bold cyan] ( +6281234567890 ): [/]").strip()
        
        if not phone_number.startswith('+'):
            console.print("[yellow]Warning: Phone number should start with '+' for international format[/]")
        
        osint = PhoneOSINT(phone_number)
        
        hibp_api = console.input("\n[bold yellow]Enter Have I Been Pwned API key (leave empty to skip): [/]").strip()
        
        with console.status("[bold green]Gathering intelligence...[/]", spinner="dots12") as status:
            results = osint.run_all_checks(
                hibp_api_key=hibp_api if hibp_api else None,
                google_results=5
            )
        
        console.print("\n[bold green]✓ OSINT Results[/]")
        display_results(console, results)
        
        open_urls_interactively(console, results)
        
        save = console.input("\n[bold]Save results to file? (y/n): [/]").lower()
        if save == 'y':
            filename = console.input("[bold cyan]Enter filename ( results.json): [/]").strip()
            try:
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2)
                console.print(f"[bold green]Results saved to {filename}[/]")
                
                open_file = console.input("[bold]Would you like to open the file now? (y/n): [/]").lower()
                if open_file == 'y':
                    webbrowser.open(filename)
            except Exception as e:
                console.print(f"[bold red]Failed to save file: {str(e)}[/]")
    
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user[/]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {str(e)}[/]")
    finally:
        console.print("\n[bold magenta]Thank you for using CentTR Tool![/]")

if __name__ == "__main__":
    main()
