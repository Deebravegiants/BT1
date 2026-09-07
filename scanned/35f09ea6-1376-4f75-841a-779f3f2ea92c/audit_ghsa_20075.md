# [H] Golf may allow attacker to bypass CSRF protections due to weak PRNG

## Summary
Severity: High
Advisory: GHSA-q9qr-jwpw-3qvv
CVE: CVE-2016-15005
CWE: CWE-332, CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-q9qr-jwpw-3qvv
Type: github-advisory

## Affected
- Go: `github.com/dinever/golf` — affected >=0 <0.3.0

## Details
CSRF tokens are generated using math/rand, which is not a cryptographically secure random number generator, allowing an attacker to predict values and bypass CSRF protections with relatively few requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15005
- https://github.com/dinever/golf/issues/20
- https://github.com/dinever/golf/pull/24
- https://github.com/dinever/golf/commit/3776f338be48b5bc5e8cf9faff7851fc52a3f1fe
- https://github.com/dinever/golf
- https://github.com/dinever/golf/releases/tag/v0.3.0
- https://pkg.go.dev/vuln/GO-2020-0045
