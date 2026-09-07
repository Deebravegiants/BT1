# [H] Potential for Script Injection in syntax-error

## Summary
Severity: High
Advisory: GHSA-5726-g6r9-5f22
CVE: CVE-2014-7192
CWE: CWE-94
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-5726-g6r9-5f22
Type: github-advisory

## Affected
- npm: `syntax-error` — affected >=0 <1.1.1

## Details
Versions of `syntax-error` prior to 1.1.1 are affected by a cross-site scripting vulnerability which may allow a malicious file to execute code when browserified. 

## Recommendation

Update to version 1.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7192
- https://github.com/substack/node-syntax-error/commit/9aa4e66eb90ec595d2dba55e6f9c2dd9a668b309
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96728
- https://github.com/advisories/GHSA-5726-g6r9-5f22
- https://github.com/substack/node-browserify/blob/master/changelog.markdown#421
- https://github.com/substack/node-syntax-error
- https://www.npmjs.com/advisories/37
- http://www-01.ibm.com/support/docview.wss?uid=swg21690815
