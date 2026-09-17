# [C] CVE-2021-37706

## Summary
Severity: Critical
Advisory: CVE-2021-37706
Aliases: GHSA-2qpg-f6wf-w984
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-22
Source: https://osv.dev/vulnerability/CVE-2021-37706
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In affected versions if the incoming STUN message contains an ERROR-CODE attribute, the header length is not checked before performing a subtraction operation, potentially resulting in an integer underflow scenario. This issue affects all users that use STUN. A malicious actor located within the victim’s network may forge and send a specially crafted UDP (STUN) message that could remotely execute arbitrary code on the victim’s machine. Users are advised to upgrade as soon as possible. There are no known workarounds.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- http://packetstormsecurity.com/files/166225/Asterisk-Project-Security-Advisory-AST-2022-004.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- http://seclists.org/fulldisclosure/2022/Mar/0
- https://github.com/pjsip/pjproject/commit/15663e3f37091069b8c98a7fce680dc04bc8e865
- https://github.com/pjsip/pjproject/security/advisories/GHSA-2qpg-f6wf-w984
