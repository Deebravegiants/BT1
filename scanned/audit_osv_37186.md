# [M] SuiteCRM has Relative Path Traversal via ModuleBuilder Modules ExportCustom Action

## Summary
Severity: Medium
Advisory: CVE-2026-29098
Aliases: GHSA-6858-fhw5-56gf
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29098
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, the `action_exportCustom` function in `modules/ModuleBuilder/controller.php` fails to properly neutralize path traversal sequences in the `$modules` and `$name` parameters. Both parameters later reach the `exportCustom` function in `modules/ModuleBuilder/MB/MBPackage.php` where they are both utilized in constructing s paths for file reading and writing. As such, it is possible for a user with access to the ModuleBuilder module, generally an administrator, to craft a request that can copy the content of any readable directory on the underlying host into the web root, making them readable. As the `ModuleBuilder` module is part of both major versions 7 and 8, both current major versions are affected. This vulnerability allows an attacker to copy any readable directory into the web root. This includes system files like the content of `/etc, or the root directory of the web server, potentially exposing secrets and environment variables. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29098.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-6858-fhw5-56gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-29098
