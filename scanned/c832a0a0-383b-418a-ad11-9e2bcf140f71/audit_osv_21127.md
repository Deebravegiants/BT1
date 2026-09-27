# [M] CVE-2021-40732

## Summary
Severity: Medium
Advisory: CVE-2021-40732
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2021-10-13
Source: https://osv.dev/vulnerability/CVE-2021-40732
Type: osv

## Details
XMP Toolkit version 2020.1 (and earlier) is affected by a null pointer dereference vulnerability that could result in leaking data from certain memory locations and causing a local denial of service in the context of the current user. User interaction is required to exploit this vulnerability in that the victim will need to open a specially crafted MXF file.

## References
- https://lists.debian.org/debian-lts-announce/2025/08/msg00003.html
- https://helpx.adobe.com/security/products/xmpcore/apsb21-85.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00032.html
