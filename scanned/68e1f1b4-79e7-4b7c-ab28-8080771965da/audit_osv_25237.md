# [H] Users can add themselves to any organization in CloudExplorer Lite

## Summary
Severity: High
Advisory: CVE-2023-32316
Aliases: GHSA-cp3j-437h-4vwj
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32316
Type: osv

## Details
CloudExplorer Lite is an open source cloud management tool. In affected versions users can add themselves to any organization in CloudExplorer Lite. This is due to a missing permission check on the user profile. It is recommended to upgrade the version to v1.1.0. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32316.json
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/security/advisories/GHSA-cp3j-437h-4vwj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32316
