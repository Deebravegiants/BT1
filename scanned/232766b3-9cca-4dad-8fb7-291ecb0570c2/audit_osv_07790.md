# [M] Audit Log Plugin Directory Guard Bypass via Legacy path Option

## Summary
Severity: Medium
Advisory: BIT-vault-2026-5051
Aliases: CVE-2026-5051
Ecosystem: Bitnami
Published: 2026-07-07
Source: https://osv.dev/vulnerability/BIT-vault-2026-5051
Type: osv

## Affected
- Bitnami: `vault` — affected >=2.0.0 <2.0.1

## Details
HashiCorp Vault and Vault Enterprise prior to 2.0.1 audit device validation logic did not consistently apply plugin directory protections when the legacy file audit path option was used. 

This vulnerability (CVE-2026-5051) is fixed in 2.0.1, 1.21.6, 1.20.11, and 1.19.17.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-16-vault-audit-device-plugin-directory-guard-bypass-via-legacy-path-option/77536
- https://nvd.nist.gov/vuln/detail/CVE-2026-5051
