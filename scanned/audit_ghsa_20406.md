# [C] OS Command Injection in diskusage-ng

## Summary
Severity: Critical
Advisory: GHSA-3269-x4pw-vffg
CVE: CVE-2020-7631
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-07
Source: https://github.com/advisories/GHSA-3269-x4pw-vffg
Type: github-advisory

## Affected
- npm: `diskusage-ng` — affected >=0

## Details
diskusage-ng through 0.2.4 is vulnerable to Command Injection.It allows execution of arbitrary commands via the path argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7631
- https://github.com/iximiuz/node-diskusage-ng/blob/master/lib/posix.js#L11
- https://snyk.io/vuln/SNYK-JS-DISKUSAGENG-564425
