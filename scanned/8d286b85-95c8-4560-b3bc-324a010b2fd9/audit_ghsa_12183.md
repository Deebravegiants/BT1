# [H] Denial of Service in ecstatic

## Summary
Severity: High
Advisory: GHSA-pm9p-9926-w68m
CVE: CVE-2016-10703
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-12-28
Source: https://github.com/advisories/GHSA-pm9p-9926-w68m
Type: github-advisory

## Affected
- npm: `ecstatic` — affected >=0 <2.0.0

## Details
`ecstatic`, a simple static file server middleware, is vulnerable to denial of service. If a payload with a large number of null bytes (`%00`) is provided by an attacker it can crash ecstatic by running it out of memory.


[Results from the original advisory](https://www.checkmarx.com/advisories/denial-of-service-dos-vulnerability-in-ecstatic-npm-package/)

```
A payload of 22kB caused a lag of 1 second,
A payload of 35kB caused a lag of 3 seconds,
A payload of 86kB caused the server to crash
```


## Recommendation

Update to version 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10703
- https://github.com/jfhbrook/node-ecstatic/commit/71ce93988ead4b561a8592168c72143907189f01
- https://github.com/jfhbrook/node-ecstatic/commit/71ce93988ead4b561a8592168c72143907189f01#diff-b2b5a88fb51675f1aa1065c093dce1ee
- https://advisory.checkmarx.net/advisory/CX-2016-4450
- https://github.com/advisories/GHSA-pm9p-9926-w68m
- https://github.com/jfhbrook/node-ecstatic
- https://www.checkmarx.com/advisories/denial-of-service-dos-vulnerability-in-ecstatic-npm-package
- https://www.npmjs.com/advisories/553
