# [M] Cross-site Scripting in sanitize-url

## Summary
Severity: Medium
Advisory: GHSA-hqq7-2q2v-82xq
CVE: CVE-2021-23648
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-17
Source: https://github.com/advisories/GHSA-hqq7-2q2v-82xq
Type: github-advisory

## Affected
- npm: `@braintree/sanitize-url` — affected >=0 <6.0.0

## Details
The package `@braintree/sanitize-url` before 6.0.0 is vulnerable to Cross-site Scripting (XSS) due to improper sanitization in the `sanitizeUrl` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23648
- https://github.com/braintree/sanitize-url/pull/40
- https://github.com/braintree/sanitize-url/pull/40/commits/e5afda45d9833682b705f73fc2c1265d34832183
- https://github.com/braintree/sanitize-url
- https://github.com/braintree/sanitize-url/blob/main/src/index.ts%23L11
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2PFW6Q2LXXWTFRTMTRN4ZGADFRQPKJ3D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/36GUEPA5TPSC57DZTPYPBL6T7UPQ2FRH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HLAQRRGNSO5MYCPAXGPH2OCSHOGHSQMQ
- https://snyk.io/vuln/SNYK-JS-BRAINTREESANITIZEURL-2339882
