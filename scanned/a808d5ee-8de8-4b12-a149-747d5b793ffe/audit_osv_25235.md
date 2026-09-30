# [H] The CloudExplorer Lite missing permissions check

## Summary
Severity: High
Advisory: CVE-2023-32311
Aliases: GHSA-hxjq-g9qv-pwq5
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32311
Type: osv

## Details
CloudExplorer Lite is an open source cloud management platform. In CloudExplorer Lite prior to version 1.1.0 users organization/workspace permissions are not properly checked. This allows users to add themselves to any organization. This vulnerability has been fixed in v1.1.0. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32311.json
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/security/advisories/GHSA-hxjq-g9qv-pwq5
- https://nvd.nist.gov/vuln/detail/CVE-2023-32311
