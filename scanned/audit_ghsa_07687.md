# [M] malcontent: Nested archive extraction failure can drop content from scan inputs

## Summary
Severity: Medium
Advisory: GHSA-945p-3jhm-6rcp
CVE: CVE-2026-28407
CWE: CWE-703
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-945p-3jhm-6rcp
Type: github-advisory

## Affected
- Go: `github.com/chainguard-dev/malcontent` — affected >=0 <1.21.0

## Details
Previously, malcontent would remove nested archives which failed to extract which could potentially leave malicious content. A better approach is to preserve these archives so that malcontent can attempt a best-effort scan of the archive bytes.

**Fix**:  https://github.com/chainguard-dev/malcontent/pull/1383

**Acknowledgements**

malcontent thanks Oleh Konko from [1seal](https://1seal.org/) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/malcontent/security/advisories/GHSA-945p-3jhm-6rcp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28407
- https://github.com/chainguard-dev/malcontent/pull/1383
- https://github.com/chainguard-dev/malcontent/commit/356c56659ccfcad0b249a97de8cf71f151ed3ee9
- https://github.com/chainguard-dev/malcontent
