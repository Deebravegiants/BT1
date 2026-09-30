# [C] PraisonAI: GitHub Actions Claude workflow command injection via unquoted PR branch name

## Summary
Severity: Critical
Advisory: CVE-2026-48168
Aliases: GHSA-xp85-6wwf-r67c
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-48168
Type: osv

## Details
PraisonAI is a multi-agent teams system. In versions prior to 4.6.40, the bundled Claude GitHub Actions workflow is vulnerable to command injection because it embeds an attacker-controlled pull request branch name into a Bash run: block without quoting or validation. Additionally, the workflow allows any @claude comment to trigger the job regardless of whether the commenter is a trusted collaborator. An outside contributor can open a pull request from a fork whose branch name contains shell metacharacters and comment @claude, causing Bash to execute arbitrary shell code in the GitHub Actions runner. Because these commands run in a job holding a GitHub App token with write permissions, OIDC access, and gh/git access, the injection can be chained through $GITHUB_PATH to compromise later privileged steps, enabling repository writes, pull request and issue manipulation, or OIDC-token abuse. This issue has been fixed in version 4.6.40.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48168.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-xp85-6wwf-r67c
- https://nvd.nist.gov/vuln/detail/CVE-2026-48168
- https://github.com/MervinPraison/PraisonAI/commit/179cab02dbec0c1e9b601507a659
