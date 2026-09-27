# [H] pngcrush-installer downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-g93h-75m9-3qq4
CVE: CVE-2016-10570
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-g93h-75m9-3qq4
Type: github-advisory

## Affected
- npm: `pngcrush-installer` — affected >=0 <1.8.10

## Details
Affected versions of `pngcrush-installer` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `pngcrush-installer`.


## Recommendation

Update to version 1.8.10 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10570
- https://github.com/advisories/GHSA-g93h-75m9-3qq4
- https://www.npmjs.com/advisories/189
