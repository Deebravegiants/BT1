# [M] CVE-2026-37458

## Summary
Severity: Medium
Advisory: CVE-2026-37458
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-37458
Type: osv

## Details
Missing input validation in the MP_REACH_NLRI component of FRRouting (FRR) stable/10.0 to stable/10.6 allows authenticated attackers to cause a Denial of Service (DoS) via supplying a crafted UPDATE message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37458.json
- https://github.com/mertsatilmaz/vulnerability-research/blob/main/advisories/CVE-2026-36365.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37458
- https://github.com/FRRouting/frr/commit/8102a8aeceb9f86fdfe1f80cd77080522bab69c8
