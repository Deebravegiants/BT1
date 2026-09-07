# [H] Pingora update for MadeYouReset HTTP/2 vulnerability

## Summary
Severity: High
Advisory: GHSA-393w-9x6h-8gc7
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-393w-9x6h-8gc7
Type: github-advisory

## Affected
- crates.io: `pingora-core` — affected >=0 <0.6.0

## Details
Pingora deployments that include HTTP/2 server support may be affected by the vulnerability described in CVE-2025-8671. Under certain conditions, Pingora applications may allocate buffers before the HTTP/2 reset and resulting stream cancellation is processed by the server. Repeated resets can force excessive memory consumption and lead to denial-of-service.

**Impact**:
On affected versions, malicious clients could trigger unusually high memory consumption, which may result in service instability or process termination.

**Credits**:
Reported responsibly by security researcher [Gal Bar Nahum](https://github.com/galbarnahum) (@[galbarnahum](https://github.com/galbarnahum))

**Mitigation**:
This issue is addressed by ensuring Pingora uses patched versions of HTTP/2 dependencies that include reset-handling safeguards to release connection resources before excessive memory buildup. Users should upgrade to the latest Pingora release, which incorporates the required fixes.
- Users are requested to upgrade to latest version of Pingora >= 0.6.0

## References
- https://github.com/cloudflare/pingora/security/advisories/GHSA-393w-9x6h-8gc7
- https://github.com/cloudflare/pingora
- https://github.com/cloudflare/pingora/releases/tag/0.6.0
