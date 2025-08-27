import time
import subprocess
import sys

# Lista de IPs para monitorar
ips = ["192.168.1.254", "8.8.8.8", "192.168.1.100", "192.168.1.50"]

# Listas para armazenar status
ips_on = []
ips_off = []


def show_notification(title, message):
    """Envia notificação no Linux usando notify-send"""
    try:
        subprocess.Popen(['notify-send', title, message])
        print(f"Notificação enviada: {title} - {message}")
    except FileNotFoundError:
        print("Erro: 'notify-send' não encontrado. Instale o pacote 'libnotify-bin'")
        print(f"Simulação de notificação: {title} - {message}")


def ping_host(ip):
    """Executa ping usando o comando nativo do Linux"""
    try:
        saida = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],  # -c 1 = 1 pacote | -W 2 = timeout de 2s
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return saida.returncode == 0
    except Exception:
        return False


def verificar_conectividade():
    ips_on.clear()
    ips_off.clear()

    for ip in ips:
        if ping_host(ip):
            ips_on.append(ip)
        else:
            ips_off.append(ip)   # agora guardamos só o IP, não a frase


# Verifica se o sistema suporta notificações
if sys.platform != 'linux':
    print("Aviso: Este script foi otimizado para Linux")

# Loop de monitoramento
try:
    while True:
        print("\n" + "=" * 40)
        print(f"Verificando conectividade em {time.strftime('%H:%M:%S')}")

        verificar_conectividade()

        if ips_off:
            # monta a mensagem com todos os IPs OFF
            mensagem = "Os seguintes IPs estão inacessíveis:\n" + "\n,".join(ips_off)
            print(mensagem)
            show_notification("Alerta de Conectividade", mensagem)
        else:
            print("Todos os IPs estão acessíveis.")

        print(f"Aguardando 5 minutos... (Ctrl+C para sair)")
        time.sleep(300)  # 5 minutos
except KeyboardInterrupt:
    print("\nMonitoramento encerrado pelo usuário.")
