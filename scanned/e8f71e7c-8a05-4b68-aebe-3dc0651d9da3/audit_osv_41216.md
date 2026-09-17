# [M] JimuReport 2.5.0 - Unauthenticated Report Export via /jmreport/auto/export

## Summary
Severity: Medium
Advisory: CVE-2026-58375
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58375
Type: osv

## Details
JimuReport through 2.5.0 exposes the POST /jmreport/auto/export endpoint without authentication: the handler is annotated @JimuNoLoginRequired, so JimuReportTokenInterceptor skips all authentication and authorization, and the export service streams the rendered report for any supplied report id without verifying the auto-export configuration flag. An unauthenticated remote attacker can enumerate Snowflake report identifiers and export the full contents of any report, including the data returned by the report configured SQL queries and any credentials embedded in its data sources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58375.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58375
- https://www.vulncheck.com/advisories/jimureport-unauthenticated-report-export-via-jmreport-auto-export
- https://github.com/jeecgboot/jimureport
- https://github.com/jeecgboot/jimureport/issues/4694
