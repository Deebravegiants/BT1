# [H] CVE-2025-61099

## Summary
Severity: High
Advisory: CVE-2025-61099
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-61099
Type: osv

## Details
FRRouting/frr from v2.0 through v10.4.1 was discovered to contain a NULL pointer dereference via the opaque_info_detail function at ospf_opaque.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted LS Update packet.

## References
- https://github.com/FRRouting/frr/pull/19480/commits/0042fbe8ca5aba866b4f0d166e54066bba5ab14e
- https://github.com/s1awwhy/BugList/blob/main/CVE-2025-61099.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61099.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61099
- https://github.com/FRRouting/frr/issues/19471
- https://github.com/FRRouting/frr/pull/19480
