# [C] Some CORS middleware allow untrusted origins

## Summary
Severity: Critical
Advisory: GHSA-v84h-653v-4pq9
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-v84h-653v-4pq9
Type: github-advisory

## Affected
- Go: `github.com/jub0bs/fcors` — affected >=0 <0.9.0

## Details
### Impact

Some CORS middleware (more specifically those created by specifying two or more origin patterns whose hosts share a proper suffix) incorrectly allow some untrusted origins, thereby opening the door to cross-origin attacks from the untrusted origins in question.

For example, specifying origin patterns `https://foo.com` and `https://bar.com` (in that order) would yield a middleware that would incorrectly allow untrusted origin `https://barfoo.com`.

### Patches

Patched in v0.9.0.

### Workarounds

None.

## References
- https://github.com/jub0bs/fcors/security/advisories/GHSA-v84h-653v-4pq9
- https://github.com/jub0bs/fcors/commit/08d85c149a418a583315cee066d4a35cc817219d
- https://github.com/jub0bs/fcors/commit/b5dcb889a49def37d7d9c25deb7135f4eb45625e
- https://github.com/jub0bs/fcors
