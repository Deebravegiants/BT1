# [H] Lemur has an authorization bypass in StrictRolePermission / AuthorityCreatorPermission

## Summary
Severity: High
Advisory: GHSA-qcqw-jwxc-2hqg
CVE: CVE-2026-48508
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-qcqw-jwxc-2hqg
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.1

## Details
## Summary

`StrictRolePermission` and `AuthorityCreatorPermission` in `lemur/auth/permissions.py` call `flask_principal.Permission.__init__()` with zero `Need`s when their config flags are unset. Both flags defaulted to `False` in code prior to the fix, so this was the state of any Lemur install that hadn't explicitly opted in.

Flask-Principal's `Permission.allows()` returns `True` whenever `self.needs` is empty. The `.can()` gate therefore passes for every authenticated identity, including the lowest-privilege role Lemur ships (`read-only`).

A user holding only `read-only` can create root Certificate Authorities, create and edit notifications (an SSRF sink), create domain entries, and upload arbitrary certificates. These classes are the sole authorization check on those endpoints.

## Root Cause

```python
# lemur/auth/permissions.py
class AuthorityCreatorPermission(Permission):
    def __init__(self):
        requires_admin = current_app.config.get("ADMIN_ONLY_AUTHORITY_CREATION", False)
        if requires_admin:
            super().__init__(RoleNeed("admin"))
        else:
            super().__init__()              # empty Need set

class StrictRolePermission(Permission):
    def __init__(self):
        strict_role_enforcement = current_app.config.get("LEMUR_STRICT_ROLE_ENFORCEMENT", False)
        if strict_role_enforcement:
            needs = [RoleNeed("admin"), RoleNeed("operator")]
            super().__init__(*needs)
        else:
            super().__init__()              # empty Need set
```

`flask_principal.Permission.allows()` (upstream, v0.4.0):

```python
def allows(self, identity):
    if self.needs and not self.needs.intersection(identity.provides):
        return False
    ...
    return True
```

When `self.needs == set()`, the first guard is falsy and is skipped. `excludes` is also empty, so `allows()` returns `True` for any identity. `AuthenticatedResource` (the parent class for these views) sets `method_decorators = [login_required]`, which checks authentication only, no role. So the permission `.can()` is the only authorization layer in front of these endpoints.

## Affected Endpoints

Views whose only authorization check is `StrictRolePermission().can()` or `AuthorityCreatorPermission().can()`:

| Method   | Path                                      | Source                                  |
|----------|-------------------------------------------|-----------------------------------------|
| POST     | /api/1/authorities                        | lemur/authorities/views.py:231          |
| POST     | /api/1/certificates/upload                | lemur/certificates/views.py:651         |
| POST     | /api/1/pending_certificates/\<id>/upload  | lemur/pending_certificates/views.py:545 |
| POST     | /api/1/notifications                      | lemur/notifications/views.py:227        |
| PUT/DEL  | /api/1/notifications/\<id>                | lemur/notifications/views.py:370,384    |
| POST     | /api/1/domains                            | lemur/domains/views.py:131              |

`POST /api/1/authorities` is gated by `AuthorityCreatorPermission().can() and StrictRolePermission().can()`; both have empty Needs by default. The other rows are gated by `StrictRolePermission().can()` alone.

Note on scope: `PUT /api/1/authorities/<id>` also references `StrictRolePermission`, but its gate is `AuthorityPermission(...).can() and StrictRolePermission().can()`. `AuthorityPermission` is constructed with non-empty Needs (`RoleNeed("admin")` plus authority-scoped needs), so that endpoint is not bypassable by a `read-only` user and is excluded from this report.

## Impact

A user holding only the `read-only` role can:

1. Create root Certificate Authorities. CA cert and private key are persisted in Lemur's DB with the attacker as owner. Any internal trust store that pins Lemur-managed roots can now be signed against by the attacker.
2. Upload arbitrary certificates via `/certificates/upload`, including attacker-supplied keys with destinations such as AWS push.
3. Create or modify notifications, which reach an SSRF sink (see related finding F3, Slack notification webhook).
4. Mark arbitrary domains as `sensitive`, manipulating Lemur's domain registry and the cert-issuance approval path.

Combined with any low-privilege credential leak (phished employee, leaked SSO token) or insider access, this is a pivot from "any authenticated identity" to control of the PKI issuance plane.

## Remediation

The config flag defaults for `ADMIN_ONLY_AUTHORITY_CREATION` and `LEMUR_STRICT_ROLE_ENFORCEMENT` were changed from `False` to `True`. Restrictive role enforcement is now active on all default installs without requiring explicit configuration.

```python
class AuthorityCreatorPermission(Permission):
    def __init__(self):
        requires_admin = current_app.config.get("ADMIN_ONLY_AUTHORITY_CREATION", True)
        ...

class StrictRolePermission(Permission):
    def __init__(self):
        strict_role_enforcement = current_app.config.get("LEMUR_STRICT_ROLE_ENFORCEMENT", True)
        ...
```

**Note:** The opt-out branches (empty Needs) remain in the code. Operators who explicitly set `ADMIN_ONLY_AUTHORITY_CREATION = False` or `LEMUR_STRICT_ROLE_ENFORCEMENT = False` in their config will reintroduce the bypass. These flags should be left unset or set to `True`.

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-qcqw-jwxc-2hqg
- https://github.com/Netflix/lemur
