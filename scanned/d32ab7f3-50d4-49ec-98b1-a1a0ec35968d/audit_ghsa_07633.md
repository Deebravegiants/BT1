# [M] EVE Has Partially Predetermined Vault Key

## Summary
Severity: Medium
Advisory: GHSA-g7vp-j25f-h34p
CVE: CVE-2023-43637
CWE: CWE-321, CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-g7vp-j25f-h34p
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20220310190112-c0c966dc31e2

## Details
### Impact

The deriveVaultKey function calls retrieveCloudKey which always returns "foobarfoobarfoobarfoobarfoobarfo". When merged with the randomly generated 32-byte key using mergeKeys (16 bytes from each), the last 16 bytes are always "arfoobarfoobarfo". This enables an attacker with physical access to the EVE-OS device to attempt to brute force the remaining 128 bits of key.

### Patches

Fixed in 7.10 and  8.12.1-lts

### Workarounds

None

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-g7vp-j25f-h34p
- https://nvd.nist.gov/vuln/detail/CVE-2023-43637
- https://github.com/lf-edge/eve/commit/c0c966dc31e2ed9aafc155e6be646adb14756c01
- https://asrg.io/security-advisories/cve-2023-43637
- https://asrg.io/security-advisories/vault-key-partially-predetermined
- https://github.com/lf-edge/eve
