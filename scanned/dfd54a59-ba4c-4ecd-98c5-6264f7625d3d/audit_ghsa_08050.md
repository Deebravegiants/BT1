# [H] Parse Dashboard Has a Cache Key Collision that Leaks Master Key to Read-Only Sessions

## Summary
Severity: High
Advisory: GHSA-jhp4-jvq3-w5xr
CVE: CVE-2026-27610
CWE: CWE-1289
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-jhp4-jvq3-w5xr
Type: github-advisory

## Affected
- npm: `parse-dashboard` — affected >=7.3.0-alpha.42 <9.0.0-alpha.8

## Details
### Impact

The `ConfigKeyCache` uses the same cache key for both master key and read-only master key when resolving function-typed keys. Under specific timing conditions, a read-only user can receive the cached full master key, or a regular user can receive the cached read-only master key.

### Patches

The fix uses distinct cache keys for master key and read-only master key.

### Workarounds

Avoid using function-typed master keys, or remove the `agent` configuration block from your dashboard configuration.

### Resources

- GitHub advisory: https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-jhp4-jvq3-w5xr
- Fixed in: https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8

## References
- https://github.com/parse-community/parse-dashboard/security/advisories/GHSA-jhp4-jvq3-w5xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27610
- https://github.com/parse-community/parse-dashboard/commit/f92a9ef5246d57e51696bd881a15f3b133b2bb50
- https://github.com/parse-community/parse-dashboard
- https://github.com/parse-community/parse-dashboard/releases/tag/9.0.0-alpha.8
