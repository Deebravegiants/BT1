# [C] Arbitrary Code Execution in Language Servers for AWS

## Summary
Severity: Critical
Advisory: CVE-2026-12957
Aliases: GHSA-xhcr-j4j9-3gh7
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-12957
Type: osv

## Details
Improper trust boundary enforcement in Language Servers for AWS before version 1.65.0 on all supported platforms may allow a for arbitrary code execution. If a local user opens a maliciously crafted workspace, any commands within the project configuration files may be automatically executed. This issue requires the user to trust the workspace when prompted.



To remediate this issue, users should upgrade to Language Servers for AWS version 1.65.0 or higher.

## References
- https://aws.amazon.com/security/security-bulletins/2026-047-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12957.json
- https://github.com/aws/language-servers/security/advisories/GHSA-xhcr-j4j9-3gh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-12957
