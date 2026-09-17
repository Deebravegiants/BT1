# [M] EVE Seals Vault Key With SHA1 PCRs

## Summary
Severity: Medium
Advisory: GHSA-4jvr-vj2c-8q37
CVE: CVE-2023-43635
CWE: CWE-327, CWE-328, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-4jvr-vj2c-8q37
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20230519072751-977f42b07fa9

## Details
### Impact

The vault key is sealed using SHA1 PCRs instead of SHA256 PCRs

Thus an attacker with physical access to an EVE-OS device can try to brute force creating a kernel or rootfs image which produces the same SHA1 PCR but with malicious content.

### Patches

Fixed in 9.4.3-lts and 10.1.0

### Workarounds

None

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-4jvr-vj2c-8q37
- https://nvd.nist.gov/vuln/detail/CVE-2023-43635
- https://asrg.io/security-advisories/cve-2023-43635
- https://asrg.io/security-advisories/vault-key-sealed-with-sha1-pcrs
- https://github.com/lf-edge/eve
