# [H] melange QEMU runner could write files outside workspace directory

## Summary
Severity: High
Advisory: GHSA-qxx2-7h4c-83f4
CVE: CVE-2026-24843
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-qxx2-7h4c-83f4
Type: github-advisory

## Affected
- Go: `chainguard.dev/melange` — affected >=0.11.3 <0.40.3

## Details
An attacker who can influence the tar stream from a QEMU guest VM could write files outside the intended workspace directory on the host. The `retrieveWorkspace` function extracts tar entries without validating that paths stay within the workspace, allowing Path Traversal via `../` sequences.

**Fix:** Fixed in [6e243d0d](https://github.com/chainguard-dev/melange/commit/6e243d0d46699f837d7c392397a694d2bcc7612b). Merged in release.

**Acknowledgements**

melange thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-qxx2-7h4c-83f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24843
- https://github.com/chainguard-dev/melange/commit/6e243d0d46699f837d7c392397a694d2bcc7612b
- https://github.com/chainguard-dev/melange
