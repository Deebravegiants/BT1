# [C] Gardener allows bypassing project secret validation which can lead to privilege escalation

## Summary
Severity: Critical
Advisory: GHSA-3hw7-qj9h-r835
CVE: CVE-2025-47283
CWE: CWE-20, CWE-269
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-3hw7-qj9h-r835
Type: github-advisory

## Affected
- Go: `github.com/gardener/gardener` — affected >=0 <1.116.4
- Go: `github.com/gardener/gardener` — affected >=1.117.0 <1.117.5
- Go: `github.com/gardener/gardener` — affected >=1.118.0 <1.118.2

## Details
A security vulnerability was discovered in Gardener that could allow a user with administrative privileges for a Gardener project to obtain control over the seed cluster(s) where their shoot clusters are managed.

### Am I Vulnerable?

This CVE affects all Gardener installations no matter of the public cloud provider(s) used for the seed clusters/shoot clusters.

### Affected Components

- `gardener/gardener`

### Affected Versions

- < v1.116.4
- < v1.117.5
- < v1.118.2
- < v1.119.0

### Fixed Versions

- &gt;= v1.116.4
- &gt;= v1.117.5
- &gt;= v1.118.2
- &gt;= v1.119.0

### How do I mitigate this vulnerability?

Update to a fixed version.

## References
- https://github.com/gardener/gardener/security/advisories/GHSA-3hw7-qj9h-r835
- https://nvd.nist.gov/vuln/detail/CVE-2025-47283
- https://github.com/gardener/gardener/commit/924b1575aae052bcda5a51fac8594d38fa3c41b0
- https://github.com/gardener/gardener/commit/b89cf2cd5067e82f364063d5241af73650a6e11d
- https://github.com/gardener/gardener/commit/bbd19b1dd3a31843d7b820172d37f75298dfaf8b
- https://github.com/gardener/gardener/commit/cf4e9887d83902216b85609caf563f7a9dd2de00
- https://github.com/gardener/gardener
