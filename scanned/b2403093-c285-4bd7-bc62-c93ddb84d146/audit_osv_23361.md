# [C] CVE-2022-48329

## Summary
Severity: Critical
Advisory: CVE-2022-48329
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2022-48329
Type: osv

## Details
MISP before 2.4.166 unsafely allows users to use the order parameter, related to app/Model/Attribute.php, app/Model/GalaxyCluster.php, app/Model/Workflow.php, and app/Plugin/Assets/models/behaviors/LogableBehavior.php.

## References
- https://github.com/MISP/MISP/compare/v2.4.165...v2.4.166
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48329.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48329
- https://github.com/MISP/MISP/commit/a73c1c461bc6f8a048eae92b5e99823afd892d1e
- https://github.com/MISP/MISP/commit/afbe08d256d609eee5195c5b0003cfb723ae7af1
