# [C] Potential out-of-bound read during RTP/RTCP parsing in PJSIP

## Summary
Severity: Critical
Advisory: CVE-2022-21722
Aliases: GHSA-m66q-q64c-hv36
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-01-27
Source: https://osv.dev/vulnerability/CVE-2022-21722
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In version 2.11.1 and prior, there are various cases where it is possible that certain incoming RTP/RTCP packets can potentially cause out-of-bound read access. This issue affects all users that use PJMEDIA and accept incoming RTP/RTCP. A patch is available as a commit in the `master` branch. There are no known workarounds.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21722.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-m66q-q64c-hv36
- https://nvd.nist.gov/vuln/detail/CVE-2022-21722
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/22af44e68a0c7d190ac1e25075e1382f77e9397a
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
