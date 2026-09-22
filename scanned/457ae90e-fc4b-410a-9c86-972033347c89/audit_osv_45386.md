# [M] JLSEC-2026-1108

## Summary
Severity: Medium
Advisory: JLSEC-2026-1108
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1108
Type: osv

## Affected
- Julia: `LibRaw_jll` — affected >=0 <0.22.1+0

## Details
A flaw was found in LibRaw. A heap-buffer-overflow in `raw2image_ex()` caused by a maliciously crafted file may lead to an application crash.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2188240
- https://bugzilla.redhat.com/show_bug.cgi?id=2188240
- https://github.com/LibRaw/LibRaw/issues/557
- https://github.com/LibRaw/LibRaw/issues/557
- https://lists.debian.org/debian-lts-announce/2023/05/msg00025.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00025.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AGZ6XF5WTPJ4GLXQ62JVRDZSVSJHXNQU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AGZ6XF5WTPJ4GLXQ62JVRDZSVSJHXNQU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E5ZJ3UBTJBZHNPJQFOSGM5L7WAHHE2GY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E5ZJ3UBTJBZHNPJQFOSGM5L7WAHHE2GY/
- https://security.gentoo.org/glsa/202312-08
- https://security.gentoo.org/glsa/202312-08
- https://www.debian.org/security/2023/dsa-5412
- https://www.debian.org/security/2023/dsa-5412
