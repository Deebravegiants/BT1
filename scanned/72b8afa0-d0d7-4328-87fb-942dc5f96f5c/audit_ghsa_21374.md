# [H] css-what vulnerable to ReDoS due to use of insecure regular expression

## Summary
Severity: High
Advisory: GHSA-p28h-cc7q-c4fg
CVE: CVE-2022-21222
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-p28h-cc7q-c4fg
Type: github-advisory

## Affected
- npm: `css-what` — affected >=0 <2.1.3

## Details
The package css-what before 2.1.3 is vulnerable to Regular Expression Denial of Service (ReDoS) due to the use of insecure regular expression in the `re_attr` variable of index.js. The exploitation of this vulnerability could be triggered via the parse function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21222
- https://github.com/fb55/css-what/commit/dc510929790da6617e7aa93a616498b22f6a6b72
- https://github.com/fb55/css-what
- https://github.com/fb55/css-what/blob/a38effd5a8f5506d75c7f8f13cbd8c76248a3860/index.js#23L12
- https://github.com/fb55/css-what/blob/a38effd5a8f5506d75c7f8f13cbd8c76248a3860/index.js%23L12
- https://lists.debian.org/debian-lts-announce/2023/03/msg00001.html
- https://security.snyk.io/vuln/SNYK-JS-CSSWHAT-3035488
