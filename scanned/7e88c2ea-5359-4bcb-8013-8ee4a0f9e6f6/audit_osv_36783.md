# [C] PlaciPy has a Hard-Coded Default Password for All Student Accounts (Account Takeover)

## Summary
Severity: Critical
Advisory: CVE-2026-25753
Aliases: GHSA-6537-cf56-j9w2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-06
Source: https://osv.dev/vulnerability/CVE-2026-25753
Type: osv

## Details
PlaciPy is a placement management system designed for educational institutions. In version 1.0.0, the application uses a hard-coded, static default password for all newly created student accounts. This results in mass account takeover, allowing any attacker to log in as any student once the password is known.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25753.json
- https://github.com/Praskla-Technology/assessment-placipy/security/advisories/GHSA-6537-cf56-j9w2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25753
