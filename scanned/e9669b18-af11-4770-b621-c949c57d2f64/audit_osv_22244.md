# [C] Adobe Commerce post-auth improper input validation leads to remote code execution

## Summary
Severity: Critical
Advisory: CVE-2022-24093
Aliases: GHSA-5xmp-7wg5-x68q
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-09-12
Source: https://osv.dev/vulnerability/CVE-2022-24093
Type: osv

## Details
Adobe Commerce versions 2.4.3-p1 (and earlier) and 2.3.7-p2 (and earlier) are affected by an improper input validation vulnerability. Exploitation of this issue does not require user interaction and could result in a post-authentication arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24093.json
- https://helpx.adobe.com/security/products/magento/apsb22-13.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-24093
