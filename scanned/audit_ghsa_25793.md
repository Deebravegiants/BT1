# [H] Command Injection in ungit

## Summary
Severity: High
Advisory: GHSA-hf8c-xr89-vfm5
CVE: CVE-2022-25766
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-22
Source: https://github.com/advisories/GHSA-hf8c-xr89-vfm5
Type: github-advisory

## Affected
- npm: `ungit` — affected >=0 <1.5.20

## Details
The package ungit before 1.5.20 are vulnerable to Remote Code Execution (RCE) via argument injection. The issue occurs when calling the /api/fetch endpoint. User controlled values (remote and ref) are passed to the git fetch command. By injecting some git options it was possible to get arbitrary command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25766
- https://github.com/FredrikNoren/ungit/pull/1510
- https://github.com/FredrikNoren/ungit/pull/1511
- https://github.com/FredrikNoren/ungit
- https://github.com/FredrikNoren/ungit/blob/master/CHANGELOG.md%231520
- https://snyk.io/vuln/SNYK-JS-UNGIT-2414099
