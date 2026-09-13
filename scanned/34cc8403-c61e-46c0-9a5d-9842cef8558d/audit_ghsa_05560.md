# [M] malcontent vulnerable to symlink Path Traversal via handleSymlink argument confusion in archive extraction

## Summary
Severity: Medium
Advisory: GHSA-923j-vrcg-hxwh
CVE: CVE-2026-24846
CWE: CWE-22, CWE-683
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-923j-vrcg-hxwh
Type: github-advisory

## Affected
- Go: `github.com/chainguard-dev/malcontent` — affected >=1.8.0 <1.20.3

## Details
malcontent could be made to create symlinks outside the intended extraction directory when scanning a specially crafted tar or deb archive. The `handleSymlink` function received arguments in the wrong order, causing the symlink target to be used as the symlink location. Additionally, symlink targets were not validated to ensure they resolved within the extraction directory.

**Fixes:**
- [Swap handleSymlink arguments; validate symlink location](https://github.com/chainguard-dev/malcontent/commit/a7dd8a5328ddbaf235568437813efa7591e00017)
- [Validate symlink targets resolve within extraction directory](https://github.com/chainguard-dev/malcontent/commit/259fca5abc004f3ab238895463ef280a87f30e96)

**Acknowledgements**

Thank you to Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/malcontent/security/advisories/GHSA-923j-vrcg-hxwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24846
- https://github.com/chainguard-dev/malcontent/commit/259fca5abc004f3ab238895463ef280a87f30e96
- https://github.com/chainguard-dev/malcontent/commit/a7dd8a5328ddbaf235568437813efa7591e00017
- https://github.com/chainguard-dev/malcontent
