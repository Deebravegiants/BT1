# [H] Cross-Site Scripting in bootstrap-tagsinput

## Summary
Severity: High
Advisory: GHSA-v2jq-9475-r5g8
CVE: CVE-2016-1000227
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-v2jq-9475-r5g8
Type: github-advisory

## Affected
- npm: `bootstrap-tagsinput` — affected >=0

## Details
All versions of `bootstrap-tagsinput` are vulnerable to cross-site scripting when user input is passed into the `itemTitle` parameter unmodified, as the package fails to properly sanitize or encode user input for that parameter.



## Recommendation

This package is not actively maintained, and has not seen an update since 2015. 

Because of this, the simplest mitigation is to avoid using the `itemTitle` parameter. With over 200 open issues and over 100 open pull requests as of 2/2018, it seems unlikely that the author has any intention of maintaining the module. If avoiding the use of `itemTitle` indefinitely is acceptable, this is a workable solution. If not, the best available mitigation is to use a fork of the module that is actively maintained and provides similar functionality. There are [many such forks to choose from available on github.](https://github.com/bootstrap-tagsinput/bootstrap-tagsinput/network/members).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000227
- https://github.com/bootstrap-tagsinput/bootstrap-tagsinput/issues/501
- https://github.com/bootstrap-tagsinput
- https://www.npmjs.com/advisories/124
