# [C] CVE-2024-25675

## Summary
Severity: Critical
Advisory: CVE-2024-25675
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-09
Source: https://osv.dev/vulnerability/CVE-2024-25675
Type: osv

## Details
An issue was discovered in MISP before 2.4.184. A client does not need to use POST to start an export generation process. This is related to app/Controller/JobsController.php and app/View/Events/export.ctp.

## References
- https://github.com/MISP/MISP/compare/v2.4.183...v2.4.184
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25675.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25675
- https://github.com/MISP/MISP/commit/0ac2468c2896f4be4ef9219cfe02bff164411594
