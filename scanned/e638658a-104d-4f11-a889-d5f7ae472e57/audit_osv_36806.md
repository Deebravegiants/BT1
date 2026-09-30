# [H] PlaciPy Admin Privilege Escalation via Trusted JWT Claims

## Summary
Severity: High
Advisory: CVE-2026-25875
Aliases: GHSA-mx95-8ppg-v574
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25875
Type: osv

## Details
PlaciPy is a placement management system designed for educational institutions. In version 1.0.0, The admin authorization middleware trusts client-controlled JWT claims (role and scope) without enforcing server-side role verification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25875.json
- https://github.com/Praskla-Technology/assessment-placipy/security/advisories/GHSA-mx95-8ppg-v574
- https://nvd.nist.gov/vuln/detail/CVE-2026-25875
