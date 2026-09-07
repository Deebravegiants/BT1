# [H] kaniko has tar archive path traversal in its build context extraction, allowing file writes outside destination directories

## Summary
Severity: High
Advisory: GHSA-6rxq-q92g-4rmf
CVE: CVE-2026-28406
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-6rxq-q92g-4rmf
Type: github-advisory

## Affected
- Go: `github.com/chainguard-dev/kaniko` — affected >=1.25.4 <1.25.10

## Details
kaniko unpacks build context archives using `filepath.Join(dest, cleanedName)` without enforcing that the final path stays within `dest`. A tar entry like `../outside.txt` escapes the extraction root and writes files outside the destination directory. In environments with registry authentication, this can be chained with docker credential helpers to achieve code execution within the executor process. Affected versions >= 1.25.4, <= 1.25.9.

**Fix:** Merged with [PR #326](https://github.com/chainguard-forks/kaniko/pull/326) — uses securejoin for path resolution in tar extraction.

**Acknowledgements**

kaniko thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-forks/kaniko/security/advisories/GHSA-6rxq-q92g-4rmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28406
- https://github.com/chainguard-forks/kaniko/pull/326
- https://github.com/chainguard-forks/kaniko/commit/a370e4b1f66e6e842b685c8f70ed507964c4b221
- https://github.com/chainguard-forks/kaniko
- https://github.com/chainguard-forks/kaniko/releases/tag/v1.25.10
