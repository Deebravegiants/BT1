# [C] CVE-2023-48655

## Summary
Severity: Critical
Advisory: CVE-2023-48655
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-17
Source: https://osv.dev/vulnerability/CVE-2023-48655
Type: osv

## Details
An issue was discovered in MISP before 2.4.176. app/Controller/Component/IndexFilterComponent.php does not properly filter out query parameters.

## References
- https://github.com/MISP/MISP/compare/v2.4.175...v2.4.176
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48655.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-48655
- https://zigrin.com/advisories/misp-blind-sql-injection-in-array-input-parameters/
- https://github.com/MISP/MISP/commit/158c8b2f788b75e0d26e9249a75e1be291e59d4b
