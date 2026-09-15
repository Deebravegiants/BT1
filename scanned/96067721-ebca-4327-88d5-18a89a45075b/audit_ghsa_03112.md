# [M] Information Exposure in jaeger

## Summary
Severity: Medium
Advisory: GHSA-gh32-pc56-4c96
CVE: CVE-2020-10750
CWE: CWE-200, CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-gh32-pc56-4c96
Type: github-advisory

## Affected
- Go: `github.com/jaegertracing/jaeger` — affected >=0 <1.18.1

## Details
Sensitive information written to a log file vulnerability was found in jaegertracing/jaeger before version 1.18.1 when the Kafka data store is used. This flaw allows an attacker with access to the container's log file to discover the Kafka credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10750
- https://github.com/jaegertracing/jaeger/commit/360c38bec3f9718ebba7ddbf0b409b05995f3ace
- https://bugzilla.redhat.com/show_bug.cgi?id=1838401
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10750
- https://github.com/jaegertracing/jaeger/releases/tag/v1.18.1
