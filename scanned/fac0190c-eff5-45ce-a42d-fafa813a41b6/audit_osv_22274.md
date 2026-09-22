# [H] Potential heap buffer overflow when parsing DNS packets in PJSIP

## Summary
Severity: High
Advisory: CVE-2022-24793
Aliases: GHSA-p6g5-v97c-w5q4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-06
Source: https://osv.dev/vulnerability/CVE-2022-24793
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. A buffer overflow vulnerability in versions 2.12 and prior affects applications that use PJSIP DNS resolution. It doesn't affect PJSIP users who utilize an external resolver. This vulnerability is related to CVE-2023-27585. The difference is that this issue is in parsing the query record `parse_rr()`, while the issue in CVE-2023-27585 is in `parse_query()`. A patch is available in the `master` branch of the `pjsip/pjproject` GitHub repository. A workaround is to disable DNS resolution in PJSIP config (by setting `nameserver_count` to zero) or use an external resolver instead.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24793.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-p6g5-v97c-w5q4
- https://nvd.nist.gov/vuln/detail/CVE-2022-24793
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/9fae8f43accef8ea65d4a8ae9cdf297c46cfe29a
- https://lists.debian.org/debian-lts-announce/2022/05/msg00047.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
