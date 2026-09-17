# [C] Pheditor: Authentication Bypass in Forced Password-Change Flow via Unverified Current Password

## Summary
Severity: Critical
Advisory: GHSA-f25v-x6vr-962g
CWE: CWE-1392
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-f25v-x6vr-962g
Type: github-advisory

## Affected
- Packagist: `pheditor/pheditor` — affected >=0 <2.0.8

## Details
## Summary

The forced password-change flow, triggered when the stored password is still the default (`admin`), does not verify that the password submitted by the client actually matches the current password. Any non-empty value in `pheditor_password` is enough to reach the password-change form, and submitting `pheditor_new_password` / `pheditor_confirm_password` in the same request is enough to set an arbitrary new password and obtain an authenticated session — without ever proving knowledge of the current password.

## Root Cause

`pheditor.php` line 163:

```php
if (PASSWORD == hash('sha512', 'admin')) { // still default — force change prompt
```

This checks whether the **stored** `PASSWORD` constant is still the default value. It does not check whether the **submitted** `pheditor_password` matches it. As a result, on any instance that hasn't changed the default password, the check passes regardless of what the client actually sends, and the subsequent password-change branch is reachable without authentication.

## PoC

```bash
TARGET="https://victim.com/pheditor.php"

# Any non-empty value works here — password is never actually verified
curl -c /tmp/j.txt \
  -d 'pheditor_password=anything' \
  -d 'pheditor_new_password=attacker123' \
  -d 'pheditor_confirm_password=attacker123' \
  "$TARGET" -L -s -o /dev/null

# Session is now authenticated as admin, with the password changed to attacker123
```

## Impact

On any instance where the default password has not yet been changed, an unauthenticated attacker can set an arbitrary new admin password and obtain a fully authenticated session, without knowing the current password. This is a complete authentication bypass, not merely "default credentials in use" — it holds even if the operator believes the instance is protected because the login form is present.

## Remediation

Verify the submitted password against the stored `PASSWORD` constant *before* entering the forced password-change branch, so the flow is reachable only by someone who actually knows the current password:

```php
$submitted_hash = hash('sha512', $_POST['pheditor_password']);

if (PASSWORD == hash('sha512', 'admin') && $submitted_hash === PASSWORD) {
    // proceed to forced password-change flow
} else {
    // treat as a normal login attempt (including rate-limiting)
}
```

## Note on scope

The original report submitted alongside this finding also included two additional items:

- **Unrestricted PHP upload** — addressed as intended behavior (Pheditor is a single-admin PHP file editor; PHP file creation/editing is core to its function, and pattern-restricting only the upload path doesn't reduce risk since the same result is reachable via the `save`/`newfile` action). Documented explicitly in the README's new Security Model section.
- **Terminal allowlist bypass (`php -r ...`)** — a duplicate of a previously reported and already-patched issue (GHSA-g3hq-hphg-8fhh, fixed in v2.0.7).

This advisory has been scoped to the authentication bypass specifically, since it's a distinct root cause from both of those. Full responses to all three points are in the comments below.

## References
- https://github.com/pheditor/pheditor/security/advisories/GHSA-f25v-x6vr-962g
- https://github.com/pheditor/pheditor/commit/0978bcda644832b67357340e2f271e32d86fdf86
- https://github.com/pheditor/pheditor
- https://github.com/pheditor/pheditor/releases/tag/2.0.8
