# [H] headless-browser-lite downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-g95j-p8f6-pwh4
CVE: CVE-2016-10625
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g95j-p8f6-pwh4
Type: github-advisory

## Affected
- npm: `headless-browser-lite` — affected >=0 <2015.4.18-a

## Details
Affected versions of `headless-browser-lite` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `headless-browser-lite`.


## Recommendation

Update to version 2015.4.18-a or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10625
- https://github.com/kaizhu256/node-phantomjs-lite/commit/96f766e5674e8462b5f5bbd4494390988f0a3916
- https://github.com/kaizhu256/node-phantomjs-lite/commit/f6e2a9489446a1dabe175aa8c14a1c55ca824520
- https://github.com/advisories/GHSA-g95j-p8f6-pwh4
- https://www.npmjs.com/advisories/230
