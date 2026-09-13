# [C] OS Command Injection in git-add-remote

## Summary
Severity: Critical
Advisory: GHSA-h9v8-rm3m-5h5f
CVE: CVE-2020-7630
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-h9v8-rm3m-5h5f
Type: github-advisory

## Affected
- npm: `git-add-remote` — affected >=0

## Details
git-add-remote through 1.0.0 is vulnerable to Command Injection. It allows execution of arbitrary commands via the name argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7630
- https://github.com/jonschlinkert/git-add-remote/blob/master/index.js#L21
- https://snyk.io/vuln/SNYK-JS-GITADDREMOTE-564269
