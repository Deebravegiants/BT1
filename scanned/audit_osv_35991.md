# [H] @fastify/multipart vulnerable to Denial of Service via aborted upload after fileSize limit

## Summary
Severity: High
Advisory: CVE-2026-18549
Aliases: GHSA-vmph-573x-85f6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-18549
Type: osv

## Details
@fastify/multipart is a multipart form-data parser for Fastify. In versions from 5.3.0 up to but not including 10.1.1, when the busboy fileSize limit truncates a file part, the plugin clears its internal current-file reference while the underlying stream is still open. If the client then aborts the connection before sending the terminating boundary, the abort cleanup finds no stream to destroy, so saveRequestFiles() never settles, the request handler hangs, and the temporary file already written to disk is never cleaned up. An unauthenticated client can repeat this to permanently leak temporary files and suspended handler executions, leading to disk and event-loop exhaustion. The issue is fixed in @fastify/multipart 10.1.1. Users should upgrade to 10.1.1.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18549.json
- https://github.com/fastify/fastify-multipart/security/advisories/GHSA-vmph-573x-85f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-18549
