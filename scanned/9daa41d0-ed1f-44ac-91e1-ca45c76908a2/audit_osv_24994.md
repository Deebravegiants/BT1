# [M] Server Side Request Forgery (SSRF) in USPS carrier integration configuration

## Summary
Severity: Medium
Advisory: CVE-2023-29291
Aliases: GHSA-5f79-vhr4-vw2r
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-15
Source: https://osv.dev/vulnerability/CVE-2023-29291
Type: osv

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by a Server-Side Request Forgery (SSRF) vulnerability that could lead to arbitrary file system read. An admin-privilege authenticated attacker can force the application to make arbitrary requests via injection of arbitrary URLs. Exploitation of this issue does not require user interaction.

## References
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29291.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29291
