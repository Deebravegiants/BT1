# [M] Weak passwords allowed in cloudexplorer-lite

## Summary
Severity: Medium
Advisory: CVE-2023-34240
Aliases: GHSA-px4m-5j22-5mw4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-06-27
Source: https://osv.dev/vulnerability/CVE-2023-34240
Type: osv

## Details
Cloudexplorer-lite is an open source cloud software stack. Weak passwords can be easily guessed and are an easy target for brute force attacks. This can lead to an authentication system failure and compromise system security. Versions of cloudexplorer-lite prior to 1.2.0 did not enforce strong passwords. This vulnerability has been fixed in version 1.2.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34240.json
- https://github.com/CloudExplorer-Dev/CloudExplorer-Lite/security/advisories/GHSA-px4m-5j22-5mw4
- https://nvd.nist.gov/vuln/detail/CVE-2023-34240
