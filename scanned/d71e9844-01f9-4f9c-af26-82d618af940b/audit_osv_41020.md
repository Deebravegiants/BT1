# [C] Modoboa < 2.9.0 - Insecure Direct Object Reference in Account Password Change API

## Summary
Severity: Critical
Advisory: CVE-2026-56780
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-56780
Type: osv

## Details
Modoboa before 2.9.0 contains an insecure direct object reference vulnerability in the PUT /api/v1/accounts/{pk}/password/ endpoint that allows domain administrators to change any user's password. Attackers with domain admin privileges can bypass object-level access controls to reset superadmin passwords and achieve full account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56780.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56780
- https://www.vulncheck.com/advisories/modoboa-insecure-direct-object-reference-in-account-password-change-api
- https://github.com/modoboa/modoboa/pull/4038
- https://github.com/modoboa/modoboa/commit/a1878c4920a6e47c3217c6ff1ed4a8753c202661
- https://github.com/modoboa/modoboa
