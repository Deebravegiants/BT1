# [H] Snyk CLI affected by Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-hpqj-7cj6-hfj8
CVE: CVE-2022-40764
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-04
Source: https://github.com/advisories/GHSA-hpqj-7cj6-hfj8
Type: github-advisory

## Affected
- npm: `snyk` — affected >=0 <1.996.0
- npm: `snyk-go-plugin` — affected >=0 <1.19.1

## Details
Snyk CLI before 1.996.0 allows arbitrary command execution, affecting Snyk IDE plugins and the snyk npm package. Exploitation could follow from the common practice of viewing untrusted files in the Visual Studio Code editor, for example. The original demonstration was with shell metacharacters in the vendor.json ignore field, affecting snyk-go-plugin before 1.19.1. This affects, for example, the Snyk TeamCity plugin (which does not update automatically) before 20220930.142957.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40764
- https://github.com/snyk/cli
- https://github.com/snyk/cli/releases/tag/v1.996.0
- https://github.com/snyk/snyk-go-plugin/releases/tag/v1.19.1
- https://support.snyk.io/hc/en-us/articles/7015908293789-CVE-2022-40764-Command-Injection-vulnerability-affecting-Snyk-CLI-versions-prior-to-1-996-0
- https://www.imperva.com/blog/how-scanning-your-projects-for-security-issues-can-lead-to-remote-code-execution
