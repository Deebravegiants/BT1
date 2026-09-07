# [C] Gardener External DNS Management allows malicious google credential in DNS secret to lead to privilege escalation

## Summary
Severity: Critical
Advisory: GHSA-xwgg-m7fx-83wx
CVE: CVE-2025-47282
CWE: CWE-20, CWE-269
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-19
Source: https://github.com/advisories/GHSA-xwgg-m7fx-83wx
Type: github-advisory

## Affected
- Go: `github.com/gardener/external-dns-management` — affected >=0 <0.23.6
- Go: `github.com/gardener/gardener-extension-shoot-dns-service` — affected >=0

## Details
A security vulnerability was discovered in Gardener that could allow a user with administrative privileges for a Gardener project or a user with administrative privileges for a shoot cluster, including administrative privileges for a single namespace of the shoot cluster, to obtain control over the seed cluster where the shoot cluster is managed.

### Am I Vulnerable?

This CVE affects all Gardener installations no matter of the public cloud provider(s) used for the seed clusters/shoot clusters.

### Affected Components

- `gardener/external-dns-management`

### Affected Versions

- < 0.23.6

### Fixed Versions

- &gt;= 0.23.6

### Important

The `external-dns-management` component may also be deployed on the seeds by the https://github.com/gardener/gardener-extension-shoot-dns-service extension when the extension is enabled. In this case, all versions of the `shoot-dns-service` extension `<= v1.60.0` are affected by this vulnerability.

### How do I mitigate this vulnerability?

Update to a fixed version.

## References
- https://github.com/gardener/external-dns-management/security/advisories/GHSA-xwgg-m7fx-83wx
- https://nvd.nist.gov/vuln/detail/CVE-2025-47282
- https://github.com/gardener/external-dns-management
