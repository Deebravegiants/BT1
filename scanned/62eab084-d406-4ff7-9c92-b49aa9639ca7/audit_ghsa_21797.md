# [C] push-dir Enables OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-926x-m6m5-3mmp
CVE: CVE-2019-10803
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-926x-m6m5-3mmp
Type: github-advisory

## Affected
- npm: `push-dir` — affected >=0

## Details
push-dir through 0.4.1 allows execution of arbritary commands. Arguments provided as part of the variable `opt.branch` is not validated before being provided to the `git` command within [index.js#L139](https://github.com/L33T-KR3W/push-dir/blob/master/index.js#L139). This could be abused by an attacker to inject arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10803
- https://github.com/L33T-KR3W/push-dir/blob/master/index.js#L139
- https://snyk.io/vuln/SNYK-JS-PUSHDIR-559009
