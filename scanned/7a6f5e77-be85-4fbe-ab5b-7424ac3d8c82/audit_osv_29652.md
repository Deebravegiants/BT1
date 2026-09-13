# [M] Adobe Commerce | Server-Side Request Forgery (SSRF) (CWE-918)

## Summary
Severity: Medium
Advisory: CVE-2024-45119
Aliases: GHSA-g9fm-wc6h-pvgj
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-45119
Type: osv

## Details
Adobe Commerce versions 2.4.7-p2, 2.4.6-p7, 2.4.5-p9, 2.4.4-p10 (and earlier) are affected by a Server-Side Request Forgery (SSRF) vulnerability that could lead to arbitrary file system read. An admin-privilege authenticated attacker can force the application to make arbitrary requests via injection of arbitrary URLs. Exploitation of this issue does not require user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45119.json
- https://helpx.adobe.com/security/products/magento/apsb24-73.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-45119
