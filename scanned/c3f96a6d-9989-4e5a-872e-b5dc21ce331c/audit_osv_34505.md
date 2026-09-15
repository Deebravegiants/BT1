# [H] CVE-2025-61107

## Summary
Severity: High
Advisory: CVE-2025-61107
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-61107
Type: osv

## Details
FRRouting/frr from v4.0 through v10.4.1 was discovered to contain a NULL pointer dereference via the show_vty_ext_pref_pref_sid function at ospf_ext.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted LSA Update packet.

## References
- https://github.com/FRRouting/frr/pull/19480/commits/fdd957408605d4a1766225630aafc7e6b7c3daf3
- https://github.com/s1awwhy/BugList/blob/main/CVE-2025-61107.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61107.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61107
- https://github.com/FRRouting/frr/issues/19471
- https://github.com/FRRouting/frr/pull/19480
