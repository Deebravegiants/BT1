# [H] CVE-2023-38407

## Summary
Severity: High
Advisory: CVE-2023-38407
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-38407
Type: osv

## Details
bgpd/bgp_label.c in FRRouting (FRR) before 8.5 attempts to read beyond the end of the stream during labeled unicast parsing.

## References
- https://github.com/FRRouting/frr/compare/frr-8.5-rc...frr-8.5
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38407.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-38407
- https://github.com/FRRouting/frr/pull/12951
- https://github.com/FRRouting/frr/pull/12956
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
