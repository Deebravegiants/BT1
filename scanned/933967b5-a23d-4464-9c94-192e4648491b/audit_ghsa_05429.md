# [H] Skipper Ingress Controller Allows Unauthorized Access to Internal Services via ExternalName

## Summary
Severity: High
Advisory: GHSA-mxxc-p822-2hx9
CVE: CVE-2026-24470
CWE: CWE-441, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-mxxc-p822-2hx9
Type: github-advisory

## Affected
- Go: `github.com/zalando/skipper` — affected >=0 <0.24.0

## Details
### Impact

When running Skipper as an Ingress controller, users with permissions to create an Ingress and a Service of type ExternalName can create routes that enable them to use Skipper's network access to reach internal services.

### Patches

https://github.com/zalando/skipper/releases/tag/v0.24.0 disables Kubernetes ExternalName by default.

### Workarounds

Developers can allow list targets of an ExternalName by using `-kubernetes-only-allowed-external-names=true` and allow list via regular expressions `-kubernetes-allowed-external-name '^[a-z][a-z0-9-.]+[.].allowed.example$'` 

### References

https://kubernetes.io/docs/concepts/services-networking/service/#externalname

## References
- https://github.com/zalando/skipper/security/advisories/GHSA-mxxc-p822-2hx9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24470
- https://github.com/zalando/skipper/commit/a4c87ce029a58eb8e1c2c1f93049194a39cf6219
- https://github.com/zalando/skipper
- https://github.com/zalando/skipper/releases/tag/v0.24.0
- https://kubernetes.io/docs/concepts/services-networking/service/#externalname
