# [M] PJSIP vulnerable to heap buffer overflow when decoding STUN message

## Summary
Severity: Medium
Advisory: CVE-2022-23537
Aliases: GHSA-9pfh-r8x4-w26w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-12-20
Source: https://osv.dev/vulnerability/CVE-2022-23537
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. Buffer overread is possible when parsing a specially crafted STUN message with unknown attribute. The vulnerability affects applications that uses STUN including PJNATH and PJSUA-LIB. The patch is available as a commit in the master branch (2.13.1).

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23537.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-9pfh-r8x4-w26w
- https://nvd.nist.gov/vuln/detail/CVE-2022-23537
- https://github.com/pjsip/pjproject/commit/d8440f4d711a654b511f50f79c0445b26f9dd1e1
