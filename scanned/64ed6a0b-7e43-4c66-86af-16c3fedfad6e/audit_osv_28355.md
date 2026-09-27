# [M] CVE-2024-31949

## Summary
Severity: Medium
Advisory: CVE-2024-31949
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-04-07
Source: https://osv.dev/vulnerability/CVE-2024-31949
Type: osv

## Details
In FRRouting (FRR) through 9.1, an infinite loop can occur when receiving a MP/GR capability as a dynamic capability because malformed data results in a pointer not advancing.

## References
- https://github.com/FRRouting/frr/pull/15640/commits/30a332dad86fafd2b0b6c61d23de59ed969a219b
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31949.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31949
- https://github.com/FRRouting/frr/pull/15640
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
