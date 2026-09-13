# [H] CVE-2023-37024

## Summary
Severity: High
Advisory: CVE-2023-37024
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2023-37024
Type: osv

## Details
A reachable assertion in the Mobile Management Entity (MME) of Magma versions <= 1.8.0 (fixed in v1.9 commit 08472ba98b8321f802e95f5622fa90fec2dea486) allows remote attackers to crash the MME with an unauthenticated cellphone by sending a NAS packet containing an `Emergency Number List` Information Element.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37024.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37024
