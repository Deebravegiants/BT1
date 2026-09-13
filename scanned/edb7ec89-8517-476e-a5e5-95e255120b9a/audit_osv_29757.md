# [H] CVE-2024-46508

## Summary
Severity: High
Advisory: CVE-2024-46508
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2024-46508
Type: osv

## Details
yeti-platform yeti before 2.1.12 allows attackers to generate valid JWT tokens is the secret is not changed (by setting YETI_AUTH_SECRET_KEY to a value other than SECRET).

## References
- https://rhinosecuritylabs.com/research/cve-2024-46507-yeti-server-side-template-injection-ssti/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46508.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46508
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2024-46507
