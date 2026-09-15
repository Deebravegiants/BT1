# [H] CVE-2021-42531

## Summary
Severity: High
Advisory: CVE-2021-42531
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-02
Source: https://osv.dev/vulnerability/CVE-2021-42531
Type: osv

## Details
XMP Toolkit SDK version 2021.07 (and earlier) is affected by a stack-based buffer overflow vulnerability potentially resulting in arbitrary code execution in the context of the current user. Exploitation requires user interaction in that a victim must open a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00003.html
- https://helpx.adobe.com/security/products/xmpcore/apsb21-108.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00032.html
