# [C] prebid-server's request forgery vulnerability allows for possible host environment data extraction

## Summary
Severity: Critical
Advisory: GHSA-4p3g-4hcj-wpvx
CVE: CVE-2026-54735
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-4p3g-4hcj-wpvx
Type: github-advisory

## Affected
- Go: `github.com/prebid/prebid-server/v4` — affected >=0 <4.4.0
- Go: `github.com/prebid/prebid-server/v3` — affected >=0
- Go: `github.com/prebid/prebid-server/v2` — affected >=0
- Go: `github.com/prebid/prebid-server` — affected >=0

## Details
### Impact
Certain bidder adapters accept user-supplied parameters that are interpolated into outbound request URLs. Without proper input validation, a malicious actor could craft bid request parameters that cause the server to send HTTP requests to unintended destinations, potentially exposing internal network services or sensitive server endpoints to unauthorized access.

### Patches
Patched in [v4.4.0](https://github.com/prebid/prebid-server/releases/tag/v4.4.0)

### Workarounds
If one is unable to update, please make sure that the affected bidder adapters are disabled.

## References
- https://github.com/prebid/prebid-server/security/advisories/GHSA-4p3g-4hcj-wpvx
- https://github.com/prebid/prebid-server/pull/4802
- https://github.com/prebid/prebid-server/commit/494ac271cd4b5024df9123ef25ca3cff96390be3
- https://github.com/prebid/prebid-server
- https://github.com/prebid/prebid-server/releases/tag/v4.4.0
