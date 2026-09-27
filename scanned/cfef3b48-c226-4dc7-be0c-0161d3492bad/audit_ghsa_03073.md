# [H] Arbitrary Code Execution in json-ptr

## Summary
Severity: High
Advisory: GHSA-rrqv-vjrw-hrcr
CWE: CWE-74
Ecosystem: npm
Published: 2021-05-26
Source: https://github.com/advisories/GHSA-rrqv-vjrw-hrcr
Type: github-advisory

## Affected
- npm: `json-ptr` — affected >=0 <2.1.0

## Details
There is a security vulnerability in `json-ptr` versions prior to v2.1.0 in which an unscrupulous actor may execute arbitrary code. If your code sends un-sanitized user input to json-ptr's .get() method, your project is vulnerable to this injection-style vulnerability.

## References
- https://github.com/418sec/json-ptr/pull/3
- https://github.com/flitbit/json-ptr/blob/456a1728b45c8663bb1ac20a249c5fb17495ec6b/README.md#security-vulnerability-prior-to-v210
- https://github.com/flitbit/json-ptr/blob/master/src/util.ts%23L174
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1038396
- https://snyk.io/vuln/SNYK-JS-JSONPTR-1016939
- https://www.huntr.dev/bounties/2-npm-json-ptr
- https://www.npmjs.com/advisories/1706
- https://www.npmjs.com/package/json-ptr
