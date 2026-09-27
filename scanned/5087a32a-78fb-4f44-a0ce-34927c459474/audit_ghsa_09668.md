# [H] HashiCorp Vault Vulnerable to Denial-of-Service via Unauthenticated Root Token Generation/Rekey Operations

## Summary
Severity: High
Advisory: GHSA-88v5-9hxc-f85r
CVE: CVE-2026-5807
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-88v5-9hxc-f85r
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0

## Details
Vault is vulnerable to a denial-of-service condition where an unauthenticated attacker can repeatedly initiate or cancel root token generation or rekey operations, occupying the single in-progress operation slot. This prevents legitimate operators from completing these workflows. This vulnerability, CVE-2026-5807, is fixed in Vault Community Edition 2.0.0 and Vault Enterprise 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5807
- https://access.redhat.com/security/cve/CVE-2026-5807
- https://bugzilla.redhat.com/show_bug.cgi?id=2459109
- https://discuss.hashicorp.com/t/hcsec-2026-08-vault-vulnerable-to-denial-of-service-via-unauthenticated-root-token-generation-rekey-operations/77345
- https://github.com/advisories/GHSA-88v5-9hxc-f85r
- https://github.com/hashicorp/vault
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-5807.json
