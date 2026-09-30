# [M] CVE-2022-34375

## Summary
Severity: Medium
Advisory: CVE-2022-34375
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-30
Source: https://osv.dev/vulnerability/CVE-2022-34375
Type: osv

## Details
Dell Container Storage Modules 1.2 contains a path traversal vulnerability in goiscsi and gobrick libraries. A remote authenticated malicious user with low privileges could exploit this vulnerability leading to unintentional access to path outside of restricted directory.

## References
- https://www.dell.com/support/kbdoc/en-us/000201835/dsa-2022-202-dell-container-storage-modules-security-update-for-multiple-vulnerabilities
