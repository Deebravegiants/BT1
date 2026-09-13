# [H] Downloads Resources over HTTP in healthcenter

## Summary
Severity: High
Advisory: GHSA-j336-34q7-cgj3
CVE: CVE-2016-10684
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-j336-34q7-cgj3
Type: github-advisory

## Affected
- npm: `healthcenter` — affected >=0

## Details
Affected versions of `healthcenter` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `healthcenter`.


## Recommendation

This package has been deprecated, and moved to a new package on npm: [`appmetrics`](https://npmjs.com/package/appmetrics).

In order to mitigate this vulnerability, please install the `appmetrics` package in place of `healthcenter` via the following commands:
```
npm uninstall healthcenter -s
npm install appmetrics -s
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10684
- https://github.com/advisories/GHSA-j336-34q7-cgj3
- https://www.npmjs.com/advisories/288
