# [M] Logto: OS command injection vulnerability exists in the Commitlint workflow

## Summary
Severity: Medium
Advisory: CVE-2026-63187
Aliases: GHSA-869c-8mm3-w5cj
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-63187
Type: osv

## Details
Logto is the modern, open-source auth infrastructure for SaaS and AI apps. From 1.40.1 until 1.41.0, Logto's .github/workflows/commitlint.yml directly interpolated github.event.pull_request.title into the Commitlint on PR title step's inline echo command before piping the title to npx commitlint. A pull request title containing a single quote could terminate the echo string and append arbitrary shell commands on the GitHub Actions runner. The pull_request trigger used a read-only GITHUB_TOKEN and did not expose repository secrets, but injected commands could alter or disrupt the ephemeral workflow execution. This issue is fixed in version 1.41.0.

## References
- https://github.com/logto-io/logto/releases/tag/v1.41.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63187.json
- https://github.com/logto-io/logto/security/advisories/GHSA-869c-8mm3-w5cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-63187
- https://github.com/logto-io/logto/commit/4a1cab21c14d26d288ffffc509cc2a8cae247b92
- https://github.com/logto-io/logto/pull/9112
