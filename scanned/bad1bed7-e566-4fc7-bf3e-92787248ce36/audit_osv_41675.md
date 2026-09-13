# [M] Open Event Server 1.19.1 Unauthenticated Member Roster Export via CSV Export Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-63101
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-63101
Type: osv

## Details
Open Event Server through 1.19.1 contains a missing authentication vulnerability that allows unauthenticated attackers to export the complete member roster of any group, including email addresses, names, join dates, and roles, by submitting requests to the group followers CSV export endpoint which lacks any authentication decorator. Attackers can enumerate sequential group IDs via brute-force, trigger an export via the unauthenticated POST endpoint, then poll the unauthenticated task status endpoint until completion to retrieve a download URL containing the full member CSV.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63101.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63101
- https://www.vulncheck.com/advisories/open-event-server-unauthenticated-member-roster-export-via-csv-export-endpoint
- https://github.com/fossasia/open-event-server
- https://github.com/geo-chen/oss/blob/main/open-event-server.md
