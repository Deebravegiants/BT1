# [M] OpenBao and Vault Leak []byte Fields in Audit Logs 

## Summary
Severity: Medium
Advisory: GHSA-rc54-2g2c-g36g
CVE: CVE-2025-62705
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-rc54-2g2c-g36g
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20251022165510-cc2c476bac66

## Details
### Impact

OpenBao's audit log did not appropriately redact fields when relevant subsystems sent `[]byte` response parameters rather than `string`s. This includes, but is not limited to:

- `sys/raw` with use of `encoding=base64`, all data would be emitted unredacted to the audit log.
- Transit, when performing a signing operation with a derived Ed25519 key, would emit public keys to the audit log.

Third-party plugins may be affected.

This issue has been present since HashiCorp Vault and continues to impact Vault as of v1.20.4. 

### Patches

OpenBao v2.4.2 will patch this issue.

### Workarounds

If users do not use the above functionality, they are not impacted. To prohibit the use of `sys/raw` globally, ensure `raw_storage_endpoint=false` is set or missing from the server configuration.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-rc54-2g2c-g36g
- https://nvd.nist.gov/vuln/detail/CVE-2025-62705
- https://github.com/openbao/openbao/commit/cc2c476bac66e1d94776c2629793daec3af625f8
- https://github.com/openbao/openbao
