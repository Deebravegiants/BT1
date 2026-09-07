# [H] apko doesn't verify downloaded apk packages against APKINDEX checksum (package substitution possible)

## Summary
Severity: High
Advisory: GHSA-hcwr-pq9g-rq3m
CVE: CVE-2026-42575
CWE: CWE-345, CWE-494
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-hcwr-pq9g-rq3m
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0 <1.2.7

## Details
apko verifies the signature on `APKINDEX.tar.gz` but never compares individually downloaded `.apk` packages against the checksum recorded in the signed index. The checksum is parsed and available via `ChecksumString()`, and the downloaded package control hash is computed, but the two values are never compared in `getPackageImpl()`. Mismatched packages are silently accepted. An attacker who can substitute download responses (compromised mirror, HTTP repository, poisoned CDN cache) can install arbitrary packages into built images.

**Fix:** No fix available yet.

**Acknowledgements**

apko thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/apko/security/advisories/GHSA-hcwr-pq9g-rq3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-42575
- https://github.com/chainguard-dev/apko/commit/a118c3d604107532b5525bd4bee2fb369a6228aa
- https://github.com/chainguard-dev/apko
- https://github.com/chainguard-dev/apko/releases/tag/v1.2.7
