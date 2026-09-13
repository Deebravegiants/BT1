# [M] ITFlow Vulnerable to Authenticated Cross-Tenant Credential Disclosure via Unprotected Credential Modal

## Summary
Severity: Medium
Advisory: CVE-2026-47755
Aliases: GHSA-987x-g5f9-2rpq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-47755
Type: osv

## Details
ITFlow provides an IT documentation, ticketing and accounting system for small managed service providers. Prior to version 26.05, low-privileged authenticated agent can retrieve plaintext credentials and TOTP secrets belonging to another client by directly requesting the credential edit modal with an arbitrary `credential_id`. The endpoint does not enforce client scoping or object-level authorization before loading and decrypting the credential record. Version 26.05 fixes the issue.

## References
- https://github.com/itflow-org/itflow/compare/v26.04...v26.05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47755.json
- https://github.com/itflow-org/itflow/security/advisories/GHSA-987x-g5f9-2rpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47755
