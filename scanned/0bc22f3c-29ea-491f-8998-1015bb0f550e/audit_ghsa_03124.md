# [M] Arbitrary command execution in roar-pidusage

## Summary
Severity: Medium
Advisory: GHSA-xfxf-qw26-hr33
CVE: CVE-2021-23380
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-xfxf-qw26-hr33
Type: github-advisory

## Affected
- npm: `roar-pidusage` — affected >=0

## Details
This affects all current versions of package roar-pidusage. If attacker-controlled user input is given to the stat function of this package on certain operating systems, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23380
- https://github.com/Svjard/pidusage
- https://github.com/Svjard/pidusage/blob/772cd2bd675ff7b1244b6fe3d7541692b1b9e42c/lib/stats.js%23L103
- https://snyk.io/vuln/SNYK-JS-ROARPIDUSAGE-1078528
