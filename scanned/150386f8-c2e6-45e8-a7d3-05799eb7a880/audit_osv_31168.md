# [H] CVE-2024-58130

## Summary
Severity: High
Advisory: CVE-2024-58130
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2024-58130
Type: osv

## Details
In app/Controller/Component/RestResponseComponent.php in MISP before 2.4.193, REST endpoints have a lack of sanitization for non-JSON responses.

## References
- https://github.com/MISP/MISP/releases/tag/v2.4.193
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58130.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58130
- https://github.com/MISP/MISP/commit/f08a2eaec25f0212c22b225c0b654bd60d089ef9
