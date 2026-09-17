# [H] CVE-2023-47234

## Summary
Severity: High
Advisory: CVE-2023-47234
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-47234
Type: osv

## Details
An issue was discovered in FRRouting FRR through 9.0.1. A crash can occur when processing a crafted BGP UPDATE message with a MP_UNREACH_NLRI attribute and additional NLRI data (that lacks mandatory path attributes).

## References
- https://github.com/FRRouting/frr/pull/14716/commits/c37119df45bbf4ef713bc10475af2ee06e12f3bf
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47234.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47234
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
