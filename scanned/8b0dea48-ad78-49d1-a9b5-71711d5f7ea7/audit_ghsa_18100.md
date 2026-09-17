# [C] Gardener provider extensions vulnerable to code injection when Terraform is used for infrastructure provisioning

## Summary
Severity: Critical
Advisory: GHSA-227x-7mh8-3cf6
CVE: CVE-2025-59823
CWE: CWE-20, CWE-94
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-227x-7mh8-3cf6
Type: github-advisory

## Affected
- Go: `github.com/gardener/gardener-extension-provider-aws` — affected >=0 <1.64.0
- Go: `github.com/gardener/gardener-extension-provider-gcp` — affected >=0 <1.46.0
- Go: `github.com/gardener/gardener-extension-provider-azure` — affected >=0 <1.55.0
- Go: `github.com/gardener/gardener-extension-provider-openstack` — affected >=0 <1.49.0

## Details
### Impact

A security vulnerability was discovered in Gardener when [Terraformer](https://github.com/gardener/terraformer) is used for infrastructure provisioning. This vulnerability could allow a user with administrative privileges for a Gardener project to obtain control over the seed cluster where the shoot cluster is managed.

This CVE affects all Gardener installations where [Terraformer](https://github.com/gardener/terraformer) is used/can be enabled for infrastructure provisioning with any of the affected components mentioned below.

### Affected Components
• gardener-extension-provider-gcp
• gardener-extension-provider-azure
• gardener-extension-provider-openstack
• gardener-extension-provider-aws

### Affected Versions
• gardener-extension-provider-gcp < v1.46.0
• gardener-extension-provider-azure < v1.55.0
• gardener-extension-provider-openstack < v1.49.0
• gardener-extension-provider-aws < v1.64.0

### Fixed versions
• gardener-extension-provider-gcp >= v1.46.0
• gardener-extension-provider-azure >= v1.55.0
• gardener-extension-provider-openstack >= v1.49.0
• gardener-extension-provider-aws >= v1.64.0

### How do I mitigate this vulnerability?
Update to a fixed version.

## References
- https://github.com/gardener/gardener-extension-provider-aws/security/advisories/GHSA-227x-7mh8-3cf6
- https://nvd.nist.gov/vuln/detail/CVE-2025-59823
- https://github.com/gardener/gardener-extension-provider-aws/commit/cb5045fc146248296994804bbfe27bd896938bf2
- https://github.com/gardener/gardener-extension-provider-azure/commit/4573a4404969f89781ed6cf72e90554bc6ae2020
- https://github.com/gardener/gardener-extension-provider-gcp/commit/51111b4f60c33c60dfdf18b1fc50f7ec8d8f70ac
- https://github.com/gardener/gardener-extension-provider-openstack/commit/2ed6f0fe1be90fbef5d6093eb0b8325c8421b8d8
- https://github.com/gardener/gardener-extension-provider-aws
- https://github.com/gardener/gardener-extension-provider-aws/releases/tag/v1.64.0
- https://github.com/gardener/gardener-extension-provider-azure/releases/tag/v1.55.0
- https://github.com/gardener/gardener-extension-provider-gcp/releases/tag/v1.46.0
- https://github.com/gardener/gardener-extension-provider-openstack/releases/tag/v1.49.0
- https://pkg.go.dev/vuln/GO-2025-3981
