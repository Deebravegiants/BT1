# [C] Command Injection in gitlabhook

## Summary
Severity: Critical
Advisory: GHSA-549f-73hh-mj38
CVE: CVE-2019-5485
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-16
Source: https://github.com/advisories/GHSA-549f-73hh-mj38
Type: github-advisory

## Affected
- npm: `gitlabhook` — affected >=0

## Details
All versions of `gitlabhook` are vulnerable to Command Injection. The package does not validate input the body of POST request and concatenates it to an exec call, allowing attackers to run arbitrary commands in the system.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5485
- https://hackerone.com/reports/685447
- http://packetstormsecurity.com/files/154598/NPMJS-gitlabhook-0.0.17-Remote-Command-Execution.html
