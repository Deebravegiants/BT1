# [C] Heap-based Buffer Overflow and Out-of-bounds Write in Sofia-SIP

## Summary
Severity: Critical
Advisory: CVE-2022-31003
Aliases: GHSA-8w5j-6g2j-pxcp
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-31003
Type: osv

## Details
Sofia-SIP is an open-source Session Initiation Protocol (SIP) User-Agent library. Prior to version 1.13.8, when parsing each line of a sdp message, `rest = record + 2` will access the memory behind `\0` and cause an out-of-bounds write. An attacker can send a message with evil sdp to FreeSWITCH, causing a crash or more serious consequence, such as remote code execution. Version 1.13.8 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31003.json
- https://github.com/freeswitch/sofia-sip/security/advisories/GHSA-8w5j-6g2j-pxcp
- https://nvd.nist.gov/vuln/detail/CVE-2022-31003
- https://security.gentoo.org/glsa/202210-18
- https://www.debian.org/security/2023/dsa-5410
- https://github.com/freeswitch/sofia-sip/commit/907f2ac0ee504c93ebfefd676b4632a3575908c9
- https://lists.debian.org/debian-lts-announce/2022/09/msg00001.html
