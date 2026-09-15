# [C] CVE-2024-44070

## Summary
Severity: Critical
Advisory: CVE-2024-44070
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-19
Source: https://osv.dev/vulnerability/CVE-2024-44070
Type: osv

## Details
An issue was discovered in FRRouting (FRR) through 10.1. bgp_attr_encap in bgpd/bgp_attr.c does not check the actual remaining stream length before taking the TLV value.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44070.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44070
- https://github.com/FRRouting/frr/pull/16497
