# [C] deferred-exec Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-54w4-2f2p-f48h
CVE: CVE-2020-28438
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-54w4-2f2p-f48h
Type: github-advisory

## Affected
- npm: `deferred-exec` — affected >=0

## Details
A command injection vulnerability affects all versions of package deferred-exec. The injection point is located in line 42 in lib/deferred-exec.js

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28438
- https://github.com/danheberden/deferred-exec
- https://github.com/danheberden/deferred-exec/blob/master/lib/deferred-exec.js#L42
- https://security.snyk.io/vuln/SNYK-JS-DEFERREDEXEC-1050433
