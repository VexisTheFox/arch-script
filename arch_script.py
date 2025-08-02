import os
import time
import random
import psutil
import subprocess
import requests
import pygame
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress

console = Console()
password = None

# Update check configuration
LOCAL_VERSION = "1.1"
VERSION_URL = "https://raw.githubusercontent.com/VexisTheFox/arch-script/main/version_info.json"
DOWNLOAD_URL = "https://raw.githubusercontent.com/VexisTheFox/arch-script/main/arch_script.py"  # Updated to match the script filename

PASTEBIN_URL = "https://pastebin.com/raw/cQG57Wbi"  # Add your Pastebin raw URL here

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    console.print("[bold green]Welcome to the Arch Linux Toolkit[/bold green]")
    console.print("[bold yellow]Select an option to proceed[/bold yellow]\n")

def set_password():
    global password
    password = Prompt.ask("Set a password to lock your system")

def block_computer():
    global password
    if password is None:
        console.print("[bold red]Please set a password first.[/bold red]")
        return

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    font = pygame.font.SysFont("Arial", 72)
    input_font = pygame.font.SysFont("Arial", 36)

    clock = pygame.time.Clock()
    input_text = ""

    running = True
    while running:
        screen.fill((0, 0, 0))
        lock_text = font.render("SYSTEM LOCKED", True, (255, 0, 0))
        prompt_text = input_font.render("Enter password to unlock:", True, (255, 255, 255))
        input_render = input_font.render("*" * len(input_text), True, (255, 255, 255))

        screen.blit(lock_text, (screen.get_width() // 2 - lock_text.get_width() // 2, 100))
        screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2, 250))
        screen.blit(input_render, (screen.get_width() // 2 - input_render.get_width() // 2, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text == password:
                        running = False
                    else:
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        clock.tick(30)

    pygame.quit()

def check_for_updates():
    """Manually checks for updates based on the remote version"""
    try:
        response = requests.get(VERSION_URL)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["version"]
            if latest_version != LOCAL_VERSION:
                console.print(f"[bold red][!] New version {latest_version} available![/bold red]")
                console.print(f"[bold yellow]Changelog:[/bold yellow] {data.get('changelog', 'No details.')}")
                console.print(f"[bold cyan]Download the latest version here:[/bold cyan] {data.get('download_url')}")
                # Optionally ask if the user wants to download the new version
                download_choice = Prompt.ask("Do you want to download the update?", choices=["yes", "no"], default="no")
                if download_choice == "yes":
                    download_update()
            else:
                console.print("[bold green][✓] You are using the latest version.[/bold green]")
        else:
            console.print("[bold red][x] Error checking for updates (HTTP error).[/bold red]")
    except Exception as e:
        console.print(f"[bold red][x] Failed to check for updates: {e}[/bold red]")

def download_update():
    """Downloads the new version of the script from GitHub"""
    try:
        console.print("[bold cyan]Downloading the latest version...[/bold cyan]")
        download_response = requests.get(DOWNLOAD_URL)
        with open('arch_script.py', 'wb') as f:  # Save with the same filename
            f.write(download_response.content)
        console.print("[bold green]Update downloaded successfully! Please restart the script.[/bold green]")
    except Exception as e:
        console.print(f"[bold red][x] Failed to download update: {e}[/bold red]")

# Other functions remain the same...
def package_installer():
    try:
        package = Prompt.ask("Enter the package name to install/remove")
        action = Prompt.ask("Do you want to install or remove this package? (install/remove)")
        if action == "install":
            console.print(f"[cyan]Installing {package}...[/cyan]")
            os.system(f"sudo pacman -S {package}")
        elif action == "remove":
            console.print(f"[red]Removing {package}...[/red]")
            os.system(f"sudo pacman -R {package}")
        else:
            console.print("[red]Invalid action![/red]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def sys_info():
    try:
        console.print("[bold blue]System Information[/bold blue]")
        uname = subprocess.getoutput("uname -a")
        uptime = subprocess.getoutput("uptime -p")
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        console.print(f"OS: {uname}")
        console.print(f"Uptime: {uptime}")
        console.print(f"CPU Usage: {cpu}%")
        console.print(f"Memory Usage: {memory}%")
        console.print(f"Disk Usage: {disk}%")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def network_tools():
    try:
        ip = subprocess.getoutput("hostname -I | awk '{print $1}'")
        console.print(f"Your IP: {ip}")
        host = Prompt.ask("Enter host to ping")
        console.print(f"Pinging {host}...")
        os.system(f"ping -c 4 {host}")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def process_manager():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            processes.append(proc.info)
        processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]

        table = Table(title="Top Processes by CPU Usage")
        table.add_column("PID", style="cyan")
        table.add_column("Process", style="magenta")
        table.add_column("CPU (%)", style="green")
        table.add_column("Memory (%)", style="yellow")

        for proc in processes:
            table.add_row(str(proc['pid']), proc['name'], f"{proc['cpu_percent']}%", f"{proc['memory_percent']}%")

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def package_info():
    try:
        package = Prompt.ask("Enter the package name to check info")
        os.system(f"pacman -Qi {package}")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def fake_progress_bar():
    with Progress() as progress:
        task = progress.add_task("Running fake task...", total=100)
        while not progress.finished:
            progress.update(task, advance=random.randint(1, 5))
            time.sleep(0.1)

def ram_to_storage():
    try:
        os.system("sudo mkdir -p /mnt/ramdisk")
        os.system("sudo mount -t tmpfs -o size=512M tmpfs /mnt/ramdisk")
        console.print("[green]RAM mounted as /mnt/ramdisk[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def unmount_ram():
    try:
        os.system("sudo umount /mnt/ramdisk")
        console.print("[yellow]RAM storage unmounted.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def full_upgrade_check():
    try:
        os.system("sudo pacman -Syu")
        os.system("sudo pacman -Qk")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def disk_usage():
    try:
        usage = psutil.disk_usage('/')
        console.print(f"Total: {usage.total // (2**30)} GB")
        console.print(f"Used: {usage.used // (2**30)} GB")
        console.print(f"Free: {usage.free // (2**30)} GB")
        console.print(f"Usage: {usage.percent}%")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def system_cleanup():
    try:
        os.system("sudo pacman -Rns $(pacman -Qtdq)")
        os.system("sudo pacman -Sc")
        console.print("[green]System cleanup complete.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def weather_check():
    try:
        city = Prompt.ask("Enter your city")
        url = f"https://wttr.in/{city}?format=3"
        weather = requests.get(url).text
        console.print(f"[bold cyan]Weather:[/bold cyan] {weather}")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def change_hostname():
    try:
        new_name = Prompt.ask("Enter new hostname")
        os.system(f"sudo hostnamectl set-hostname {new_name}")
        console.print(f"[green]Hostname changed to {new_name}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

def backup_tool():
    try:
        src = Prompt.ask("Enter the source directory")
        dest = Prompt.ask("Enter the backup destination")
        os.system(f"rsync -avh --progress {src} {dest}")
        console.print("[green]Backup completed.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

# Fetch content from Pastebin
def fetch_pastebin_content():
    try:
        response = requests.get(PASTEBIN_URL)
        if response.status_code == 200:
            content = response.text
            console.print("[bold cyan]Pastebin Content:[/bold cyan]")
            console.print(content)
        else:
            console.print("[bold red]Failed to fetch content from Pastebin[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

def main_menu():
    while True:
        clear()
        banner()

        console.print("[1] Set Password")
        console.print("[2] Lock Computer (Full-Screen Lock)")
        console.print("[3] Install/Remove Package")
        console.print("[4] Show System Info")
        console.print("[5] Network Tools (Ping, IP)")
        console.print("[6] Process Manager")
        console.print("[7] Package Info")
        console.print("[8] Fake Progress Bar (for fun)")
        console.print("[9] Mount RAM as Storage")
        console.print("[10] Unmount RAM Storage")
        console.print("[11] Full System Upgrade & Integrity Check")
        console.print("[12] Disk Usage Analyzer")
        console.print("[13] System Cleanup")
        console.print("[14] Weather Checker")
        console.print("[15] Change Hostname")
        console.print("[16] Backup Tool")
        console.print("[17] Check for Updates")  # New option for update check
        console.print("[0] Exit")

        choice = Prompt.ask("Select an option")

        if choice == '1':
            set_password()
        elif choice == '2':
            block_computer()
        elif choice == '3':
            package_installer()
        elif choice == '4':
            sys_info()
        elif choice == '5':
            network_tools()
        elif choice == '6':
            process_manager()
        elif choice == '7':
            package_info()
        elif choice == '8':
            fake_progress_bar()
        elif choice == '9':
            ram_to_storage()
        elif choice == '10':
            unmount_ram()
        elif choice == '11':
            full_upgrade_check()
        elif choice == '12':
            disk_usage()
        elif choice == '13':
            system_cleanup()
        elif choice == '14':
            weather_check()
        elif choice == '15':
            change_hostname()
        elif choice == '16':
            backup_tool()
        elif choice == '17':  # Check for updates manually
            check_for_updates()
        elif choice == '69':  # Hidden Pastebin option
            fetch_pastebin_content()
        elif choice == '0':
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[bold red]Invalid selection![/bold red]")

        input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    main_menu()
