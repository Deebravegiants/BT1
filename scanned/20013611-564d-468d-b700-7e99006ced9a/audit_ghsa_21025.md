# [M] express-xss-sanitizer vulnerable to Prototype Pollution via allowedTags attribute

## Summary
Severity: Medium
Advisory: GHSA-grjp-4jmr-mjcw
CVE: CVE-2022-21169
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-grjp-4jmr-mjcw
Type: github-advisory

## Affected
- npm: `express-xss-sanitizer` — affected >=0 <1.1.3

## Details
The package express-xss-sanitizer before 1.1.3 is vulnerable to Prototype Pollution via the `allowedTags` attribute, allowing the attacker to bypass xss sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21169
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/issues/4
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/commit/3bf8aaaf4dbb1c209dcb8d87a82711a54c1ab39a
- https://github.com/AhmedAdelFahim/express-xss-sanitizer
- https://runkit.com/embed/w306l6zfm7tu
- https://security.snyk.io/vuln/SNYK-JS-EXPRESSXSSSANITIZER-3027443
