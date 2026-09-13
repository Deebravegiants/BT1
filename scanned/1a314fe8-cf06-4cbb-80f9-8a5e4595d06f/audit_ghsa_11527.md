# [M] malcontent: Error-path cleanup gap can leak scanners and fds and degrade availability

## Summary
Severity: Medium
Advisory: GHSA-54p8-x2m9-c593
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-54p8-x2m9-c593
Type: github-advisory

## Affected
- Go: `github.com/chainguard-dev/malcontent` — affected >=0 <1.21.0

## Details
Several extraction and scanning code paths registered late defers which could leak resources and exhaust system resources.

This report is an aggregate of these individual reports for the affected code:
Advisory | Affected File
-- | --
`GHSA-jjgh-mc5q-gch7` | `pkg/action/scan.go`
`GHSA-mwmf-fxh2-w4x7` | `pkg/archive/deb.go`
`GHSA-p8j3-rpf5-gwv3` | `pkg/archive/gzip.go`
`GHSA-qfh4-7f5v-75gq` | `pkg/archive/zlib.go`
`GHSA-wxxf-r586-5rf5` | `pkg/archive/bzip2.go`

**Fix**: #1354, #1355, #1356, #1361

**Acknowledgements**

Thank you to Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting all six of these issues.

## References
- https://github.com/chainguard-dev/malcontent/security/advisories/GHSA-54p8-x2m9-c593
- https://github.com/chainguard-dev/malcontent/pull/1354
- https://github.com/chainguard-dev/malcontent/pull/1355
- https://github.com/chainguard-dev/malcontent/pull/1356
- https://github.com/chainguard-dev/malcontent/pull/1361
- https://github.com/chainguard-dev/malcontent
