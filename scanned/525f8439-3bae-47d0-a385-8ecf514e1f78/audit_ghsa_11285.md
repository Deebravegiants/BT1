# [M] Parse Server LiveQuery subscription with invalid regular expression crashes server

## Summary
Severity: Medium
Advisory: GHSA-827p-g5x5-h86c
CVE: CVE-2026-32770
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-827p-g5x5-h86c
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.6.0-alpha.19
- npm: `parse-server` — affected >=0 <8.6.43

## Details
### Impact

A remote attacker can crash the Parse Server by subscribing to a LiveQuery with an invalid regular expression pattern. The server process terminates when the invalid pattern reaches the regex engine during subscription matching, causing denial of service for all connected clients.

### Patches

The fix validates regular expression patterns at subscription time, rejecting invalid patterns before they are stored. Additionally, a defense-in-depth try-catch prevents any subscription matching error from crashing the server process.

### Workarounds

Disable LiveQuery if it is not needed.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-827p-g5x5-h86c
- https://nvd.nist.gov/vuln/detail/CVE-2026-32770
- https://github.com/parse-community/parse-server/pull/10197
- https://github.com/parse-community/parse-server/pull/10199
- https://github.com/parse-community/parse-server
