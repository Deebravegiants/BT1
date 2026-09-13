# [H] cal.com Repository Takeover via pull_request_target Workflow

## Summary
Severity: High
Advisory: CVE-2024-58354
Aliases: GHSA-p3f6-52gv-cj7m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2024-58354
Type: osv

## Details
cal.com (calcom repository, later renamed cal.diy) is affected by a repository takeover vulnerability in its GitHub Actions workflows. The workflow pr.yml uses the pull_request_target trigger with the repository's default write permissions and passes them down to check-types.yml. check-types.yml then performs a 'dangerous' checkout of the attacker-submitted pull request code (via the dangerous-git-checkout action) and subsequently executes it (through yarn install and package.json scripts). An attacker can open a pull request whose code runs arbitrary commands with the repository's write-scoped GITHUB_TOKEN, allowing them to push commits, merge or mutate pull requests, add or delete comments, and delete or force-push branches, thereby compromising the repository. The main branch is affected; no patched version is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58354.json
- https://github.com/calcom/cal.diy/security/advisories/GHSA-p3f6-52gv-cj7m
- https://nvd.nist.gov/vuln/detail/CVE-2024-58354
- https://www.vulncheck.com/advisories/cal-com-repository-takeover-via-pull-request-target-workflow
- https://github.com/calcom/cal.diy/commit/9aa60fae41a6b6b101c86bf430754b439f440871
