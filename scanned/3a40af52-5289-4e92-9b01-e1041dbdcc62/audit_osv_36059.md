# [H] @fastify/busboy vulnerable to Denial of Service via oversized multipart boundary

## Summary
Severity: High
Advisory: CVE-2026-19484
Aliases: GHSA-xjh9-v7x6-24jw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-19484
Type: osv

## Details
@fastify/busboy is a multipart form-data parser. In versions 3.1.0 through 3.2.0, a remote unauthenticated attacker can stall the Node.js event loop by sending a multipart request whose boundary is crafted to a specific length. The vendored streaming search stores its skip table in a fixed 256 entry byte array, and a boundary of exactly 252 bytes makes the search needle 256 bytes, which truncates the default skip distance to zero and turns the search into a CPU bound loop on a small body. A single small request can keep one core busy and deny service to other requests handled by the same process. The issue is fixed in @fastify/busboy 3.2.1, which widens the skip table so the skip distance is preserved. Users should upgrade to 3.2.1.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19484.json
- https://github.com/fastify/busboy/security/advisories/GHSA-xjh9-v7x6-24jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-19484
