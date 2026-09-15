# [H] fuseki downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-3627-w2qr-5fxr
CVE: CVE-2016-10576
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-3627-w2qr-5fxr
Type: github-advisory

## Affected
- npm: `fuseki` — affected >=0 <1.0.1

## Details
Affected versions of `fuseki` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `fuseki`.


## Recommendation

Update to version 1.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10576
- https://github.com/advisories/GHSA-3627-w2qr-5fxr
- https://www.npmjs.com/advisories/278
