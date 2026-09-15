# [C] Command Injection in pdfinfojs

## Summary
Severity: Critical
Advisory: GHSA-3pxp-6963-46r9
CVE: CVE-2018-3746
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-3pxp-6963-46r9
Type: github-advisory

## Affected
- npm: `pdfinfojs` — affected >=0 <0.4.1

## Details
Versions of `pdfinfojs` before 0.4.1 are vulnerable to command injection. This is exploitable if an attacker can control the filename parameter that is passed into the `pdfinfojs` constructor.


## Recommendation

Update to version 0.4.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3746
- https://github.com/fagbokforlaget/pdfinfojs/commit/5cc59cd8aa13ca8d16bb41da8affdfef370ad4fd
- https://hackerone.com/reports/330957
- https://github.com/advisories/GHSA-3pxp-6963-46r9
- https://www.npmjs.com/advisories/643
