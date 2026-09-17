# [H] CVE-2021-41160

## Summary
Severity: High
Advisory: CVE-2021-41160
Aliases: GHSA-7c9r-6r2q-93qg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-41160
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol (RDP), released under the Apache license. In affected versions a malicious server might trigger out of bound writes in a connected client. Connections using GDI or SurfaceCommands to send graphics updates to the client might send `0` width/height or out of bound rectangles to trigger out of bound writes. With `0` width or heigth the memory allocation will be `0` but the missing bounds checks allow writing to the pointer at this (not allocated) region. This issue has been patched in FreeRDP 2.4.1.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DWJXQOWKNR7O5HM2HFJOM4GBUFPTE3RG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WIZUPVRGCWUDAPDOQVUGUIYUO7UWKMXX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZXCR73EDVPLI6TRWRAWJCJ7OBYDKBB74/
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-7c9r-6r2q-93qg
- https://security.gentoo.org/glsa/202210-24
