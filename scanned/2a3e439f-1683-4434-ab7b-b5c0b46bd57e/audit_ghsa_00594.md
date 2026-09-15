# [H] windows-build-tools downloads Resources over HTTP

## Summary
Severity: High
Advisory: GHSA-9p47-w5xp-f4xr
CVE: CVE-2017-16003
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-9p47-w5xp-f4xr
Type: github-advisory

## Affected
- npm: `windows-build-tools` — affected >=0 <1.0.0

## Details
Affected versions of `windows-build-tools` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `windows-build-tools`.


## Recommendation

Update to version 1.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16003
- https://github.com/felixrieseberg/windows-build-tools/commit/9835d33e68f2cb5e4d148e954bb3ed0221d98e90
- https://github.com/felixrieseberg/windows-build-tools/commit/9835d33e68f2cb5e4d148e954bb3ed0221d98e90)
- https://github.com/advisories/GHSA-9p47-w5xp-f4xr
- https://www.npmjs.com/advisories/304
