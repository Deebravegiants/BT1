# [C] Command Injection in umount

## Summary
Severity: Critical
Advisory: GHSA-6q48-vjq2-mwcj
CVE: CVE-2020-7628
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-6q48-vjq2-mwcj
Type: github-advisory

## Affected
- npm: `umount` — affected >=0

## Details
All versions of `umount ` are vulnerable to Command Injection. The package fails to sanitize input rules and passes it directly to an `exec` call on the `umount` function . This may allow attackers to execute arbitrary code in the system if the `device` value passed to the function is user-controlled.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7628
- https://snyk.io/vuln/SNYK-JS-UMOUNT-564265
- https://www.npmjs.com/advisories/1512
