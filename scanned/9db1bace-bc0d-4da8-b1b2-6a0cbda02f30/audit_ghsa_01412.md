# [H] fuelux vulnerable to Cross-Site Scripting in Pillbox feature

## Summary
Severity: High
Advisory: GHSA-fwcw-5qw2-87mp
CVE: CVE-2016-1000235
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-fwcw-5qw2-87mp
Type: github-advisory

## Affected
- npm: `fuelux` — affected >=0 <3.15.7

## Details
Affected versions of `fuelux` contain a cross-site scripting vulnerability in the Pillbox feature. By supplying a script as a value for a new pillbox, it is possible to cause arbitrary script execution.

## Recommendation

Update to version 3.15.7 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000235
- https://github.com/ExactTarget/fuelux/issues/1841
- https://github.com/ExactTarget/fuelux/pull/1856
- https://github.com/ExactTarget/fuelux
- https://www.npmjs.com/advisories/133
