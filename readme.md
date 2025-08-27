# Código Ajustado para Notificações no Linux

Usando `notify-send`, que é o sistema de notificação nativo do Linux (funciona com GNOME, KDE, etc.). Também vou fazer algumas melhorias:


## Melhorias realizadas:

1. **Substituição do `win10toast`**:
   - Usei `notify-send` via `subprocess` (disponível na maioria das distribuições Linux)
   - Adicionei tratamento de erro caso o comando não exista

2. **Otimizações**:
   - Agrupa todos os IPs inacessíveis em uma única notificação
   - Adicionei timestamp nas verificações
   - Mensagem de encerramento mais clara

3. **Pré-requisitos**:
   - Instale o `libnotify-bin` se necessário:
     ```bash
     sudo apt install libnotify-bin
     ```
   - Instale via pip (recomendado):**
   ```bash
   pip install ping3
   ```
   Se você receber um erro de permissão, use:
   ```bash
   pip install --user ping3
   ```

---

**Se não tiver o `pip` instalado:**
   Instale primeiro o pip:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   ```
   (Para distribuições baseadas em Debian/Ubuntu)

2**Verifique se a instalação funcionou:**
   ```bash
   python3 -c "from ping3 import ping; print(ping('8.8.8.8'))"
   ```
   Isso deve retornar um número (tempo de resposta em segundos) ou `None` se falhar.

### Observações importantes:

1. **Dependências:**
   - O `ping3` requer permissão para enviar pacotes ICMP. Se estiver executando como usuário normal, pode precisar de:
     ```bash
     sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
     ```

2. **Alternativa sem `ping3`:**
   Se preferir não instalar o `ping3`, você pode substituir a função `ping()` por um comando nativo do sistema:
   ```python
   import subprocess

   def ping(host):
       try:
           output = subprocess.check_output(["ping", "-c", "1", "-W", "2", host])
           return True
       except subprocess.CalledProcessError:
           return False
   ```

3. **Para desinstalar (caso necessário):**
   ```bash
   pip uninstall ping3
   ```
**Atenção**

Pode erro ocorre porque o Python não tem permissão para criar sockets RAW, necessários para enviar pacotes ICMP (ping) no Linux. Vamos resolver isso de três maneiras:

### Solução 1: Conceder permissões (recomendado)
Execute este comando para dar ao Python as permissões necessárias:
```bash
sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
```

Sobre o setcap (Solução 1):

Você só precisa executar uma vez o comando:
```bash

sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
```

A menos que:

    Você reinstale o Python

    Atualize para uma nova versão do Python que mude o caminho do binário

    Remova manualmente a permissão com setcap -r

A permissão permanecerá persistente até um desses eventos ocorrer.

### Solução 2: Executar como root (não recomendado)
Execute o script com sudo:
```bash
sudo python3 seu_script.py
```

### Solução 3: Usar subprocess (alternativa sem ping3)
Modifique seu script para usar o comando `ping` do sistema:

```python
import time
import subprocess
from win10toast import ToastNotifier

# Lista de IPs para monitorar
ips = ["192.168.1.254", "8.8.8.8", "192.168.1.50", "192.168.1.100"]

def ping(host):
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "2", host], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def verificar_conectividade():
    for ip in ips:
        if not ping(ip):
            mensagem = f"Atenção! O IP {ip} está inacessível."
            print(mensagem)
            # Enviar notificação (substitua por notify-send no Linux)
            subprocess.Popen(['notify-send', "Monitoramento de Rede", mensagem])

try:
    while True:
        print("Verificando conectividade...")
        verificar_conectividade()
        print("Aguardando 2 minutos...")
        time.sleep(120)
except KeyboardInterrupt:
    print("Monitoramento encerrado.")
```

### Por que isso acontece?
- No Linux, enviar pacotes ICMP requer privilégios especiais
- O `setcap` concede apenas a permissão específica necessária
- A solução com `subprocess` funciona porque o binário `ping` já tem as permissões necessárias

### Dica adicional:
Para notificações no Linux, instale:
```bash
sudo apt install libnotify-bin
```

Escolha a solução que melhor se adapta ao seu ambiente. A Solução 1 é a mais segura e recomendada para uso contínuo.



4. **Funcionamento**:
   - As notificações aparecerão no sistema de notificação do seu ambiente gráfico
   - Se testar em terminal sem GUI, mostrará apenas as mensagens no console


---

### Sobre o Aviso do `notify-send`:
Esse aviso ocorre porque:

#### Causa:
Seu ambiente Linux está usando **Portal Notifications** (parte do sistema Flatpak/Snap/Sandboxing) em vez do sistema nativo de notificações. Isso é comum em:
- Sistemas com GNOME moderno (especialmente em Fedora, Ubuntu recentes)
- Ambientes com restrições de sandbox
- Sistemas onde o `notify-send` está sendo executado em um container/Flatpak

#### Impacto:
- **Não afeta a funcionalidade básica** (as notificações ainda aparecerão)
- Apenas algumas "features avançadas" de notificações não estarão disponíveis (como categorias ou nomes de aplicativos personalizados)

#### Como resolver (opcional):
1. **Método simples (ignorar o aviso)**  
   Funciona normalmente apesar do aviso.

2. **Forçar notificações nativas**  
   Execute isto antes de rodar seu script:
   ```bash
   export NO_AT_BRIDGE=1
   ```

3. **Instalar notificações nativas**  
   Certifique-se de ter o pacote completo:
   ```bash
   sudo apt install libnotify-bin notification-daemon
   ```

4. **Alternativa usando `zenity`**  
   Substitua no código:
   ```python
   subprocess.Popen(['zenity', '--info', '--text', mensagem])
   ```

---

### Versão Final Otimizada do Código (com tratamento do aviso):
```python
import os
os.environ['NO_AT_BRIDGE'] = '1'  # Suprime o aviso

