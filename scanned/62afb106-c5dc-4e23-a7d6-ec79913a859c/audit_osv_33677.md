# [C] GetSimple CMS RCE in Edit component

## Summary
Severity: Critical
Advisory: CVE-2025-48492
Aliases: GHSA-g435-p72m-p582
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-48492
Type: osv

## Details
GetSimple CMS is a content management system. In versions starting from 3.3.16 to 3.3.21, an authenticated user with access to the Edit component can inject arbitrary PHP into a component file and execute it via a crafted query string, resulting in Remote Code Execution (RCE). This issue is set to be patched in version 3.3.22.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48492.json
- https://github.com/GetSimpleCMS-CE/GetSimpleCMS-CE/security/advisories/GHSA-g435-p72m-p582
- https://nvd.nist.gov/vuln/detail/CVE-2025-48492
