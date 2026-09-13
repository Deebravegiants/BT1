# [H] Fastify's Content-Type header tab character allows body validation bypass

## Summary
Severity: High
Advisory: GHSA-jx2c-rxcm-jvmq
CVE: CVE-2026-25223
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-jx2c-rxcm-jvmq
Type: github-advisory

## Affected
- npm: `fastify` — affected >=0 <5.7.2

## Details
### Impact

A validation bypass vulnerability exists in Fastify where request body validation schemas specified by Content-Type can be completely circumvented. By appending a tab character (`\t`) followed by arbitrary content to the Content-Type header, attackers can bypass body validation while the server still processes the body as the original content type.

For example, a request with `Content-Type: application/json\ta` will bypass JSON schema validation but still be parsed as JSON.

This vulnerability affects all Fastify users who rely on Content-Type-based body validation schemas to enforce data integrity or security constraints. The concrete impact depends on the handler implementation and the level of trust placed in the validated request body, but at the library level, this allows complete bypass of body validation for any handler using Content-Type-discriminated schemas.

This issue is a regression or missed edge case from the fix for a previously reported vulnerability.

### Patches

This vulnerability has been patched in **Fastify v5.7.2**. All users should upgrade to this version or later immediately.

### Workarounds

If upgrading is not immediately possible, user can implement a custom `onRequest` hook to reject requests containing tab characters in the Content-Type header:

```javascript
fastify.addHook('onRequest', async (request, reply) => {
  const contentType = request.headers['content-type']
  if (contentType && contentType.includes('\t')) {
    reply.code(400).send({ error: 'Invalid Content-Type header' })
  }
})
```

### Resources

- https://github.com/fastify/fastify/blob/759e9787b5669abf953068e42a17bffba7521348/lib/validation.js#L272
- https://github.com/fastify/fastify/blob/759e9787b5669abf953068e42a17bffba7521348/lib/content-type-parser.js#L125
- [Fastify Validation and Serialization Documentation](https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/)
- https://hackerone.com/reports/3464114

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-jx2c-rxcm-jvmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25223
- https://github.com/fastify/fastify/commit/32d7b6add39ddf082d92579a58bea7018c5ac821
- https://hackerone.com/reports/3464114
- https://fastify.dev/docs/latest/Reference/Validation-and-Serialization
- https://github.com/fastify/fastify
- https://github.com/fastify/fastify/blob/759e9787b5669abf953068e42a17bffba7521348/lib/content-type-parser.js#L125
- https://github.com/fastify/fastify/blob/759e9787b5669abf953068e42a17bffba7521348/lib/validation.js#L272
