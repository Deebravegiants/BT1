# [C] Full authentication bypass if SASL authorization username is specified

## Summary
Severity: Critical
Advisory: GHSA-4g76-w3xw-2x6w
CVE: CVE-2023-27582
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-14
Source: https://github.com/advisories/GHSA-4g76-w3xw-2x6w
Type: github-advisory

## Affected
- Go: `github.com/foxcpp/maddy` — affected >=0.2.0 <0.6.3

## Details
### Impact

maddy 0.2.0 - 0.6.2 allows a full authentication bypass if SASL authorization username is specified when using the PLAIN authentication mechanisms. Instead of validating the specified authorization username, it is accepted as is after checking the credentials for the authentication username.

### Patches

maddy 0.6.3 includes the fix for the bug. 

### Workarounds

There is no way to fix the issue without upgrading.

### References

* Commit that introduced the vulnerable code: https://github.com/foxcpp/maddy/commit/55a91a37b71210f34f98f4d327c30308fe24399a
* Fix: https://github.com/foxcpp/maddy/commit/9f58cb64b39cdc01928ec463bdb198c4c2313a9c

## References
- https://github.com/foxcpp/maddy/security/advisories/GHSA-4g76-w3xw-2x6w
- https://nvd.nist.gov/vuln/detail/CVE-2023-27582
- https://github.com/foxcpp/maddy/commit/55a91a37b71210f34f98f4d327c30308fe24399a
- https://github.com/foxcpp/maddy/commit/9f58cb64b39cdc01928ec463bdb198c4c2313a9c
- https://github.com/foxcpp/maddy
- https://github.com/foxcpp/maddy/releases/tag/v0.6.3
