# [M] Improper random reading in CIRCL

## Summary
Severity: Medium
Advisory: GHSA-2q89-485c-9j2x
CVE: CVE-2023-1732
CWE: CWE-20, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-2q89-485c-9j2x
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/circl` — affected >=0 <1.3.3

## Details
### Impact
When sampling randomness for a shared secret, the implementation of Kyber and FrodoKEM, did not check whether `crypto/rand.Read()` returns an error. In rare deployment cases (error thrown by the `Read()` function), this could lead to a predictable shared secret.

The tkn20 and blindrsa components did not check whether enough randomness was returned from the user provided randomness source. Typically the user provides `crypto/rand.Reader`, which in the vast majority of cases will always return the right number random bytes. In the cases where it does not, or the user provides a source that does not, the blinding for blindrsa is weak and integrity of the plaintext is not ensured in tkn20.


### Patches
The fix was introduced in CIRCL v. 1.3.3

## References
- https://github.com/cloudflare/circl/security/advisories/GHSA-2q89-485c-9j2x
- https://nvd.nist.gov/vuln/detail/CVE-2023-1732
- https://github.com/cloudflare/circl/commit/ff8d91225f8954b4970b6d6382d2e4c78f4a4cf8
- https://github.com/cloudflare/circl
- https://github.com/cloudflare/circl/releases/tag/v1.3.3
