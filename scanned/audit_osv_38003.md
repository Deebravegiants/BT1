# [M] Coolify: Password reset link poisoning via X-Forwarded-Host header spoofing

## Summary
Severity: Medium
Advisory: CVE-2026-34198
Aliases: GHSA-cgj8-7m5q-x5gv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34198
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the TrustProxies middleware trusts all proxies ($proxies = '*'), accepting X-Forwarded-Host from any source. The TrustHosts middleware, intended to prevent host header attacks, has a circular caching dependency that prevents it from ever validating hosts. When a password reset is requested, the ResetPassword notification generates the reset URL using url(route(..., false)), which derives the host from the (spoofable) request. An unauthenticated attacker can trigger a password reset email containing a link pointing to an attacker-controlled domain, enabling token theft and account takeover. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34198.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-cgj8-7m5q-x5gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34198
- https://github.com/coollabsio/coolify/commit/98569e4edbfc316877c9e0d27ea89fab3c49e3bd
- https://github.com/coollabsio/coolify/pull/9193
