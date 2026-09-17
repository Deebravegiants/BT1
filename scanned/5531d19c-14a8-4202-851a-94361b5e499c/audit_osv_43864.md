# [M] JimuReport Unauthenticated Report Listing and Share Token Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-75479
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75479
Type: osv

## Details
JimuReport contains an authentication bypass vulnerability in the report folder template listing endpoint that allows unauthenticated attackers to enumerate all reports and retrieve share tokens. Attackers can use disclosed share tokens to access protected report endpoints and retrieve full report definitions including embedded SQL statements and live query data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75479.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75479
- https://www.vulncheck.com/advisories/jimureport-unauthenticated-report-listing-and-share-token-disclosure
- https://github.com/jeecgboot/jimureport/issues/4695
- https://github.com/jeecgboot/jimureport
