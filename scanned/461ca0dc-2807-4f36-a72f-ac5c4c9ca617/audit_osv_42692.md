# [H] HashBrown CMS - OS Command Injection via Git Deployer Branch Field

## Summary
Severity: High
Advisory: CVE-2026-70375
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70375
Type: osv

## Details
HashBrown CMS through 1.4.6 contains an OS Command Injection vulnerability (CWE-78) in the Git deployer component. GitDeployer.pullRepo in src/Server/Entity/Deployer/GitDeployer.js executes AppService.exec, interpolating the configured branch value directly into a shell command with no escaping.

## References
- https://cve.turansec.uz/advisories/TRN-B571F773
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70375.json
- https://github.com/HashBrownCMS/hashbrown-cms
- https://nvd.nist.gov/vuln/detail/CVE-2026-70375
