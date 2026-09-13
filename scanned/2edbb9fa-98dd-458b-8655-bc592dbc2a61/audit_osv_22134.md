# [C] Out-of-bounds read in multipart parsing in PJSIP

## Summary
Severity: Critical
Advisory: CVE-2022-21723
Aliases: GHSA-7fw8-54cv-r7pm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-01-27
Source: https://osv.dev/vulnerability/CVE-2022-21723
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In versions 2.11.1 and prior, parsing an incoming SIP message that contains a malformed multipart can potentially cause out-of-bound read access. This issue affects all PJSIP users that accept SIP multipart. The patch is available as commit in the `master` branch. There are no known workarounds.

## References
- http://packetstormsecurity.com/files/166227/Asterisk-Project-Security-Advisory-AST-2022-006.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21723.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-7fw8-54cv-r7pm
- https://nvd.nist.gov/vuln/detail/CVE-2022-21723
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/077b465c33f0aec05a49cd2ca456f9a1b112e896
- http://seclists.org/fulldisclosure/2022/Mar/2
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
