# [M] pgAdmin 4: Improper restriction of excessive authentication attempts

## Summary
Severity: Medium
Advisory: GHSA-hv9p-2pqf-r5w3
CVE: CVE-2026-7820
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hv9p-2pqf-r5w3
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
Improper restriction of excessive authentication attempts (CWE-307) in pgAdmin 4.

pgAdmin enforces MAX_LOGIN_ATTEMPTS only inside its custom /authenticate/login view. Flask-Security's default /login view, which is registered automatically by security.init_app() and is reachable on every server, never consulted the User.locked field: pgAdmin's User model relied on Flask-Security's UserMixin.is_locked() (which always returns 'not locked') and Flask-Login's is_active (which only checks the active column, not locked). An attacker who triggered an account lockout via /authenticate/login could therefore obtain a session by re-submitting valid credentials directly to /login, defeating the brute-force-protection control for accounts using the INTERNAL authentication source. The same bypass also means that login attempts via /login are never rate-limited, so an attacker can perform an unbounded online password-guessing attack against INTERNAL accounts regardless of MAX_LOGIN_ATTEMPTS.

Fix overrides User.is_active and User.is_locked() so the locked column is enforced on every authentication path. LDAP, OAuth2, Kerberos, and Webserver users are not reachable by this bypass because they have no local password and are rejected by Flask-Security's LoginForm.validate before the locked check; the lockout itself is also internal-only (the /authenticate/login view filters by auth_source=INTERNAL).

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7820
- https://github.com/pgadmin-org/pgadmin4/issues/9904
- https://github.com/pgadmin-org/pgadmin4/commit/d336c1e78
- https://github.com/pgadmin-org/pgadmin4
