# [H] CVE-2025-61100

## Summary
Severity: High
Advisory: CVE-2025-61100
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-61100
Type: osv

## Details
FRRouting/frr from v2.0 through v10.4.1 was discovered to contain a NULL pointer dereference via the ospf_opaque_lsa_dump function at ospf_opaque.c. This vulnerability allows attackers to cause a Denial of Service (DoS) under specific malformed LSA conditions.

## References
- https://github.com/FRRouting/frr/pull/19480/commits/cda5ddac0940562d1dca7cbef34d0ce5b00f160b
- https://github.com/s1awwhy/BugList/blob/main/CVE-2025-61100.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61100.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61100
- https://github.com/FRRouting/frr/issues/19471
- https://github.com/FRRouting/frr/pull/19480
