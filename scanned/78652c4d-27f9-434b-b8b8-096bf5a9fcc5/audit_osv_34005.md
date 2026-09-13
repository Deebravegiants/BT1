# [C] Folo allows secrets exfiltration via `pull_request_target`

## Summary
Severity: Critical
Advisory: CVE-2025-53546
Aliases: GHSA-h87r-5w74-qfm4
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-53546
Type: osv

## Details
Folo organizes feeds content into one timeline. Using pull_request_target on .github/workflows/auto-fix-lint-format-commit.yml can be exploited by attackers, since untrusted code can be executed having full access to secrets (from the base repo). By exploiting the vulnerability is possible to exfiltrate GITHUB_TOKEN which has high privileges. GITHUB_TOKEN can be used to completely overtake the repo since the token has content write privileges. This vulnerability is fixed in commit 585c6a591440cd39f92374230ac5d65d7dd23d6a.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53546.json
- https://github.com/RSSNext/Folo/security/advisories/GHSA-h87r-5w74-qfm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-53546
- https://github.com/RSSNext/Folo/commit/585c6a591440cd39f92374230ac5d65d7dd23d6a
