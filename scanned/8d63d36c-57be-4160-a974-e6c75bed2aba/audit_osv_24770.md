# [M] Error based file extraction via PHP filter chains during product bulk import logic

## Summary
Severity: Medium
Advisory: CVE-2023-26367
Aliases: GHSA-9mx6-4gg4-85xj
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-13
Source: https://osv.dev/vulnerability/CVE-2023-26367
Type: osv

## Details
Adobe Commerce versions 2.4.7-beta1 (and earlier), 2.4.6-p2 (and earlier), 2.4.5-p4 (and earlier) and 2.4.4-p5 (and earlier) are affected by an Improper Input Validation vulnerability that could lead to arbitrary file system read by an admin-privilege authenticated attacker. Exploitation of this issue does not require user interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26367.json
- https://helpx.adobe.com/security/products/magento/apsb23-50.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-26367
