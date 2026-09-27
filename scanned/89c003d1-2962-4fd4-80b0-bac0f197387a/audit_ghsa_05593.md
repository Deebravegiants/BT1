# [H] Jervis has Deterministic AES IV Derivation from Passphrase

## Summary
Severity: High
Advisory: GHSA-crxp-chh4-9ghp
CVE: CVE-2025-68701
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-crxp-chh4-9ghp
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L866-L874

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L891-L900

Same passphrase + same plaintext = same ciphertext (IV reuse)

### Impact

Severity is considered low for internal uses of this library but if there's any consumer using these methods directly then this is considered high.

Significant reduction in the security of the encryption scheme. Pattern analysis becomes possible.

### Patches

Random IV will be generated and prepended to the ciphertext.

Upgrade to Jervis 2.2.

### Workarounds

None

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-crxp-chh4-9ghp
- https://nvd.nist.gov/vuln/detail/CVE-2025-68701
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L866-L874
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L891-L900
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
