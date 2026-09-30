# [C] Gardener allows metadata injection for a project secret which can lead to privilege escalation

## Summary
Severity: Critical
Advisory: GHSA-9x73-87fh-54w9
CVE: CVE-2025-47284
CWE: CWE-150
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-9x73-87fh-54w9
Type: github-advisory

## Affected
- Go: `github.com/gardener/gardener` — affected >=0 <1.116.4
- Go: `github.com/gardener/gardener` — affected >=1.117.0 <1.117.5
- Go: `github.com/gardener/gardener` — affected >=1.118.0 <1.118.2

## Details
A security vulnerability was discovered in the `gardenlet` component of Gardener. It could allow a user with administrative privileges for a Gardener project to obtain control over the seed cluster(s) where their shoot clusters are managed.

### Am I Vulnerable?

This CVE affects all Gardener installations where https://github.com/gardener/gardener-extension-provider-gcp is in use.

### Affected Components

- `gardener/gardener` (`gardenlet`)

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
- https://github.com/gardener/gardener/security/advisories/GHSA-9x73-87fh-54w9
- https://nvd.nist.gov/vuln/detail/CVE-2025-47284
- https://github.com/gardener/gardener
