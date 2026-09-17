# [C] CVE-2024-25674

## Summary
Severity: Critical
Advisory: CVE-2024-25674
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-25674
Type: osv

## Details
An issue was discovered in MISP before 2.4.184. Organisation logo upload is insecure because of a lack of checks for the file extension and MIME type.

## References
- https://github.com/MISP/MISP/compare/v2.4.183...v2.4.184
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25674.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25674
- https://github.com/MISP/MISP/commit/312d2d5422235235ddd211dcb6bb5bb09c07791f
