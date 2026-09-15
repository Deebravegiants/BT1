# [M] BookWyrm through 0.9.1 Insecure Direct Object Reference in edit-readthrough Allows Tampering with Other Users' Reading Records

## Summary
Severity: Medium
Advisory: CVE-2026-86113
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86113
Type: osv

## Details
BookWyrm through 0.9.1 contains an authorization bypass vulnerability in the edit_readthrough function that allows authenticated users to modify other users' reading records. Attackers can exploit sequential ReadThrough IDs to overwrite arbitrary users' start dates, finish dates, progress, and progress mode, affecting reading statistics and exported data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86113
- https://www.vulncheck.com/advisories/bookwyrm-through-0.9.1-insecure-direct-object-reference-in-edit-readthrough-allows-tampering-with-other-users-reading-records
- https://github.com/bookwyrm-social/bookwyrm
- https://github.com/bookwyrm-social/bookwyrm/blob/v0.9.1/bookwyrm/views/status.py
- https://github.com/geo-chen/oss/blob/main/bookwyrm.md#finding-3-authenticated-idor-in-edit-readthrough-allows-tampering-with-other-users-reading-progress
