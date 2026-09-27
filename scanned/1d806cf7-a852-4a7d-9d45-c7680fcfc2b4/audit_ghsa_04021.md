# [H] Downloads Resources over HTTP in nw

## Summary
Severity: High
Advisory: GHSA-hv96-xxx2-5v7w
CVE: CVE-2016-10588
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-hv96-xxx2-5v7w
Type: github-advisory

## Affected
- npm: `nw` — affected >=0 <0.23.6-1

## Details
Affected versions of `nw` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `nw`.


## Recommendation

Update to version 0.23.6-1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10588
- https://github.com/nwjs/npm-installer/commit/adb4df1e012d38a3872578d484291b9af07aad5b
- https://github.com/advisories/GHSA-hv96-xxx2-5v7w
- https://www.npmjs.com/advisories/166
