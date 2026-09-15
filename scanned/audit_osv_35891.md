# [C] @fastify/http-proxy vulnerable to prefix escape via URL-encoded characters

## Summary
Severity: Critical
Advisory: CVE-2026-16117
Aliases: GHSA-mx7v-qhg9-2mvv
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-16117
Type: osv

## Details
Impact: @fastify/http-proxy versions up to and including 11.5.0 fail to rewrite the request prefix when the prefix segment is URL-encoded. Fastify's router URL-decodes paths for route matching, but request.url retains the original encoded form, and the prefix-rewrite step uses a literal string replace against the decoded prefix. A request that encodes one or more characters of the configured prefix therefore matches the route but skips the rewrite, so the raw encoded path is forwarded to the upstream unchanged. The upstream then decodes the path and serves it, letting an attacker reach upstream paths that the proxy was configured to hide via rewritePrefix, including internal or administrative endpoints.

Patches: upgrade to @fastify/http-proxy 11.6.0.

Workarounds: none.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16117.json
- https://github.com/fastify/fastify-http-proxy/security/advisories/GHSA-mx7v-qhg9-2mvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-16117
