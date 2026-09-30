# [H] Stored Clickhouse SQL Injection Through Customer Usage Attribution

## Summary
Severity: High
Advisory: CVE-2026-18801
Aliases: GHSA-m2fw-9wxq-jgf5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:H/SC:H/SI:L/SA:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-18801
Type: osv

## Details
OpenMeter contains a stored, or second-order, SQL injection vulnerability in the handling of customer usage-attribution values.



An attacker who can create or update a customer can store a malicious value in the usageAttribution.key or usageAttribution.subjectKeys fields. When that customer is subsequently used in a meter or event query, OpenMeter inserts the stored value into a ClickHouse WITH map(...) expression using string concatenation.

OpenMeter versions from v1.0.0-beta.218 through v1.0.0-beta.231 are affected.

## References
- https://github.com/openmeterio/openmeter/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18801.json
- https://github.com/openmeterio/openmeter/security/advisories/GHSA-m2fw-9wxq-jgf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-18801
