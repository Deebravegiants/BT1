# [H] github-slug-action vulnerable to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-6q4m-7476-932w
CVE: CVE-2023-27581
CWE: CWE-77
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-13
Source: https://github.com/advisories/GHSA-6q4m-7476-932w
Type: github-advisory

## Affected
- GitHub Actions: `rlespinasse/github-slug-action` — affected >=4.0.0 <4.4.1

## Details
### Impact

This action uses the `github.head_ref` parameter in an insecure way. 

This vulnerability can be triggered by any user on GitHub on any workflow using the action on pull requests. They just need to create a pull request with a branch name, which can contain the attack payload. (Note that first-time PR requests will not be run - but the attacker can submit a valid PR before submitting an invalid PR).  This can be used to execute code on the GitHub runners (potentially use it for crypto-mining, and waste your resources) and to exfiltrate any secrets you use in the CI pipeline.

### Patches

> Pass the variable as an environment variable and then use the environment variable instead of substituting it directly.

Patched action is available on tag **v4**, tag **v4.4.1**, and any tag beyond.

### Workarounds

No workaround is available if impacted, please upgrade the version

> ℹ️ **v3** and **v4** are compatibles.

### References

[Here](https://securitylab.github.com/research/github-actions-untrusted-input/) is a set of blog posts by Github's security team explaining this issue.

### Thanks

Thanks to the team of researchers from Purdue University, who are working on finding vulnerabilities in CI/CD configurations of open-source software. Their tool detected this security vulnerability.

## References
- https://github.com/rlespinasse/github-slug-action/security/advisories/GHSA-6q4m-7476-932w
- https://nvd.nist.gov/vuln/detail/CVE-2023-27581
- https://github.com/rlespinasse/github-slug-action/commit/102b1a064a9b145e56556e22b18b19c624538d94
- https://github.com/rlespinasse/github-slug-action
- https://github.com/rlespinasse/github-slug-action/releases/tag/v4.4.1
- https://securitylab.github.com/research/github-actions-untrusted-input
