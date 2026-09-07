# [M] Decryption of malicious PBES2 JWE objects can consume unbounded system resources

## Summary
Severity: Medium
Advisory: GHSA-2c7c-3mj9-8fqh
CWE: CWE-400
Ecosystem: Go
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-2c7c-3mj9-8fqh
Type: github-advisory

## Affected
- Go: `github.com/go-jose/go-jose/v3` — affected >=0 <3.0.1
- Go: `github.com/square/go-jose` — affected >=0 <2.6.2

## Details
The go-jose package is subject to a "billion hashes attack" causing denial-of-service when decrypting JWE inputs. This occurs when an attacker can provide a PBES2 encrypted JWE blob with a very large p2c value that, when decrypted, produces a denial-of-service.

## References
- https://github.com/go-jose/go-jose/issues/64
- https://github.com/go-jose/go-jose/commit/65351c27657d58960c2e6c9fbb2b00f818e50568
- https://github.com/go-jose/go-jose/commit/a3d307244c3bc50b25a71aa0688764c32ec419c7
- https://github.com/go-jose/go-jose
