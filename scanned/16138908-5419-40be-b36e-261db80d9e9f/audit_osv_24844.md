# [H] CVE-2023-27585

## Summary
Severity: High
Advisory: CVE-2023-27585
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2023-27585
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. A buffer overflow vulnerability in versions 2.13 and prior affects applications that use PJSIP DNS resolver. It doesn't affect PJSIP users who do not utilise PJSIP DNS resolver. This vulnerability is related to CVE-2022-24793. The difference is that this issue is in parsing the query record `parse_query()`, while the issue in CVE-2022-24793 is in `parse_rr()`. A patch is available as commit `d1c5e4d` in the `master` branch. A workaround is to disable DNS resolution in PJSIP config (by setting `nameserver_count` to zero) or use an external resolver implementation instead.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://www.pjsip.org/pjlib-util/docs/html/group__PJ__DNS__RESOLVER.htm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27585.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-p6g5-v97c-w5q4
- https://github.com/pjsip/pjproject/security/advisories/GHSA-q9cp-8wcq-7pfr
- https://nvd.nist.gov/vuln/detail/CVE-2023-27585
- https://www.debian.org/security/2023/dsa-5438
- https://github.com/pjsip/pjproject/commit/d1c5e4da5bae7f220bc30719888bb389c905c0c5
- https://lists.debian.org/debian-lts-announce/2023/04/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
