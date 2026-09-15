# [M] Coder's workspace app CORS origin check can be bypassed via UUID-based subdomain spoofing

## Summary
Severity: Medium
Advisory: GHSA-5wg6-jmq2-53pw
CVE: CVE-2026-55438
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-5wg6-jmq2-53pw
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

Coder's subdomain-based workspace app proxy allowed the same-owner CORS check to be bypassed. When a workspace-name subdomain segment parsed as a UUID, the workspace was resolved by ID without confirming the URL's username matched the real owner, while the CORS middleware trusted the unverified username in the hostname.

> **Note:** Practical exploitation requires subdomain app routing (wildcard hostname) enabled and a victim who visits the attacker's crafted app URL while authenticated.

### Impact

An authenticated user could craft a subdomain encoding their own workspace UUID and a victim's username. If the victim visited the attacker's URL, the attacker's JavaScript could issue credentialed cross-origin `fetch()` requests to the victim's workspace apps and read the responses, exfiltrating data accessible through those apps.

### Patches

The fix validates the subdomain username against the resolved workspace's actual owner and bases the same-owner CORS decision on the authoritative owner identity.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

None.

### Resources

- Fix: #26086, #26085

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22434) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-5wg6-jmq2-53pw
- https://github.com/coder/coder/pull/26085
- https://github.com/coder/coder/pull/26086
- https://github.com/coder/coder
