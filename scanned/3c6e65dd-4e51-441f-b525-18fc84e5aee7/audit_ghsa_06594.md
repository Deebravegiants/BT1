# [M] goshs has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-wg2q-39h6-66x9
CVE: CVE-2026-66063
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-wg2q-39h6-66x9
Type: github-advisory

## Affected
- Go: `goshs.de/goshs/v2` — affected >=0 <2.1.5-0.20260727065949-f3ef599e4091
- Go: `github.com/patrickhener/goshs/v2` — affected >=0 <2.1.5-0.20260727065949-f3ef599e4091
- Go: `goshs.de/goshs` — affected >=0
- Go: `github.com/patrickhener/goshs` — affected >=0

## Details
## Summary

The multipart upload filename fix splits on the path separator but never rejects dot-dot, allowing a write outside the served tree.

## Finding (Medium): upload filename escapes the served tree (residual of CVE-2026-35393)

The multipart filename fix (updown.go lines 135-136) splits on the path separator but never rejects "..". Uploading with filename=".." results in os.Create against the parent of the upload folder with a trailing marker character, outside the served tree, and the subsequent failed rename leaves that file behind. Verified: a file containing ESCAPED_WRITE_PROOF was written outside the webroot, unauthenticated, with the default configuration. Not claimed: a Windows-specific variant (Go's Part.FileName() already applies filepath.Base).

## Suggested fixes

1. Reject any upload filename that is "..", is empty after sanitisation, or resolves outside the upload folder; validate the final resolved destination rather than only transforming the input.

## Tooling

AI assistance was used while investigating. The finding was reproduced against a running server on loopback.

## References
- https://github.com/goshs-labs/goshs/security/advisories/GHSA-wg2q-39h6-66x9
- https://github.com/goshs-labs/goshs/commit/f3ef599e409151d1380866e47de8b1afb0bb54fa
- https://github.com/goshs-labs/goshs
