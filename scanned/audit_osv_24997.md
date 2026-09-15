# [M] [Cloud] Customer suspects IDOR vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-29296
Aliases: GHSA-3qr4-w96f-672v
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-15
Source: https://osv.dev/vulnerability/CVE-2023-29296
Type: osv

## Details
Adobe Commerce versions 2.4.6 (and earlier), 2.4.5-p2 (and earlier) and 2.4.4-p3 (and earlier) are affected by an Incorrect Authorization vulnerability that could result in a security feature bypass. A low-privileged attacker could leverage this vulnerability to modify a minor functionality of another user's data. Exploitation of this issue does not require user interaction.

## References
- https://helpx.adobe.com/security/products/magento/apsb23-35.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29296.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29296
