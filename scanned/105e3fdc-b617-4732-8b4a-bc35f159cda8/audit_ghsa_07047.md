# [C] Ghost: Cache-poisoning XSS in Ghost frontend via x-ghost-preview header

## Summary
Severity: Critical
Advisory: GHSA-62q6-4hv4-vjrw
CVE: CVE-2026-53943
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-62q6-4hv4-vjrw
Type: github-advisory

## Affected
- npm: `ghost` — affected >=4.0.0 <6.37.0

## Details
### Impact

When Ghost is behind a shared caching layer that results in cached content being shared between different visitors (e.g., Fastly, Cloudflare, nginx proxy_cache, and others), an unauthenticated user could send an `x-ghost-preview` header that altered the rendered frontend response. In affected cache configurations, that response could be stored and served to subsequent visitors requesting the same page, allowing cache poisoning of request-specific preview output. 

When running Ghost's frontend and admin panel on the same domain this could be used to take over staff user accounts. When running these on different domains staff accounts have no exposure. 

### Vulnerable versions

This vulnerability is present in Ghost from v4.0 up to v6.36.0.

### Patches

v6.37.0 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost).

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update).

If you suspect a credential compromise, use the “Reset all authentication” dialogue under Settings / Danger Zone. This is available starting with Ghost v6.41.0. 

### Workarounds

At the caching layer, bypass the cache for `x-ghost-preview` requests. 

### References

Ghost thanks [CryptoCat](https://linkedin.com/in/cryptocat) for disclosing this vulnerability responsibly.

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-62q6-4hv4-vjrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53943
- https://github.com/TryGhost/Ghost
