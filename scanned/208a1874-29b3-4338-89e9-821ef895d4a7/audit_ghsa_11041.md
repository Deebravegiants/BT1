# [M] Saloon has a Fixture Name Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f7xc-5852-fj99
CVE: CVE-2026-33183
CWE: CWE-125, CWE-22, CWE-787
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-f7xc-5852-fj99
Type: github-advisory

## Affected
- Packagist: `saloonphp/saloon` — affected >=0 <4.0.0

## Details
### Impact
Users with MockResponse fixtures that use path traversal.

### Patches
Upgrade to Saloon v4+

Upgrade guide: https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4

### Description
Fixture names were used to build file paths under the configured fixture directory without validation. A name containing path segments (e.g. ../traversal or ../../etc/passwd) resulted in a path outside that directory. When the application read a fixture (e.g. for mocking) or wrote one (e.g. when recording responses), it could read or write files anywhere the process had access. If the fixture name was derived from user or attacker-controlled input (e.g. request parameters or config), this constituted a path traversal vulnerability and could lead to disclosure of sensitive files or overwriting of critical files. The fix adds validation in the fixture layer (rejecting names with /, \, .., or null bytes, and restricting to a safe character set) and defence-in-depth in the storage layer (ensuring the resolved path remains under the base directory before any read or write).

### Credits
Saloon thanks @HuajiHD for finding the issue and recommending solutions and @JonPurvis for applying the fix.

## References
- https://github.com/saloonphp/saloon/security/advisories/GHSA-f7xc-5852-fj99
- https://nvd.nist.gov/vuln/detail/CVE-2026-33183
- https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4
- https://github.com/saloonphp/saloon
