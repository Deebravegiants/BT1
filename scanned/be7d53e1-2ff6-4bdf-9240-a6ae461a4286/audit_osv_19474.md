# [M] CVE-2021-21375

## Summary
Severity: Medium
Advisory: CVE-2021-21375
Aliases: GHSA-hvq6-f89p-frvp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2021-21375
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In PJSIP version 2.10 and earlier, after an initial INVITE has been sent, when two 183 responses are received, with the first one causing negotiation failure, a crash will occur. This results in a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00023.html
- https://lists.debian.org/debian-lts-announce/2021/05/msg00020.html
- https://security.gentoo.org/glsa/202107-42
- https://github.com/pjsip/pjproject/commit/97b3d7addbaa720b7ddb0af9bf6f3e443e664365
- https://github.com/pjsip/pjproject/security/advisories/GHSA-hvq6-f89p-frvp
