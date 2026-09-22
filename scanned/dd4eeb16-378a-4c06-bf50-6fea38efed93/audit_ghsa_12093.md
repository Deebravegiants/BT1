# [M] `melange update-cache` has unbounded HTTP download that can exhaust disk in CI

## Summary
Severity: Medium
Advisory: GHSA-7rp8-r62p-q6wc
CVE: CVE-2026-29049
CWE: CWE-400, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-7rp8-r62p-q6wc
Type: github-advisory

## Affected
- Go: `chainguard.dev/melange` — affected >=0 <0.43.4

## Details
`melange update-cache` downloads URIs from build configs via `io.Copy` without any size limit or HTTP client timeout (`pkg/renovate/cache/cache.go`). An attacker-controlled URI in a melange config can cause unbounded disk writes, exhausting disk on the build runner. Affected versions <= 0.40.5.

**Fix:** Merged
**Acknowledgements**

Thank you to Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-7rp8-r62p-q6wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-29049
- https://github.com/chainguard-dev/melange/pull/2379
- https://github.com/chainguard-dev/melange/commit/652ca5af08588f78e2d405e64b058fac8398d23f
- https://github.com/chainguard-dev/melange
- https://github.com/chainguard-dev/melange/releases/tag/v0.43.4
