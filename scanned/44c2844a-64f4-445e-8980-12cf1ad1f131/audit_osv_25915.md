# [M] CVE-2023-47235

## Summary
Severity: Medium
Advisory: CVE-2023-47235
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2023-47235
Type: osv

## Details
An issue was discovered in FRRouting FRR through 9.0.1. A crash can occur when a malformed BGP UPDATE message with an EOR is processed, because the presence of EOR does not lead to a treat-as-withdraw outcome.

## References
- https://github.com/FRRouting/frr/pull/14716/commits/6814f2e0138a6ea5e1f83bdd9085d9a77999900b
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47235.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47235
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
