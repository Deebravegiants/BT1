# [M] CVE-2024-31948

## Summary
Severity: Medium
Advisory: CVE-2024-31948
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-07
Source: https://osv.dev/vulnerability/CVE-2024-31948
Type: osv

## Details
In FRRouting (FRR) through 9.1, an attacker using a malformed Prefix SID attribute in a BGP UPDATE packet can cause the bgpd daemon to crash.

## References
- https://github.com/FRRouting/frr/pull/15628/commits/ba6a8f1a31e1a88df2de69ea46068e8bd9b97138
- https://lists.debian.org/debian-lts-announce/2024/09/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31948.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31948
- https://github.com/FRRouting/frr/pull/15628
- https://lists.debian.org/debian-lts-announce/2024/04/msg00019.html
