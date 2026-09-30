# [M] Jenkins HashiCorp Vault Plugin exposes system-scoped Vault credentials

## Summary
Severity: Medium
Advisory: GHSA-3fm2-hx3h-xm4v
CVE: CVE-2025-67642
CWE: CWE-282
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-3fm2-hx3h-xm4v
Type: github-advisory

## Affected
- Maven: `com.datapipe.jenkins.plugins:hashicorp-vault-plugin` — affected >=0

## Details
Jenkins HashiCorp Vault Plugin 371.v884a_4dd60fb_6 and earlier does not set the appropriate context for Vault credentials lookup, allowing attackers with Item/Configure permission to access and potentially capture Vault credentials they are not entitled to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67642
- https://github.com/jenkinsci/hashicorp-vault-plugin
- https://www.jenkins.io/security/advisory/2025-12-10/#SECURITY-3045
