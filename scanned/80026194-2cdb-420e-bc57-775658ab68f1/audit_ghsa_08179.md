# [M] EVE Doesn't Measure Config Partition From 2 Fronts

## Summary
Severity: Medium
Advisory: GHSA-phcg-h58r-gmcq
CVE: CVE-2023-43630
CWE: CWE-328, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-phcg-h58r-gmcq
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20230126065759-d9383a7ee4e1

## Details
### Impact
PCR14 is not included in the list of PCRs that seal/unseal the vault key. Additionally, the vault key uses SHA1 PCRs instead of SHA256.
Thus an attacker with physical access can take out the disk, use a different computer to modify the files in the /config partition, and re-insert the disk and boot without the change being detected by measured boot and remote attestation.

### Patches

Fixed in EVE version 9.4.3-lts

### Workarounds

None (apart from preventing physical access to the device)

### Resources

https://help.zededa.com/hc/en-us/articles/43295940828827-TPM-PCR-Index-Security-Implications
https://github.com/lf-edge/eve/commit/d9383a7ee4e1c39f5c8c6d4a63cb2ebd00695e8a

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-phcg-h58r-gmcq
- https://nvd.nist.gov/vuln/detail/CVE-2023-43630
- https://github.com/lf-edge/eve/commit/d9383a7ee4e1c39f5c8c6d4a63cb2ebd00695e8a
- https://asrg.io/security-advisories/config-partition-not-measured-from-2-fronts
- https://asrg.io/security-advisories/cve-2023-43630
- https://github.com/lf-edge/eve
- https://help.zededa.com/hc/en-us/articles/43295940828827-TPM-PCR-Index-Security-Implications
