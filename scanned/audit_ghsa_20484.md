# [C] OS Command Injection in node-mpv

## Summary
Severity: Critical
Advisory: GHSA-cqr2-xhg6-p268
CVE: CVE-2020-7632
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-07
Source: https://github.com/advisories/GHSA-cqr2-xhg6-p268
Type: github-advisory

## Affected
- npm: `node-mpv` — affected >=0

## Details
node-mpv through 1.4.3 is vulnerable to Command Injection. It allows execution of arbitrary commands via the options argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7632
- https://github.com/j-holub/Node-MPV/blob/master/lib/util.js#L34
- https://snyk.io/vuln/SNYK-JS-NODEMPV-564426
