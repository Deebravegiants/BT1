# [M] CVE-2022-40302

## Summary
Severity: Medium
Advisory: CVE-2022-40302
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-03
Source: https://osv.dev/vulnerability/CVE-2022-40302
Type: osv

## Details
An issue was discovered in bgpd in FRRouting (FRR) through 8.4. By crafting a BGP OPEN message with an option of type 0xff (Extended Length from RFC 9072), attackers may cause a denial of service (assertion failure and daemon restart, or out-of-bounds read). This is possible because of inconsistent boundary checks that do not account for reading 3 bytes (instead of 2) in this 0xff case.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40302.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40302
- https://www.debian.org/security/2023/dsa-5495
- https://github.com/FRRouting/frr/releases
- https://lists.debian.org/debian-lts-announce/2023/09/msg00020.html
