# [H] Clipboard-based XSS

## Summary
Severity: High
Advisory: GHSA-qh7x-j4v8-qw5w
CVE: CVE-2021-41086
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-qh7x-j4v8-qw5w
Type: github-advisory

## Affected
- npm: `jsuites` — affected >=0 <4.9.11

## Details
### Impact
XSS against the user.

### Details
jsuites is vulnerable to DOM based XSS if the user can be tricked into copying _anything_ from a malicious and pasting it into the html editor. This is because a part of the clipboard content is directly written to `innerHTML` causing XSS.

### References
The Curious Case of Copy & Paste – on risks of pasting arbitrary content in browsers: https://research.securitum.com/the-curious-case-of-copy-paste/

## References
- https://github.com/jsuites/jsuites/security/advisories/GHSA-qh7x-j4v8-qw5w
- https://nvd.nist.gov/vuln/detail/CVE-2021-41086
- https://github.com/jsuites/jsuites/commit/d47a6f4e143188dde2742f4cffd313e1068ad3b3
- https://github.com/jsuites/jsuites/commit/fe1d3cc5e339f2f4da8ed1f9f42271fdf9cbd8d2
- https://github.com/jsuites/jsuites
- https://www.npmjs.com/package/jsuites
