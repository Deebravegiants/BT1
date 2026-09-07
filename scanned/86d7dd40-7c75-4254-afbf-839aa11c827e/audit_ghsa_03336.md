# [M] Arbitrary code execution in kill-by-port

## Summary
Severity: Medium
Advisory: GHSA-mm4f-47ch-f7hx
CVE: CVE-2021-23363
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-mm4f-47ch-f7hx
Type: github-advisory

## Affected
- npm: `kill-by-port` — affected >=0 <0.0.2

## Details
This affects the package kill-by-port before 0.0.2. If (attacker-controlled) user input is given to the killByPort function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23363
- https://github.com/GuyMograbi/kill-by-port/commit/ea5b1f377e196a4492e05ff070eba8b30b7372c4
- https://github.com/GuyMograbi/kill-by-port
- https://github.com/GuyMograbi/kill-by-port/blob/16dcbe264b6b4a5ecf409661b42836dd286fd43f/index.js#23L8
- https://snyk.io/vuln/SNYK-JS-KILLBYPORT-1078531
