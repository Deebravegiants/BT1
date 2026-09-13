# [H] Go JOSE Panics in JWE decryption

## Summary
Severity: High
Advisory: GHSA-78h2-9frx-2jm8
CVE: CVE-2026-34986
CWE: CWE-248
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-78h2-9frx-2jm8
Type: github-advisory

## Affected
- Go: `github.com/go-jose/go-jose/v4` — affected >=0 <4.1.4
- Go: `github.com/go-jose/go-jose/v3` — affected >=0 <3.0.5
- Go: `github.com/go-jose/go-jose` — affected >=0

## Details
### Impact

Decrypting a JSON Web Encryption (JWE) object will panic if the `alg` field indicates a key wrapping algorithm ([one ending in `KW`](https://pkg.go.dev/github.com/go-jose/go-jose/v4#pkg-constants), with the exception of `A128GCMKW`, `A192GCMKW`, and `A256GCMKW`) and the `encrypted_key` field is empty. The panic happens when `cipher.KeyUnwrap()` in `key_wrap.go` attempts to allocate a slice with a zero or negative length based on the length of the `encrypted_key`.

This code path is reachable from `ParseEncrypted()` / `ParseEncryptedJSON()` / `ParseEncryptedCompact()` followed by `Decrypt()` on the resulting object. Note that the parse functions take a list of accepted key algorithms. If the accepted key algorithms do not include any key wrapping algorithms, parsing will fail and the application will be unaffected.

This panic is also reachable by calling `cipher.KeyUnwrap()` directly with any `ciphertext` parameter less than 16 bytes long, but calling this function directly is less common.

Panics can lead to denial of service.

### Fixed In

4.1.4 and v3.0.5

### Workarounds

If the list of `keyAlgorithms` passed to `ParseEncrypted()` / `ParseEncryptedJSON()` / `ParseEncryptedCompact()` does not include key wrapping algorithms (those ending in `KW`), your application is unaffected.

If your application uses key wrapping, you can prevalidate to the JWE objects to ensure the `encrypted_key` field is nonempty. If your application accepts JWE Compact Serialization, apply that validation to the corresponding field of that serialization (the data between the first and second `.`).

### Thanks

Thanks to Datadog's Security team for finding this issue.

## References
- https://github.com/go-jose/go-jose/security/advisories/GHSA-78h2-9frx-2jm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34986
- https://github.com/go-jose/go-jose
- https://pkg.go.dev/github.com/go-jose/go-jose/v4#pkg-constants