# [...] (restante do código igual)
```

Isso manterá:
- Permissão permanente do `setcap`
- Notificações funcionais (mesmo com o aviso inofensivo)
- Monitoramento contínuo sem necessidade de reconfiguração

---
# Ajuste para melhorar a informação - 27/08/2025

Boa observação 👀. O problema não está no `ping` do terminal (que funciona como esperado), mas sim no **comportamento da biblioteca `ping3`** que você está usando no script.

⚡ O detalhe é que o `ping3` só retorna `None` quando **não recebe resposta nenhuma** (timeout).
Se a resposta for `"Destination Host Unreachable"` (como no seu caso com `192.168.1.50` e `192.168.1.100`), o `ping3` ainda considera que recebeu *alguma* resposta ICMP e não retorna `None`. Por isso um deles aparece como OFF e o outro não.

Ou seja:

* `ping3` trata `Destination Host Unreachable` como se fosse "resposta válida" → ele coloca o IP como **ON**.
* Só quando não há resposta de jeito nenhum é que ele devolve `None`.

---

### 🔧 Soluções possíveis

1. **Forçar checagem com retorno numérico**
   Você pode verificar se o resultado é `None` **ou não é número** (porque `ping3` deveria retornar o tempo em segundos como `float`).

```python
def verificar_conectividade():
    ips_on.clear()
    ips_off.clear()

    for ip in ips:
        resultado = ping(ip, timeout=3, unit='ms')
        if resultado is None or not isinstance(resultado, (int, float)):
            ips_off.append(f"IP {ip} inacessível")
        else:
            ips_on.append(ip)
```

---

2. **Usar `subprocess` com o ping nativo do Linux**
   Isso vai te dar a mesma saída que você vê no terminal, sem depender do jeito "meio confuso" do `ping3` interpretar.

```python
def ping_host(ip):
    try:
        saida = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return saida.returncode == 0
    except Exception as e:
        return False


def verificar_conectividade():
    ips_on.clear()
    ips_off.clear()

    for ip in ips:
        if ping_host(ip):
            ips_on.append(ip)
        else:
            ips_off.append(f"IP {ip} inacessível")
```

Aqui, se o `ping` retornar erro (`returncode != 0`), cai no `ips_off`. Isso vai bater 100% com o comportamento do terminal.

---

👉 Eu, pessoalmente, iria de **opção 2** (`subprocess`), porque é mais fiel ao que você já testou no terminal e não depende das "interpretações" da lib `ping3`.

--- 

# Informações

Boa pergunta 👊

Esse alerta não é erro do teu script — é um **comportamento esperado do `notify-send` no Linux moderno**.
Explico:

📌 **O que está acontecendo?**

* Em distros que usam **Flatpak / Snap** ou ambientes gráficos mais recentes (ex.: GNOME + Wayland), o `notify-send` roda em um modo chamado **Portal**.
* Nesse modo, algumas opções extras do `notify-send` não funcionam (como ícone customizado, categorias, hints avançados).
* O aviso é só para te dizer: *"Olha, estou usando um fallback, então nem todos os recursos estão disponíveis"*.

📌 **O que isso significa para você?**

* As notificações **continuam aparecendo normalmente** (o que você precisa está funcionando).
* Você só não vai poder usar algumas frescuras como definir ícones ou categorias de notificação.

📌 **Preciso me preocupar?**
👉 **Não.**
É totalmente inofensivo, e o `notify-send` foi projetado para mostrar esse aviso.
Se quiser se livrar do log "chato", pode redirecionar a saída de erro do `subprocess.Popen` para `subprocess.DEVNULL`:

```python
subprocess.Popen(['notify-send', title, message],
                 stderr=subprocess.DEVNULL)
```

Assim você não vê mais a mensagem no terminal.

---

⚡ Resumindo:
Esse aviso não quebra nada. Se a notificação está aparecendo, está tudo certo.
É só o Linux reclamando que não pode usar todos os recursos do `libnotify`.

Quer que eu já te deixe o `show_notification` ajustado para **silenciar esse aviso** no terminal?

