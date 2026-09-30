# [H] @fastify/multipart vulnerable to Denial of Service via temporary file leak on aborted upload

## Summary
Severity: High
Advisory: CVE-2026-19474
Aliases: GHSA-62qx-hpj5-j6hc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-19474
Type: osv

## Details
@fastify/multipart is a multipart form-data parser for Fastify. In versions from 3.0.0 up to but not including 10.1.1, request.saveRequestFiles() can leave completed temporary files on disk when a client disconnects while the parser is advancing between multipart parts. The iterator rejection that occurs between parts falls outside the per-file cleanup path, so an earlier completed file is never removed. An unauthenticated client can repeat this to cause persistent, linear disk consumption, leading to denial of service. This is an incomplete-fix variant of CVE-2025-24033. The issue is fixed in @fastify/multipart 10.1.1. Users should upgrade to 10.1.1.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19474.json
- https://github.com/fastify/fastify-multipart/security/advisories/GHSA-62qx-hpj5-j6hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-19474
