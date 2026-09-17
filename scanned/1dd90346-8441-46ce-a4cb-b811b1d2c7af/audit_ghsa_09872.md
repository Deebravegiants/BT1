# [H] pyLoad has Stale Session Privilege After Role/Permission Change (Privilege Revocation Bypass)

## Summary
Severity: High
Advisory: GHSA-66hx-chf7-3332
CVE: CVE-2026-41133
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-66hx-chf7-3332
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0

## Details
### Summary
pyLoad caches `role` and `permission` in the session at login and continues to authorize requests using these cached values, even after an admin changes the user's role/permissions in the database.

As a result, an already logged-in user can keep old (revoked) privileges until logout/session expiry, enabling continued privileged actions.

This is a core authorization/session-consistency issue and is not resolved by toggling an optional security feature.

### Details
The WebUI auth flow stores authorization state in session:

- `src/pyload/webui/app/helpers.py:187-200`
  - `set_session(...)` writes:
    - `"role": user_info["role"]`
    - `"perms": user_info["permission"]`

Authorization checks later trust cached session values:

- `src/pyload/webui/app/helpers.py:134-151`
  - `parse_permissions(...)` reads `session.get("role")` / `session.get("perms")`
- `src/pyload/webui/app/helpers.py:225-230`
  - `is_authenticated(...)` only verifies `authenticated` and `api.user_exists(user)` (existence), not fresh role/permission
- `src/pyload/webui/app/helpers.py:267-275`
  - `login_required(...)` uses `parse_permissions(s)` for allow/deny decisions
- `src/pyload/webui/app/helpers.py:356-365`
  - API session auth path also trusts `s["role"]` and `s["perms"]`

Role/permission updates are written to DB but active sessions are not invalidated/refreshed:

- `src/pyload/webui/app/blueprints/json_blueprint.py:389-434`
  - `update_users(...)` calls `api.set_user_permission(...)` and returns
- `src/pyload/core/api/__init__.py:1643-1645`
  - `set_user_permission(...)` updates DB role/permission only

Default exposure window is long:

- `src/pyload/core/config/default.cfg:47`
  - `session_lifetime = 44640` minutes (~31 days)

Therefore, privilege revocation is not enforced immediately for active sessions.

Note on duplicates:
- This appears distinct from CVE-2023-0227 (session validity after **user deletion**) because this report is about stale authorization after **role/permission changes** while the user still exists.

### PoC

```python
#!/usr/bin/env python3
"""
Repro: stale session privilege after role/permission changes.

This PoC is source-based and leaves no persistent state.
It validates that:
1) Role/permission are cached into session at login.
2) Authorization checks read role/permission from session, not fresh DB values.
3) User updates write DB permission/role without invalidating active sessions.
4) Default session lifetime is long, increasing stale-privilege exposure window.
"""

from __future__ import annotations

import pathlib
import re
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parent / "pyload" / "src" / "pyload"


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def has_any(text: str, patterns: Iterable[str]) -> bool:
    return all(re.search(p, text, re.MULTILINE) for p in patterns)


def main() -> None:
    helpers = read("webui/app/helpers.py")
    json_blueprint = read("webui/app/blueprints/json_blueprint.py")
    api_init = read("core/api/__init__.py")
    default_cfg = (ROOT / "core/config/default.cfg").read_text(encoding="utf-8")

    checks = {
        "set_session_caches_role_perms": has_any(
            helpers,
            [
                r'def\\s+set_session\\(',
                r'"role"\\s*:\\s*user_info\\["role"\\]',
                r'"perms"\\s*:\\s*user_info\\["permission"\\]',
            ],
        ),
        "is_authenticated_only_checks_user_exists": has_any(
            helpers,
            [
                r'def\\s+is_authenticated\\(',
                r'api\\s*=\\s*flask\\.current_app\\.config\\["PYLOAD_API"\\]',
                r'return\\s+authenticated\\s+and\\s+api\\.user_exists\\(user\\)',
            ],
        ),
        "parse_permissions_reads_session_cache": has_any(
            helpers,
            [
                r'def\\s+parse_permissions\\(',
                r'session\\.get\\("role"\\)\\s*==\\s*Role\\.ADMIN',
                r'session\\.get\\("perms"\\)',
            ],
        ),
        "login_required_uses_parse_permissions_session": has_any(
            helpers,
            [
                r'def\\s+login_required\\(',
                r'if\\s+is_authenticated\\(s\\):',
                r'perms\\s*=\\s*parse_permissions\\(s\\)',
            ],
        ),
        "api_session_auth_uses_cached_role_perms": has_any(
            helpers,
            [
                r'if\\s+is_authenticated\\(s\\):',
                r'"role"\\s*:\\s*s\\["role"\\]',
                r'"permission"\\s*:\\s*s\\["perms"\\]',
            ],
        ),
        "update_users_changes_db_without_session_invalidation": has_any(
            json_blueprint,
            [
                r'def\\s+update_users\\(',
                r'api\\.set_user_permission\\(name,\\s*data\\["permission"\\],\\s*data\\["role"\\]\\)',
                r'return\\s+jsonify\\(True\\)',
            ],
        ),
        "set_user_permission_only_updates_db": has_any(
            api_init,
            [
                r'def\\s+set_user_permission\\(',
                r'self\\.pyload\\.db\\.set_permission\\(user,\\s*permission\\)',
                r'self\\.pyload\\.db\\.set_role\\(user,\\s*role\\)',
            ],
        ),
        "default_session_lifetime_long": re.search(
            r'session_lifetime\\s*:\\s*"Session lifetime \\(minutes\\)"\\s*=\\s*44640',
            default_cfg,
            re.MULTILINE,
        )
        is not None,
    }

    for name, ok in checks.items():
        print(f"{name}={ok}")

    stale_privilege_repro_success = all(checks.values())
    print(f"stale_privilege_repro_success={stale_privilege_repro_success}")

    # Cleanup: this PoC creates/modifies no runtime/data files.
    print("cleanup_done=True")


if __name__ == "__main__":
    main()
```

```text
set_session_caches_role_perms=True
is_authenticated_only_checks_user_exists=True
parse_permissions_reads_session_cache=True
login_required_uses_parse_permissions_session=True
api_session_auth_uses_cached_role_perms=True
update_users_changes_db_without_session_invalidation=True
set_user_permission_only_updates_db=True
default_session_lifetime_long=True
stale_privilege_repro_success=True
cleanup_done=True
```

### Impact
- Privilege revocation is not immediate for active sessions.
- A user can continue using stale, previously granted privileges (including admin) after downgrade/restriction.
- This can allow continued access to privileged WebUI/API actions until session expiry or manual logout/session reset.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-66hx-chf7-3332
- https://nvd.nist.gov/vuln/detail/CVE-2026-41133
- https://github.com/pyload/pyload/commit/e95804fb0d06cbb07d2ba380fc494d9ff89b68c1
- https://github.com/pyload/pyload
