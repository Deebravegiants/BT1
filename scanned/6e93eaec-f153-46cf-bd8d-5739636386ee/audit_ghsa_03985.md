# [H] Downloads Resources over HTTP in js-given

## Summary
Severity: High
Advisory: GHSA-rqwh-c535-j9hw
CVE: CVE-2016-10638
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-rqwh-c535-j9hw
Type: github-advisory

## Affected
- npm: `js-given` — affected >=0 <0.0.18

## Details
Affected versions of `js-given` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `js-given`.


## Recommendation

Update to version 0.0.18 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10638
- https://github.com/jsGiven/jsGiven/commit/92f750739c7b9b6e704e562ad34e2ad148acad64)
- https://github.com/advisories/GHSA-rqwh-c535-j9hw
- https://www.npmjs.com/advisories/241
