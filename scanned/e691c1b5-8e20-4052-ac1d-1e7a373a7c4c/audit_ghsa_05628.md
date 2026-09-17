# [H] Jervis's AES CBC Mode is Without Authentication

## Summary
Severity: High
Advisory: GHSA-gxp5-mv27-vjcj
CVE: CVE-2025-68931
CWE: CWE-287, CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-gxp5-mv27-vjcj
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L682-L684

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L720-L722

`AES/CBC/PKCS5Padding` lacks authentication, making it vulnerable to padding oracle attacks and ciphertext manipulation.

### Impact

Severity is considered low for internal uses of this library but if there's any consumer using these methods directly then this is considered critical.

Unlikely to matter due to the design of how AES-256-CBC is used in conjunction with RSA and SHA-256 checksum within Jervis.

Jervis uses RSA to encrypt AES keys and a SHA-256 checksum of the encrypted data in local-only storage inaccessible from the web.  After asymmetric decryption and before symmetric decryption, a SHA-256 checksum is performed on the metadata and encrypted data. All encrypted data is discarded if the checksum does not match without attempting to decrypt since the encrypted data is assumed invalid.  The data stored is GitHub App authentication tokens which will expire within one hour.

### Patches

Jervis patch will migrate from `AES/CBC/PKCS5Padding` to `AES/GCM/NoPadding`.

Upgrade to Jervis 2.2.

### Workarounds

None

### References

- [Padding Oracle Attacks](https://en.wikipedia.org/wiki/Padding_oracle_attack)

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-gxp5-mv27-vjcj
- https://nvd.nist.gov/vuln/detail/CVE-2025-68931
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L682-L684
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L720-L722
- http://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
