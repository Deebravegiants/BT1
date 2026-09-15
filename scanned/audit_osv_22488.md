# [H] Out-of-bounds Read in Sofia-SIP

## Summary
Severity: High
Advisory: CVE-2022-31001
Aliases: GHSA-79jq-hh82-cv9g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-31001
Type: osv

## Details
Sofia-SIP is an open-source Session Initiation Protocol (SIP) User-Agent library. Prior to version 1.13.8, an attacker can send a message with evil sdp to FreeSWITCH, which may cause crash. This type of crash may be caused by `#define MATCH(s, m) (strncmp(s, m, n = sizeof(m) - 1) == 0)`, which will make `n` bigger and trigger out-of-bound access when `IS_NON_WS(s[n])`. Version 1.13.8 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31001.json
- https://github.com/freeswitch/sofia-sip/security/advisories/GHSA-79jq-hh82-cv9g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31001
- https://security.gentoo.org/glsa/202210-18
- https://www.debian.org/security/2023/dsa-5410
- https://github.com/freeswitch/sofia-sip/commit/a99804b336d0e16d26ab7119d56184d2d7110a36
- https://lists.debian.org/debian-lts-announce/2022/09/msg00001.html
