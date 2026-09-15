# [M] Leantime all versions prior to and 3.6.2 Broken Access Control via tickets.getMilestone JSON-RPC

## Summary
Severity: Medium
Advisory: CVE-2026-66412
Aliases: GHSA-wv69-xr82-phr6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-66412
Type: osv

## Details
Leantime 3.6.2 and prior contains a broken access control vulnerability that allows authenticated users to read milestone data from projects they are not assigned to by supplying arbitrary integer milestone IDs to the tickets.getMilestone JSON-RPC endpoint. Attackers can enumerate integer milestone IDs through the JSON-RPC API to access project planning information, milestone titles, descriptions, and timelines across all projects on the instance regardless of project membership.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66412.json
- https://github.com/Leantime/leantime/security/advisories/GHSA-wv69-xr82-phr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-66412
- https://www.vulncheck.com/advisories/leantime-all-versions-prior-to-and-broken-access-control-via-tickets-getmilestone-json-rpc
- https://github.com/Leantime/leantime/pull/3657
- https://github.com/Leantime/leantime/commit/68898eeb914882a21797523f2782914795bc67ae
