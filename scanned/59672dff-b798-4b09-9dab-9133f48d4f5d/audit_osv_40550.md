# [M] CrossWatch: Unauthenticated /api/app-auth/status endpoint leaks active session metadata (IP, User-Agent, session IDs)

## Summary
Severity: Medium
Advisory: CVE-2026-53497
Aliases: GHSA-rv3j-r4h5-q3cj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-53497
Type: osv

## Details
CrossWatch (CW) is a synchronization engine. Prior to version 0.9.21, GET /api/app-auth/status is accessible without authentication and returns the other_sessions array, which exposes metadata of all active sessions — including originating IP addresses, User-Agent strings, internal session IDs, and creation/expiry timestamps. Any unauthenticated network attacker can enumerate this data without credentials. Version 0.9.21 fixes the issue.

## References
- https://github.com/cenodude/CrossWatch/releases/tag/v0.9.21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53497.json
- https://github.com/cenodude/CrossWatch/security/advisories/GHSA-rv3j-r4h5-q3cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-53497
