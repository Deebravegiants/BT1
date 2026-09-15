# [C] OS command injection in git-diff-apply

## Summary
Severity: Critical
Advisory: GHSA-84cm-v6jp-gjmr
CVE: CVE-2019-10776
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-84cm-v6jp-gjmr
Type: github-advisory

## Affected
- npm: `git-diff-apply` — affected >=0 <0.22.2

## Details
In "index.js" file line 240, the run command executes the git command with a user controlled variable called remoteUrl. This affects git-diff-apply all versions prior to 0.22.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10776
- https://github.com/kellyselden/git-diff-apply/commit/106d61d3ae723b4257c2a13e67b95eb40a27e0b5
- https://snyk.io/vuln/SNYK-JS-GITDIFFAPPLY-540774
- https://snyk.io/vuln/SNYK-JS-GITDIFFAPPLY-540774,
