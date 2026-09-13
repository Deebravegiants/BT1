# [M] rPGP's integrity protection of encrypted data was not always checked

## Summary
Severity: Medium
Advisory: GHSA-c7ph-f7jm-xv4w
CWE: CWE-354
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-c7ph-f7jm-xv4w
Type: github-advisory

## Affected
- crates.io: `pgp` — affected >=0.16.0-alpha.0 <0.19.0

## Details
### Summary
For some messages, rPGP returned incorrectly decrypted data without signaling that integrity protection was invalid.

### Details
When decrypting SEIPD (Symmetrically Encrypted and Integrity Protected Data Packet), rPGP previously did not under all circumstances report the absence of valid integrity protection to callers of the library.

### Impact
While the resulting invalid decryption output is not attacker controlled, its contents may be a security concern if an attacker can gain access to it.

### Attribution
Discovered internally in the course of rPGP development work.

## References
- https://github.com/rpgp/rpgp/security/advisories/GHSA-c7ph-f7jm-xv4w
- https://github.com/rpgp/rpgp
