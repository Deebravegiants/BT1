# [H] @fastify/middie standalone engine vulnerable to Denial of Service via malformed percent-encoded paths

## Summary
Severity: High
Advisory: CVE-2026-14181
Aliases: GHSA-qcc9-jh8q-47vh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-14181
Type: osv

## Details
@fastify/middie versions 9.1.0 through 9.3.2 fail to guard the URL normalization step used by the standalone engine when incoming request paths contain malformed percent-encoded sequences. Inputs such as an incomplete percent escape or a truncated multibyte sequence cause the underlying decoder to throw synchronously, and the exception escapes the middie normalize step and terminates the Node.js process. The bypass affects applications that call middie.run directly on the standalone engine API, causing an immediate denial of service for all connected clients until restart. Applications using the Fastify plugin path are not affected because Fastifys error handler catches the exception. Patches: upgrade to @fastify/middie 9.3.3. Workarounds: migrate from the standalone engine API to the Fastify plugin path, where the framework error handler catches the exception.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14181.json
- https://github.com/fastify/middie/security/advisories/GHSA-qcc9-jh8q-47vh
- https://nvd.nist.gov/vuln/detail/CVE-2026-14181
