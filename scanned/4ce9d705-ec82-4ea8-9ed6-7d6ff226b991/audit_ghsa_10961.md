# [M] OpenClaw has a IPv6 multicast SSRF classifier bypass

## Summary
Severity: Medium
Advisory: GHSA-h97f-6pqj-q452
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-h97f-6pqj-q452
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
OpenClaw's SSRF IP classifier did not treat IPv6 multicast literals (`ff00::/8`) as blocked/private-internal. This allowed literal multicast hosts to pass SSRF preflight checks.

### Impact
A bypass in address classification existed for IPv6 multicast literals. OpenClaw's network fetch/navigation paths are constrained to HTTP/HTTPS and this was triaged as low-severity defense-in-depth hardening.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.24`
- Patched versions: `>= 2026.2.25` 

### Technical Details
The IPv6 private/internal range set omitted `multicast`, so addresses like `ff02::1` and `ff05::1:3` were not classified as blocked by the shared SSRF classifier.

### Fix Commit(s)
- `baf656bc6fd7f83b6033e6dbc2548ec75028641f`

### Release Process Note
`patched_versions` is pre-set to the planned next npm release (`2026.2.25`). Once that release is published on npm, the advisory is published.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h97f-6pqj-q452
- https://github.com/openclaw/openclaw/commit/baf656bc6fd7f83b6033e6dbc2548ec75028641f
- https://github.com/openclaw/openclaw
