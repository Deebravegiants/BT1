# [H] Downloads Resources over HTTP in broccoli-closure

## Summary
Severity: High
Advisory: GHSA-vvwp-3f54-xc39
CVE: CVE-2016-10635
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-vvwp-3f54-xc39
Type: github-advisory

## Affected
- npm: `broccoli-closure` — affected >=0 <1.3.1

## Details
Affected versions of `broccoli-closure` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `broccoli-closure`.


## Recommendation

Update to version 1.3.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10635
- https://github.com/advisories/GHSA-vvwp-3f54-xc39
- https://www.npmjs.com/advisories/242
