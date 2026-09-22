# [M] Adobe Commerce | Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') (CWE-22)

## Summary
Severity: Medium
Advisory: CVE-2024-39406
Aliases: GHSA-6pxh-2557-5cj5
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-08-14
Source: https://osv.dev/vulnerability/CVE-2024-39406
Type: osv

## Details
Adobe Commerce versions 2.4.7-p1, 2.4.6-p6, 2.4.5-p8, 2.4.4-p9 and earlier are affected by an Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') vulnerability that could lead to arbitrary file system read. An admin attacker could exploit this vulnerability to gain access to files and directories that are outside the restricted directory. Exploitation of this issue does not require user interaction and scope is changed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39406.json
- https://helpx.adobe.com/security/products/magento/apsb24-61.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-39406
