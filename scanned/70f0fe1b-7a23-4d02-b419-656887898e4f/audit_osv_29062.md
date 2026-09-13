# [C] Adobe Commerce | Unrestricted Upload of File with Dangerous Type (CWE-434)

## Summary
Severity: Critical
Advisory: CVE-2024-39397
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/CVE-2024-39397
Type: osv

## Details
Adobe Commerce versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Unrestricted Upload of File with Dangerous Type vulnerability that could result in arbitrary code execution by an attacker. An attacker could exploit this vulnerability by uploading a malicious file which can then be executed on the server. Exploitation of this issue does not require user interaction, but attack complexity is high and scope is changed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39397.json
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-39397
