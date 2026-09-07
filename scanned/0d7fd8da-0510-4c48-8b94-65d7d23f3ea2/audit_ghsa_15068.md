# [M] @fastify/reply-from JSON Content-Type parsing confusion

## Summary
Severity: Medium
Advisory: GHSA-v2v2-hph8-q5xp
CVE: CVE-2023-51701
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-v2v2-hph8-q5xp
Type: github-advisory

## Affected
- npm: `@fastify/reply-from` — affected >=0 <9.6.0

## Details
### Impact

The main repo of fastify use [fast-content-type-parse](https://github.com/fastify/fast-content-type-parse) to parse request Content-Type, which will [trim after split](https://github.com/fastify/fast-content-type-parse/blob/2776d054dd48e9ce40b8d5e5ff9b46fee82b95f1/index.js#L59).

The [fastify-reply-from](https://github.com/fastify/fastify-reply-from/blob/b79a22d6eb9a0b52cfbe8eb2cb22ad65f5a39e64/index.js#L118C14-L118C14) have not use this repo to unify the parse of Content-Type, which [won't trim](https://github.com/fastify/fastify-reply-from/blob/b79a22d6eb9a0b52cfbe8eb2cb22ad65f5a39e64/index.js#L118C14-L118C14).

As a result, a reverse proxy server built with `@fastify/reply-from` could misinterpret the incoming body by passing an header `ContentType: application/json ; charset=utf-8`. This can lead to bypass of security checks.

### Patches

`@fastify/reply-from` v9.6.0 include the fix. 

### Workarounds

There are no known workarounds.

### References

Hackerone Report: https://hackerone.com/reports/2295770.

## References
- https://github.com/fastify/fastify-reply-from/security/advisories/GHSA-v2v2-hph8-q5xp
- https://nvd.nist.gov/vuln/detail/CVE-2023-51701
- https://github.com/fastify/fastify-reply-from/commit/cbd7c17c09e6476268e34f5e499a6b923e8acc18
- https://github.com/fastify/fastify-reply-from
- https://github.com/fastify/fastify-reply-from/releases/tag/v9.6.0
