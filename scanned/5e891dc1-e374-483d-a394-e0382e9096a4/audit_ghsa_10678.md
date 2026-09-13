# [H] HashiCorp Vault May Expose Tokens to Auth Plugins Due to Incorrect Header Sanitization

## Summary
Severity: High
Advisory: GHSA-72gw-fmmr-c4r4
CVE: CVE-2026-4525
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-72gw-fmmr-c4r4
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=0.11.2

## Details
If a Vault auth mount is configured to pass through the "Authorization" header, and the "Authorization" header is used to authenticate to Vault, Vault forwarded the Vault token to the auth plugin backend. Fixed in 2.0.0, 1.21.5, 1.20.10, and 1.19.16.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4525
- https://access.redhat.com/security/cve/CVE-2026-4525
- https://bugzilla.redhat.com/show_bug.cgi?id=2459107
- https://discuss.hashicorp.com/t/hcsec-2026-07-vault-may-expose-tokens-to-auth-plugins-due-to-incorrect-header-sanitization/77344
- https://github.com/advisories/GHSA-72gw-fmmr-c4r4
- https://github.com/hashicorp/vault
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-4525.json
