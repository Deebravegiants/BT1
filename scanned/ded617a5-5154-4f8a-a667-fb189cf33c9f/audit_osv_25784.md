# [H] CloudExplorer Lite permission bypass vulnerability

## Summary
Severity: High
Advisory: CVE-2023-44397
Aliases: GHSA-fqxr-7g94-vrfj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-10-30
Source: https://osv.dev/vulnerability/CVE-2023-44397
Type: osv

## Details
CloudExplorer Lite is an open source, lightweight cloud management platform. Prior to version 1.4.1, the gateway filter of CloudExplorer Lite uses a controller with path starting with `matching/API/`, which can cause a permission bypass. Version 1.4.1 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44397.json
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/security/advisories/GHSA-fqxr-7g94-vrfj
- https://nvd.nist.gov/vuln/detail/CVE-2023-44397
