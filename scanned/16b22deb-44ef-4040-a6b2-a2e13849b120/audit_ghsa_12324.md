# [C] Potential Command Injection in printer

## Summary
Severity: Critical
Advisory: GHSA-5c8j-xr24-2665
CVE: CVE-2014-3741
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-28
Source: https://github.com/advisories/GHSA-5c8j-xr24-2665
Type: github-advisory

## Affected
- npm: `printer` — affected >=0 <0.0.2

## Details
Versions 0.0.1 and earlier of `printer` are affected by a command injection vulnerability resulting from a failure to sanitize command arguments properly in the `printDirect()` function. 



## Recommendation

Update to version 0.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3741
- https://github.com/tojocky/node-printer/commit/e001e38738c17219a1d9dd8c31f7d82b9c0013c7
- https://github.com/advisories/GHSA-5c8j-xr24-2665
- https://github.com/tojocky/node-printer
- https://www.npmjs.com/advisories/27
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
