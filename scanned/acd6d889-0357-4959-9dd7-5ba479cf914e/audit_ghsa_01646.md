# [C] Command Injection in node-df

## Summary
Severity: Critical
Advisory: GHSA-wp7m-mrvf-599c
CVE: CVE-2019-15597
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-14
Source: https://github.com/advisories/GHSA-wp7m-mrvf-599c
Type: github-advisory

## Affected
- npm: `node-df` — affected >=0

## Details
All versions of `node-df` are vulnerable to Command Injection. The package fails to sanitize filenames passed to the  `file` option. If this value is user-controlled it  may allow attackers to run arbitrary commands in the server.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15597
- https://hackerone.com/reports/703412
- https://github.com/adriano-di-giovanni/node-df
- https://www.npmjs.com/advisories/1431
