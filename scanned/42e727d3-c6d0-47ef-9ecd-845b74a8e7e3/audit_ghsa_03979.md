# [H] Downloads Resources over HTTP in bkjs-wand

## Summary
Severity: High
Advisory: GHSA-4wm5-q7wv-6jx3
CVE: CVE-2016-10571
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-4wm5-q7wv-6jx3
Type: github-advisory

## Affected
- npm: `bkjs-wand` — affected >=0 <0.3.2

## Details
Affected versions of `bkjs-wand` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `bkjs-wand`.


## Recommendation

Update to version 0.3.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10571
- https://github.com/advisories/GHSA-4wm5-q7wv-6jx3
- https://www.npmjs.com/advisories/220
