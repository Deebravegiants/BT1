# [M] CVE-2021-42528

## Summary
Severity: Medium
Advisory: CVE-2021-42528
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2021-42528
Type: osv

## Details
XMP Toolkit 2021.07 (and earlier) is affected by a Null pointer dereference vulnerability when parsing a specially crafted file. An unauthenticated attacker could leverage this vulnerability to achieve an application denial-of-service in the context of the current user. Exploitation of this issue requires user interaction in that a victim must open a malicious file.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00003.html
- https://helpx.adobe.com/security/products/xmpcore/apsb21-108.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00032.html
