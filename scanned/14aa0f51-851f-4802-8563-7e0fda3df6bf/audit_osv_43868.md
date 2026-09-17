# [C] Synk Sweater Comb < 3.8.8 Command Injection via .vervet.yaml Branch Name

## Summary
Severity: Critical
Advisory: CVE-2026-75486
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-75486
Type: osv

## Details
Synk Sweater Comb before 3.8.8 contains a command injection vulnerability that allows an attacker who controls the .vervet.yaml configuration file to execute arbitrary OS commands by injecting malicious input into the linters.<key>.optic-ci.original branch name field. The expectGitBranch() function in src/lint.ts passes the unsanitized branch name directly into child_process.exec() via an unescaped template literal, enabling arbitrary command execution when the lint command is run against the repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75486.json
- https://github.com/snyk/sweater-comb/releases/tag/v3.8.8
- https://nvd.nist.gov/vuln/detail/CVE-2026-75486
- https://www.vulncheck.com/advisories/synk-sweater-comb-command-injection-via-vervet-yaml-branch-name
- https://github.com/snyk/sweater-comb/commit/05a0eec4f2acb9ce6d4814016b475504fc64eab2
- https://github.com/snyk/sweater-comb/pull/743
- https://github.com/snyk/sweater-comb
