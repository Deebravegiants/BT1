# [M] Gitpod vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-gqx9-h3w2-fprg
CVE: CVE-2023-32766
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-05
Source: https://github.com/advisories/GHSA-gqx9-h3w2-fprg
Type: github-advisory

## Affected
- Go: `github.com/gitpod-io/gitpod` — affected >=0 <2022.11.3

## Details
Gitpod before 2022.11.3 allows XSS because redirection can occur for some protocols outside of the trusted set of three (vscode: vscode-insiders: jetbrains-gateway:).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32766
- https://github.com/gitpod-io/gitpod/pull/17559
- https://github.com/gitpod-io/gitpod/commit/6771283c3406586e352337675b79ff2ca50f191b
- https://app.safebase.io/portal/71ccd717-aa2d-4a1e-942e-c768d37e9e0c/preview?product=default&tcuUid=1d505bda-9a38-4ca5-8724-052e6337f34d
- https://github.com/gitpod-io/gitpod
- https://github.com/gitpod-io/gitpod/compare/release-2022.11.2...2022.11.3
- https://github.com/gitpod-io/gitpod/releases/tag/2022.11.3
- https://www.gitpod.io
