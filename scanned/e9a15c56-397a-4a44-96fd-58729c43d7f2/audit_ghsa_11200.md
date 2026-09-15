# [M] Parse Server has denylist `requestKeywordDenylist` keyword scan bypass through nested object placement

## Summary
Severity: Medium
Advisory: GHSA-q342-9w2p-57fp
CVE: CVE-2026-30938
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-q342-9w2p-57fp
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <8.6.12
- npm: `parse-server` — affected >=9.0.0-alpha.1 <9.5.1-alpha.1

## Details
### Impact

The `requestKeywordDenylist` security control can be bypassed by placing any nested object or array before a prohibited keyword in the request payload. This is caused by a logic bug that stops scanning sibling keys after encountering the first nested value. Any custom `requestKeywordDenylist` entries configured by the developer are equally by-passable using the same technique.

All Parse Server deployments are affected. The `requestKeywordDenylist` is enabled by default.

### Patches

The fix replaces the recursive object scanner with an iterative stack-based traversal that processes all nested values without prematurely exiting the scan loop. This also eliminates a potential stack overflow on deeply nested payloads.

### Workarounds

Use a Cloud Code `beforeSave` trigger to validate incoming data for prohibited keywords across all classes.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-q342-9w2p-57fp
- Fix Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.1-alpha.1
- Fix Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.12

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-q342-9w2p-57fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-30938
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.12
- https://github.com/parse-community/parse-server/releases/tag/9.5.1-alpha.1
