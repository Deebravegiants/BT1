# [M] @fastify/busboy vulnerable to CRLF injection via multipart Content-Disposition filename and name

## Summary
Severity: Medium
Advisory: CVE-2026-74866
Aliases: GHSA-gxm5-99cw-xjw9
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-74866
Type: osv

## Details
@fastify/busboy is a multipart form-data parser for Node.js. Its multipart part-header parser splits header lines only on the two-byte carriage-return line-feed sequence, so a lone carriage return or line feed embedded in a part header is not treated as a line break and is carried verbatim into the parsed Content-Disposition filename and field name handed to the application. An attacker who uploads a file whose filename or field name contains a bare carriage return or line feed can inject control characters into consumers that trust the parser to return clean values, enabling filesystem filename pollution, log forging, or header injection when the value is forwarded to a carriage-return-sensitive sink. All versions of @fastify/busboy up to and including 3.2.1 are affected. The issue is fixed in version 3.2.2, which rejects any header line that still contains a bare carriage return or line feed. Users should upgrade to 3.2.2, and consumers such as @fastify/multipart should bump their @fastify/busboy dependency to pull in the fix.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74866.json
- https://github.com/fastify/busboy/security/advisories/GHSA-gxm5-99cw-xjw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-74866
