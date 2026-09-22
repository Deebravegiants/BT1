# [H] @fastify/busboy vulnerable to Denial of Service via prototype-named multipart part header

## Summary
Severity: High
Advisory: CVE-2026-19481
Aliases: GHSA-x8mw-p69m-v3mx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-19481
Type: osv

## Details
@fastify/busboy is a multipart form-data parser. In versions 1.0.0 through 3.2.0, an attacker who can submit multipart form-data can crash the parser by sending a part header whose name is a prototype-inherited property such as __proto__ or constructor. The internal header parser stores headers in a plain JavaScript object and assumes each value is an array, so an inherited property name resolves to a truthy non-array value and triggers a TypeError. In the common pipe integration the failure surfaces as an error event, but in direct write or end usage the exception is thrown synchronously and can terminate the Node.js process, causing an unauthenticated denial of service. The issue is fixed in @fastify/busboy 3.2.1, which creates the header object with a null prototype. Users should upgrade to 3.2.1.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19481.json
- https://github.com/fastify/busboy/security/advisories/GHSA-x8mw-p69m-v3mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-19481
