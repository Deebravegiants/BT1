# [M] Regular Expression Denial of Service in bleach

## Summary
Severity: Medium
Advisory: GHSA-mvmf-cvfx-qg55
CVE: CVE-2014-8881
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-mvmf-cvfx-qg55
Type: github-advisory

## Affected
- npm: `bleach` — affected >=0.0.0

## Details
All versions of the `bleach` package are vulnerable to a regular expression denial of service attack when certain types of input are passed into the sanitize function.



## Recommendation

The `bleach` package is not currently maintained, and has not seen an update since 2014. 

To mitigate this issue, it is necessary to use an alternative module that is actively maintained and provides similar functionality. There are [multiple modules fitting this criteria available on npm.](https://www.npmjs.com/search?q=html%20sanitizer&page=1&ranking=optimal).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8881
- https://snyk.io/vuln/npm:bleach:20151024
- https://www.npmjs.com/advisories/47
