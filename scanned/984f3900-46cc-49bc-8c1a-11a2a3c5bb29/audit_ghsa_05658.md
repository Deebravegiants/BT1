# [H] Jervis's Salt for PBKDF2 derived from password

## Summary
Severity: High
Advisory: GHSA-36h5-vrq6-pp34
CVE: CVE-2025-68703
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-36h5-vrq6-pp34
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L869-L870

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L894-L895

The salt is derived from sha256Sum(passphrase).  Two encryption operations with the same password will have the same derived key.

### Impact

Pre-computation attacks.

Severity is considered low for internal uses of this library and high for consumers of this library.

### Patches

Jervis will generate a random salt for each password and store it alongside the ciphertext.

Upgrade to Jervis 2.2.

### Workarounds

None

### References

- [NIST SP 800-132: Password-Based Key Derivation](https://csrc.nist.gov/publications/detail/sp/800-132/final)

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-36h5-vrq6-pp34
- https://nvd.nist.gov/vuln/detail/CVE-2025-68703
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L869-L870
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L894-L895
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
