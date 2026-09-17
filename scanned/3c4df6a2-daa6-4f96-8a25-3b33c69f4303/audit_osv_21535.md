# [H] CVE-2021-43804

## Summary
Severity: High
Advisory: CVE-2021-43804
Aliases: GHSA-3qx3-cg72-wrh9
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/CVE-2021-43804
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In affected versions if the incoming RTCP BYE message contains a reason's length, this declared length is not checked against the actual received packet size, potentially resulting in an out-of-bound read access. This issue affects all users that use PJMEDIA and RTCP. A malicious actor can send a RTCP BYE message with an invalid reason length. Users are advised to upgrade as soon as possible. There are no known workarounds.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/8b621f192cae14456ee0b0ade52ce6c6f258af1e
- https://github.com/pjsip/pjproject/security/advisories/GHSA-3qx3-cg72-wrh9
