# [H] Use after free in PJSIP

## Summary
Severity: High
Advisory: CVE-2022-23608
Aliases: GHSA-ffff-m5fm-qm62
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-22
Source: https://osv.dev/vulnerability/CVE-2022-23608
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE. In versions up to and including 2.11.1 when in a dialog set (or forking) scenario, a hash key shared by multiple UAC dialogs can potentially be prematurely freed when one of the dialogs is destroyed . The issue may cause a dialog set to be registered in the hash table multiple times (with different hash keys) leading to undefined behavior such as dialog list collision which eventually leading to endless loop. A patch is available in commit db3235953baa56d2fb0e276ca510fefca751643f which will be included in the next release. There are no known workarounds for this issue.

## References
- http://packetstormsecurity.com/files/166226/Asterisk-Project-Security-Advisory-AST-2022-005.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23608.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-ffff-m5fm-qm62
- https://nvd.nist.gov/vuln/detail/CVE-2022-23608
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/db3235953baa56d2fb0e276ca510fefca751643f
- http://seclists.org/fulldisclosure/2022/Mar/1
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00040.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
