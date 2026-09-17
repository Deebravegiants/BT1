# [M] apko `DiscoverKeys` has a panic on non-rsa jwks key that causes crash during key discovery

## Summary
Severity: Medium
Advisory: GHSA-m7hm-vm4x-28jf
CVE: CVE-2026-42576
CWE: CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-m7hm-vm4x-28jf
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0 <1.2.7

## Details
`DiscoverKeys` in `pkg/apk/apk/implementation.go` unconditionally type-asserts JWKS keys as `*rsa.PublicKey` without checking the key type. If a repository JWKS endpoint returns a non-RSA key (e.g. EC), the unchecked assertion panics and crashes apko. This affects any workflow that initializes the APK database and fetches repository keys. Affected versions <= 0.30.34.

**Fix:** No fix available yet.

**Acknowledgements**

apko thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/apko/security/advisories/GHSA-m7hm-vm4x-28jf
- https://nvd.nist.gov/vuln/detail/CVE-2026-42576
- https://github.com/chainguard-dev/apko/commit/6604826b19e36e9bc6e196592800fad93738f4a1
- https://github.com/chainguard-dev/apko
- https://github.com/chainguard-dev/apko/releases/tag/v1.2.7
