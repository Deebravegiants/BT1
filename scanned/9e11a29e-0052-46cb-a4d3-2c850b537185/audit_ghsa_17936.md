# [H] Komari vulnerable to 2FA Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-jhmr-57cj-q6g9
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-jhmr-57cj-q6g9
Type: github-advisory

## Affected
- Go: `github.com/komari-monitor/komari` — affected >=0 <0.0.0-20250809064056-cc3d54bff4c6

## Details
### Summary

Logic error in 2FA verification condition allows bypass of two-factor authentication

### Details

https://github.com/komari-monitor/komari/blob/bd5a6934e1b79a12cf1e6a9bba5372d0e04f3abc/api/login.go#L55

There is no way for `Verify2Fa` to return an error **AND** true as `ok` at the same time, any codes are considered as valid.

### PoC

Use any 6 digits as 2FA code

### Impact

Bypass 2FA Authentication

## References
- https://github.com/komari-monitor/komari/security/advisories/GHSA-jhmr-57cj-q6g9
- https://github.com/komari-monitor/komari/commit/cc3d54bff4c6495beaa1c7483379cd04542c557f
- https://github.com/komari-monitor/komari
- https://github.com/komari-monitor/komari/blob/bd5a6934e1b79a12cf1e6a9bba5372d0e04f3abc/api/login.go#L55
- https://github.com/komari-monitor/komari/releases/tag/1.0.4-fix1
