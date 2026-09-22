# [M] CVE-2021-40716

## Summary
Severity: Medium
Advisory: CVE-2021-40716
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/CVE-2021-40716
Type: osv

## Details
XMP Toolkit SDK versions 2021.07 (and earlier) are affected by an out-of-bounds read vulnerability that could lead to disclosure of sensitive memory. An attacker could leverage this vulnerability to bypass mitigations such as ASLR. Exploitation of this issue requires user interaction in that a victim must open a malicious file.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00003.html
- https://helpx.adobe.com/security/products/xmpcore/apsb21-85.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00032.html
