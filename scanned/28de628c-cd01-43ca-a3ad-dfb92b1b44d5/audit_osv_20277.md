# [M] CVE-2021-32686

## Summary
Severity: Medium
Advisory: CVE-2021-32686
Aliases: GHSA-cv8x-p47p-99wr
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-23
Source: https://osv.dev/vulnerability/CVE-2021-32686
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In PJSIP before version 2.11.1, there are a couple of issues found in the SSL socket. First, a race condition between callback and destroy, due to the accepted socket having no group lock. Second, the SSL socket parent/listener may get destroyed during handshake. Both issues were reported to happen intermittently in heavy load TLS connections. They cause a crash, resulting in a denial of service. These are fixed in version 2.11.1.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/pjsip/pjproject/releases/tag/2.11.1
- https://github.com/pjsip/pjproject/security/advisories/GHSA-cv8x-p47p-99wr
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2021/dsa-4999
- https://github.com/pjsip/pjproject/commit/d5f95aa066f878b0aef6a64e60b61e8626e664cd
- https://github.com/pjsip/pjproject/pull/2716
