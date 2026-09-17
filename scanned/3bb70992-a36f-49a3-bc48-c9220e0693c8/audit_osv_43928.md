# [H] fastify vulnerable to authentication bypass via malformed URLs reaching encapsulated not-found handlers

## Summary
Severity: High
Advisory: CVE-2026-76169
Aliases: GHSA-p68q-wchp-6fh7
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-76169
Type: osv

## Details
fastify versions >= 4.0.0 and before 5.12.2 can route a malformed URL sent under one plugin prefix to the custom not-found handler of a different sibling plugin, and invoke it without the preHandler hook declared for that handler. The internal not-found router for encapsulated handlers dispatches malformed paths through a single shared handler pointer before URL decoding, ignoring the prefix and skipping the selected handler's normal lifecycle. An unauthenticated attacker can therefore reach an authentication-protected private fallback through an unrelated public prefix and read its full response, bypassing the authentication hook and breaking prefix encapsulation. Users should upgrade to fastify 5.12.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76169.json
- https://github.com/fastify/fastify/security/advisories/GHSA-p68q-wchp-6fh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-76169
