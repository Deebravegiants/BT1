# [C] Command Injection in npm-programmatic

## Summary
Severity: Critical
Advisory: GHSA-426h-24vj-qwxf
CVE: CVE-2020-7614
CWE: CWE-20, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-04-23
Source: https://github.com/advisories/GHSA-426h-24vj-qwxf
Type: github-advisory

## Affected
- npm: `npm-programmatic` — affected >=0

## Details
All versions of `npm-programmatic ` are vulnerable to Command Injection. The package fails to sanitize input rules and passes it directly to an `exec` call on the `install`, `uninstall` and `list` functions . This may allow attackers to execute arbitrary code in the system if the package name passed to the function is user-controlled.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7614
- https://github.com/Manak/npm-programmatic/blob/master/index.js#L18
- https://snyk.io/vuln/SNYK-JS-NPMPROGRAMMATIC-564115
- https://www.npmjs.com/advisories/1507
