# [H] Jervis Has a RSA PKCS#1 Padding Vulnerability

## Summary
Severity: High
Advisory: GHSA-mqw7-c5gg-xq97
CVE: CVE-2025-68698
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-mqw7-c5gg-xq97
Type: github-advisory

## Affected
- Maven: `net.gleske:jervis` — affected >=0 <2.2

## Details
### Vulnerability

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L463-L465

https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L495-L497

Uses `PKCS1Encoding` which is vulnerable to Bleichenbacher padding oracle attacks. Modern systems should use OAEP (Optimal Asymmetric Encryption Padding).

### Impact

Severity is considered low for internal uses of this library but if there's any consumer using these methods directly then this is considered critical.

An attacker with access to a decryption oracle (e.g., timing differences or error messages) could potentially decrypt ciphertext without knowing the private key.

Jervis uses RSA to encrypt AES keys in local-only storage inaccessible from the web.  The data stored is GitHub App authentication tokens which will expire within one hour or less.

### Patches

Jervis patch will migrate from `PKCS1Encoding` to `OAEPEncoding`.

Upgrade to Jervis 2.2.

### Workarounds

None

### References

- [Bleichenbacher's Attack on PKCS#1](https://en.wikipedia.org/wiki/Adaptive_chosen-ciphertext_attack)

## References
- https://github.com/samrocketman/jervis/security/advisories/GHSA-mqw7-c5gg-xq97
- https://nvd.nist.gov/vuln/detail/CVE-2025-68698
- https://github.com/samrocketman/jervis/commit/c3981ff71de7b0f767dfe7b37a2372cb2a51974a
- https://github.com/samrocketman/jervis
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L463-L465
- https://github.com/samrocketman/jervis/blob/157d2b63ffa5c4bb1d8ee2254950fd2231de2b05/src/main/groovy/net/gleske/jervis/tools/SecurityIO.groovy#L495-L497
