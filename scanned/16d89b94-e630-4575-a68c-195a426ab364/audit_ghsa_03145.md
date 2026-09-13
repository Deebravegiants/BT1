# [C] xmlhttprequest and xmlhttprequest-ssl vulnerable to Arbitrary Code Injection

## Summary
Severity: Critical
Advisory: GHSA-h4j5-c7cj-74xg
CVE: CVE-2020-28502
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-04
Source: https://github.com/advisories/GHSA-h4j5-c7cj-74xg
Type: github-advisory

## Affected
- npm: `xmlhttprequest` — affected >=0 <1.7.0
- npm: `xmlhttprequest-ssl` — affected >=0 <1.6.2

## Details
This affects the package xmlhttprequest before 1.7.0; all versions of package xmlhttprequest-ssl. Provided requests are sent synchronously (`async=False` on `xhr.open`), malicious user input flowing into `xhr.send` could result in arbitrary code being injected and run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28502
- https://github.com/driverdan/node-XMLHttpRequest/commit/983cfc244c7567ad6a59e366e55a8037e0497fe6
- https://github.com/mjwwit/node-XMLHttpRequest/commit/ee1e81fc67729c7c0eba5537ed7fe1e30a6b3291
- https://github.com/driverdan/node-XMLHttpRequest/blob/1.6.0/lib/XMLHttpRequest.js#L480
- https://github.com/driverdan/node-XMLHttpRequest/blob/1.6.0/lib/XMLHttpRequest.js%23L480
- https://github.com/mjwwit/node-XMLHttpRequest/blob/ae38832a0f1347c5e96dda665402509a3458e302/lib/XMLHttpRequest.js#L531
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1082937
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1082938
- https://snyk.io/vuln/SNYK-JS-XMLHTTPREQUEST-1082935
- https://snyk.io/vuln/SNYK-JS-XMLHTTPREQUESTSSL-1082936
