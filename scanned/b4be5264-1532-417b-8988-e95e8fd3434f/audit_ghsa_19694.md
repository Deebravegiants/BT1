# [M] Pitchfork HTTP Request/Response Splitting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pfqj-w6r6-g86v
CVE: CVE-2025-30221
CWE: CWE-113
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-pfqj-w6r6-g86v
Type: github-advisory

## Affected
- RubyGems: `pitchfork` — affected >=0 <0.11.0

## Details
### Impact
HTTP Response Header Injection in Pitchfork Versions < 0.11.0 when used in conjunction with Rack 3

### Patches
The issue was fixed in Pitchfork release 0.11.0

### Workarounds
There are no known work arounds. Users must upgrade.

## References
- https://github.com/Shopify/pitchfork/security/advisories/GHSA-pfqj-w6r6-g86v
- https://nvd.nist.gov/vuln/detail/CVE-2025-30221
- https://github.com/Shopify/pitchfork/commit/17ed9b61bf9f58957065f7405b66102daf86bf55
- https://github.com/Shopify/pitchfork
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pitchfork/CVE-2025-30221.yml
