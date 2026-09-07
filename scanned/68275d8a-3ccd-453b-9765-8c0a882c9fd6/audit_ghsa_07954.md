# [M] EVE Doesn't Protect Config Partition with Measured Boot

## Summary
Severity: Medium
Advisory: GHSA-wc42-fcjp-v8vq
CVE: CVE-2023-43634
CWE: CWE-522, CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-wc42-fcjp-v8vq
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20230519072751-977f42b07fa9

## Details
### Impact
Config partition measurement was moved from PCR 13 to PCR 14 in a commit, but PCR 14 was not added to the list of PCRs that seal/unseal the vault key. As a result, an attacker can remove the disk, use another server to modify the files in the config partition, and then re-insert the disk.

### Patches

Fixed in EVE version 9.4.3-lts

### Workarounds

None (apart from preventing physical access to the device)

### Resources

https://help.zededa.com/hc/en-us/articles/43295940828827-TPM-PCR-Index-Security-Implications
https://github.com/lf-edge/eve/commit/d9383a7ee4e1c39f5c8c6d4a63cb2ebd00695e8a

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-wc42-fcjp-v8vq
- https://nvd.nist.gov/vuln/detail/CVE-2023-43634
- https://asrg.io/security-advisories/config-partition-not-protected-by-measured-boot
- https://asrg.io/security-advisories/cve-2023-43634
- https://github.com/lf-edge/eve
