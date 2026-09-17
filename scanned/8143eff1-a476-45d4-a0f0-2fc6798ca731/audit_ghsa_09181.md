# [M] pyload-ng: non-admin SETTINGS users can disable outbound TLS peer verification via unrestricted `ssl_verify` config (incomplete fix for CVE-2026-33509 / -35463 / -35464 / -35586)

## Summary
Severity: Medium
Advisory: GHSA-ccxc-x975-4hh9
CVE: CVE-2026-42312
CWE: CWE-295, CWE-306, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-ccxc-x975-4hh9
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev100

## Details
### Summary

The `set_config_value()` API method (`@permission(Perms.SETTINGS)`) in `src/pyload/core/api/__init__.py` gates security-sensitive options behind a hand-maintained allowlist `ADMIN_ONLY_CORE_OPTIONS`. The option `("general", "ssl_verify")` is **not** on that allowlist. Any authenticated user with the non-admin `SETTINGS` permission can set `general.ssl_verify = off`, and every subsequent outbound pycurl request is made with `SSL_VERIFYPEER=0` and `SSL_VERIFYHOST=0` — TLS peer and hostname verification are fully disabled. An on-path attacker can then present forged certificates for any hostname pyload fetches.

This is a direct continuation of the fix family CVE-2026-33509 / CVE-2026-35463 / CVE-2026-35464 / CVE-2026-35586, each of which patched a different missed option in the same allowlist.

### Details

**Writer** — `src/pyload/core/api/__init__.py`, `set_config_value()` (around lines 215–290). The function is decorated with `@permission(Perms.SETTINGS)` and only rejects writes when `(category, option)` appears in `ADMIN_ONLY_CORE_OPTIONS`:

```python
ADMIN_ONLY_CORE_OPTIONS = {
    ("general", "storage_folder"),
    ("log", "syslog_host"), ("log", "syslog_port"),
    ("proxy", "password"), ("proxy", "username"),
    ("reconnect", "script"),
    ("webui", "host"),
    ("webui", "ssl_certfile"), ("webui", "ssl_keyfile"), ("webui", "ssl_certchain"),
    ("webui", "use_ssl"),
}
...
if (category, option) in ADMIN_ONLY_CORE_OPTIONS and not is_admin:
    self.pyload.log.error(...); return
self.pyload.config.set(category, option, value)
```

`("general", "ssl_verify")` is absent. `config.set()` in `src/pyload/core/config/parser.py:329` calls `cast()` which has no branch for enum-string types — `"off"` is stored verbatim and persisted to disk via `self.save()`.

**Reader** — `src/pyload/core/network/request_factory.py:109-110`:

```python
def get_options(self):
    return {
        "interface": self.iface(),
        "proxies":   self.get_proxies(),
        "ipv6":      self.pyload.config.get("download", "ipv6"),
        "ssl_verify": self.pyload.config.get("general", "ssl_verify"),
        ...
    }
```

**Sink** — `src/pyload/core/network/http/http_request.py:193-206`:

```python
if "ssl_verify" in options:
    aiachaser_on = b"on (using aia-chaser)"
    if options["ssl_verify"] in [True, b"on", aiachaser_on]:
        ...
        ssl_verify = 1
    else:
        ssl_verify = 0
    self.c.setopt(pycurl.SSL_VERIFYPEER, ssl_verify)
    self.c.setopt(pycurl.SSL_VERIFYHOST, ssl_verify * 2)
```

Because `get_options()` is invoked every time a new pycurl handle is built, the new config value takes effect on the very next outbound request — no pyload restart required.

### PoC

Authenticated as any user who has `Perms.SETTINGS` but is **not** admin (e.g. a user with `Role.USER` + the SETTINGS permission bit):

```bash
# 1) Log in as the SETTINGS (non-admin) user.
curl -c cookies.txt -X POST http://pyload.example:8000/api/login \
    -d 'username=settings_user&password=<password>'

# 2) Disable TLS verification for all outbound downloads.
curl -b cookies.txt -X POST http://pyload.example:8000/api/setConfigValue \
    -d 'category=general&option=ssl_verify&value=off&section=core'
# -> 200 OK. Config persisted.

# 3) Enqueue any HTTPS download. An on-path attacker (shared LAN,
#    compromised upstream router, DNS hijack, or a malicious proxy
#    enabled via the sibling advisory on the proxy.* options) can
#    now present a forged cert for any target — pyload accepts it.
```

Verification: observe pycurl `SSL_VERIFYPEER=0` in a debug build, or confirm that a download from an HTTPS endpoint served with a self-signed / mismatched cert succeeds after step 2 and fails before it.

### Impact

- **Who**: any authenticated user whose role was granted `Perms.SETTINGS`. In multi-user pyload deployments that delegate settings administration to non-admins, this is an unintended privilege escalation from "can change UI/download settings" to "can silently disable TLS cert validation for all outbound fetches".
- **What**:
    1. Man-in-the-middle on all HTTPS downloads, captcha fetches, update checks, and plugin HTTP calls.
    2. Extends the impact of the already-published SSRF chain (CVE-2026-33992 / CVE-2026-35459). The URL-hostname validation those patches added is only meaningful if the TLS channel authenticates the endpoint; with `ssl_verify=off`, an on-path attacker can present forged certs for already-validated hosts — so HTTPS cloud-metadata endpoints and internal HTTPS services behind the host allowlist become reachable again.
    3. Silent to the admin. Every adjacent security-critical option (`proxy.password`, SSL certfile/keyfile/certchain, `use_ssl`) is already admin-only, so the admin's mental model is that TLS policy cannot be weakened by a non-admin.
- **Not impacted**: unauthenticated attackers; users holding only `DOWNLOAD` / `LIST` roles.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-ccxc-x975-4hh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42312
- https://github.com/advisories/GHSA-4744-96p5-mp2j
- https://github.com/advisories/GHSA-ppvx-rwh9-7rj7
- https://github.com/advisories/GHSA-r7mc-x6x7-cqxx
- https://github.com/advisories/GHSA-w48f-wwwf-f5fr
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-126.yaml
