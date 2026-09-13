# [M] Measured is vulnerable to Path Traversal attacks during class initialization

## Summary
Severity: Medium
Advisory: GHSA-29g5-m8v7-v564
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-29g5-m8v7-v564
Type: github-advisory

## Affected
- RubyGems: `measured` — affected >=0 <3.2.1

## Details
### Impact
A path traversal vulnerability exists where an attacker with access to manipulate inputs when initializing the `Measured::Cache::Json class` would be able to instruct the library to read arbitrary files.

### Patches
Users should update to the latest version.

## References
- https://github.com/Shopify/measured/security/advisories/GHSA-29g5-m8v7-v564
- https://github.com/Shopify/measured/commit/d6319985a2304d97c085e3dc45c98af554f4be76
- https://github.com/Shopify/measured
