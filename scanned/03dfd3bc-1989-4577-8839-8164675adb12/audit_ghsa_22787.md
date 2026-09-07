# [C] chrome-launcher subject to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-gp2j-mg4w-2rh5
CVE: CVE-2020-7645
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gp2j-mg4w-2rh5
Type: github-advisory

## Affected
- npm: `chrome-launcher` — affected >=0 <0.13.2

## Details
chrome-launcher prior to 0.13.2 is subject to OS Command Injection via the `$HOME` environment variable in Linux operating systems. This issue is patched in version 0.13.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7645
- https://github.com/GoogleChrome/chrome-launcher/pull/197
- https://github.com/GoogleChrome/chrome-launcher
- http://snyk.io/vuln/SNYK-JS-CHROMELAUNCHER-537575
