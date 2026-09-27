# [H] Adobe Commerce XML Injection Arbitrary file system read

## Summary
Severity: High
Advisory: CVE-2023-22247
Aliases: GHSA-2444-8gj8-6fmx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-22247
Type: osv

## Details
Adobe Commerce versions 2.4.4-p2 (and earlier) and 2.4.5-p1 (and earlier) are affected by an XML Injection vulnerability that could lead to arbitrary file system read. An unauthenticated attacker can force the application to make arbitrary requests via injection of arbitrary URLs. Exploitation of this issue does not require user interaction.

## References
- https://helpx.adobe.com/security/products/magento/apsb23-17.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22247.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22247
