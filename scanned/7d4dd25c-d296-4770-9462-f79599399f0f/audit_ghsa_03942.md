# [H] Downloads Resources over HTTP in unicode-json

## Summary
Severity: High
Advisory: GHSA-hw4r-xr38-hm8j
CVE: CVE-2016-10610
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-hw4r-xr38-hm8j
Type: github-advisory

## Affected
- npm: `unicode-json` — affected >=0 <2.0.0

## Details
Affected versions of `unicode-json` insecurely downloads resources over HTTP. 

In scenarios where an attacker has a privileged network position, they can modify or read such resources at will. While the exact severity of impact for a vulnerability like this is highly variable and depends on the behavior of the package itself, it ranges from being able to read sensitive information all the way up to and including remote code execution.


## Recommendation

Install version 2.0.0 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10610
- https://github.com/advisories/GHSA-hw4r-xr38-hm8j
- https://www.npmjs.com/advisories/206
