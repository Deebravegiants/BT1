# [M] undici vulnerable to cross-user cookie disclosure via Set-Cookie caching in shared caches

## Summary
Severity: Medium
Advisory: CVE-2026-84933
Aliases: GHSA-2jfj-6hjv-fm6j
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84933
Type: osv

## Details
undici's cache interceptor does not handle the Set-Cookie response header anywhere in its cache path, so it neither refuses to store nor strips that header. In shared cache mode, which is the default, an otherwise cacheable response that carries a Set-Cookie header, for example one marked with a public and max-age directive, is stored and then re-served to a later caller that matches the same cache key. As a result one caller's cookie is disclosed to a different caller, and an untrusted server can inject cookies into cached responses served to all subsequent callers. This violates the requirement that a shared cache must not store cookies. This affects undici versions from 7.0.0 up to 7.29.1 and from 8.0.0 up to 8.10.2. Users should upgrade to undici 7.29.1 or 8.10.2.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84933.json
- https://github.com/nodejs/undici/security/advisories/GHSA-2jfj-6hjv-fm6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-84933
