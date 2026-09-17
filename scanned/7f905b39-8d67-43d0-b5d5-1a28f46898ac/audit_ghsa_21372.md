# [H] Bifrost vulnerable to authentication check flaw that leads to authentication bypass

## Summary
Severity: High
Advisory: GHSA-mxrx-fg8p-5p5j
CVE: CVE-2022-39267
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-mxrx-fg8p-5p5j
Type: github-advisory

## Affected
- Go: `github.com/brokercap/Bifrost` — affected >=0 <1.8.7-release

## Details
### Impact
The admin and monitor user groups need to be authenticated by username and password. If we delete the X-Requested-With: XMLHttpRequest field in the request header,the authentication will be bypassed.

### Patches
https://github.com/brockercap/Bifrost/pull/201

### Workarounds
Upgrade to the latest version

## References
- https://github.com/brokercap/Bifrost/security/advisories/GHSA-mxrx-fg8p-5p5j
- https://nvd.nist.gov/vuln/detail/CVE-2022-39267
- https://github.com/brockercap/Bifrost/pull/201
- https://github.com/brokercap/Bifrost/commit/63da5c8eb7eb21639ea7ac199fe10b5e07b03a8a
- https://github.com/brokercap/Bifrost
