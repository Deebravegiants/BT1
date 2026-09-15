# [H] @fastify/reply-from vulnerable to cross-upstream request routing via URL cache key collision

## Summary
Severity: High
Advisory: CVE-2026-16158
Aliases: GHSA-v574-6498-x57v
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-16158
Type: osv

## Details
Impact: @fastify/reply-from versions from 8.3.1 up to but not including 12.6.4 build the internal URL cache key by concatenating the destination and source path without a delimiter. Different destination and source pairs can therefore produce the same key while resolving to different upstream URLs. When getUpstream selects an upstream from request data, a URL cached for one upstream can be reused for a request intended for another upstream, causing cross-upstream data access and modification. The default configuration is affected. Setting disableCache to true prevents the behavior. Patches: upgrade to @fastify/reply-from 12.6.4. Workarounds: pass disableCache: true when registering the plugin.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16158.json
- https://github.com/fastify/fastify-reply-from/security/advisories/GHSA-v574-6498-x57v
- https://nvd.nist.gov/vuln/detail/CVE-2026-16158
