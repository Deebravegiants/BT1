# [C] Couchbase Sync Gateway admin credentials not verified when using X.509 client cert authentication

## Summary
Severity: Critical
Advisory: GHSA-9266-j9v3-q4j5
CVE: CVE-2022-32563
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-9266-j9v3-q4j5
Type: github-advisory

## Affected
- PyPI: `couchbase` — affected >=3.0.0 <3.0.2

## Details
An issue was discovered in Couchbase Sync Gateway 3.x before 3.0.2. Admin credentials are not verified when using X.509 client-certificate authentication from Sync Gateway to Couchbase Server. When Sync Gateway is configured to authenticate with Couchbase Server using X.509 client certificates, the admin credentials provided to the Admin REST API are ignored, resulting in privilege escalation for unauthenticated users. The Public REST API is not impacted by this issue. A workaround is to replace X.509 certificate based authentication with Username and Password authentication inside the bootstrap configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32563
- https://forums.couchbase.com/tags/security
- https://github.com/pypa/advisory-database/tree/main/vulns/couchbase/PYSEC-2022-207.yaml
- https://www.couchbase.com/alerts
- https://www.couchbase.com/alerts/#CVE-2022-32563
