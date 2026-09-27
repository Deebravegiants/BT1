# [C] Potential stack buffer overflow when parsing message as a STUN client

## Summary
Severity: Critical
Advisory: CVE-2022-31031
Aliases: GHSA-26j7-ww69-c4qj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-07
Source: https://osv.dev/vulnerability/CVE-2022-31031
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In versions prior to and including 2.12.1 a stack buffer overflow vulnerability affects PJSIP users that use STUN in their applications, either by: setting a STUN server in their account/media config in PJSUA/PJSUA2 level, or directly using `pjlib-util/stun_simple` API. A patch is available in commit 450baca which should be included in the next release. There are no known workarounds for this issue.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31031.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-26j7-ww69-c4qj
- https://nvd.nist.gov/vuln/detail/CVE-2022-31031
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2023/dsa-5358
- https://github.com/pjsip/pjproject/commit/450baca94f475345542c6953832650c390889202
- https://lists.debian.org/debian-lts-announce/2023/02/msg00029.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
