# [H] CVE-2022-26129

## Summary
Severity: High
Advisory: CVE-2022-26129
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-03
Source: https://osv.dev/vulnerability/CVE-2022-26129
Type: osv

## Details
Buffer overflow vulnerabilities exist in FRRouting through 8.1.0 due to wrong checks on the subtlv length in the functions, parse_hello_subtlv, parse_ihu_subtlv, and parse_update_subtlv in babeld/message.c.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/26xxx/CVE-2022-26129.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-26129
- https://github.com/FRRouting/frr/issues/10503
