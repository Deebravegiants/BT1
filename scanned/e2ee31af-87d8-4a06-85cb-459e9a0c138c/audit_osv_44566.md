# [H] fastify vulnerable to header validation bypass via incomplete schema case normalization

## Summary
Severity: High
Advisory: CVE-2026-84428
Aliases: GHSA-9q9j-q6p8-xq58
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84428
Type: osv

## Details
fastify versions before 5.12.2 implement the case-insensitive nature of HTTP header names by lowercasing names in a route's header schema before compiling it, but the transformation is incomplete: it lowercases the properties keys and the root-level required array, and does not lowercase the trigger and dependent names inside the JSON Schema Draft 7 dependencies keyword. Because Node stores request header names in lowercase, a canonical-case dependency such as requiring an authentication header whenever a privileged-mode header is present never matches, and the presence assertion is silently skipped. An unauthenticated remote client can therefore send the header that activates a privileged branch while omitting the header the dependency was meant to require, bypassing the conditional check. Users should upgrade to fastify 5.12.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84428.json
- https://github.com/fastify/fastify/security/advisories/GHSA-9q9j-q6p8-xq58
- https://nvd.nist.gov/vuln/detail/CVE-2026-84428
