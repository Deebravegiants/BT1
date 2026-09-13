# [C] Signature forgery in Biscuit

## Summary
Severity: Critical
Advisory: GHSA-75rw-34q6-72cr
CVE: CVE-2022-31053
CWE: CWE-347
Ecosystem: Go, Maven, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-75rw-34q6-72cr
Type: github-advisory

## Affected
- crates.io: `biscuit-auth` — affected >=1.0.0 <2.0.0
- Go: `github.com/biscuit-auth/biscuit-go` — affected >=0 <2.0.0
- Maven: `com.clever-cloud:biscuit-java` — affected >=0 <2.0.0

## Details
### Impact

The paper [Cryptanalysis of Aggregate Γ-Signature and Practical Countermeasures in Application to Bitcoin](https://eprint.iacr.org/2020/1484) defines a way to forge valid Γ-signatures, an algorithm that is used in the Biscuit specification version 1.
It would allow an attacker to create a token with any access level.

As Biscuit v1 was still an early version and not broadly deployed, we were able to contact all known users of Biscuit v1 and help them migrate to Biscuit v2.
We are not aware of any active exploitation of this vulnerability.

### Patches

The version 2 of the specification mandates a different algorithm than gamma signatures and as such is not affected by this vulnerability. The Biscuit implementations in Rust, Haskell, Go, Java and Javascript all have published versions following the v2 specification.

### Workarounds

There is no known workaround, any use of Biscuit v1 should be migrated to v2.

### References
[Cryptanalysis of Aggregate Γ-Signature and Practical Countermeasures in Application to Bitcoin](https://eprint.iacr.org/2020/1484)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [biscuit-auth/biscuit](https://github.com/biscuit-auth/biscuit)
* Ask questions on [Matrix](https://matrix.to/#/#biscuit-auth:matrix.org)

## References
- https://github.com/biscuit-auth/biscuit/security/advisories/GHSA-75rw-34q6-72cr
- https://nvd.nist.gov/vuln/detail/CVE-2022-31053
- https://eprint.iacr.org/2020/1484
- https://github.com/advisories/GHSA-75rw-34q6-72cr
- https://github.com/biscuit-auth/biscuit
- https://pkg.go.dev/vuln/GO-2022-0564
