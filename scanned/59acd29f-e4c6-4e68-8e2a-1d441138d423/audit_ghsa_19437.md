# [H] Fastify vulnerable to invalid content-type parsing, which could lead to validation bypass

## Summary
Severity: High
Advisory: GHSA-mg2h-6x62-wpwc
CVE: CVE-2025-32442
CWE: CWE-1287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-04-18
Source: https://github.com/advisories/GHSA-mg2h-6x62-wpwc
Type: github-advisory

## Affected
- npm: `fastify` — affected >=5.0.0 <5.3.2
- npm: `fastify` — affected >=4.29.0 <4.29.1

## Details
### Impact

In applications that specify different validation strategies for different content types, it's possible to bypass the validation by providing a _slightly altered_ content type such as with different casing or altered whitespacing before `;`.

Users using the the following pattern are affected:

```js
fastify.post('/', {
  handler(request, reply) {
    reply.code(200).send(request.body)
  },
  schema: {
    body: {
      content: {
        'application/json': {
          schema: {
            type: 'object',
            properties: {
              'foo': {
                type: 'string',
              }
            },
            required: ['foo']
          }
        },
      }
    }
  }
})
```

User using the following pattern are **not** affected:

```js
fastify.post('/', {
  handler(request, reply) {
    reply.code(200).send(request.body)
  },
  schema: {
    body: {
      type: 'object',
      properties: {
        'foo': {
          type: 'string',
        }
      },
      required: ['foo']
    }
  }
})
```

### Patches

This was patched in v5.3.1, but unfortunately it did not cover all problems. This has been fully patched in v5.3.2.
Version v4.9.0 was also affected by this issue. This has been fully patched in v4.9.1.

### Workarounds

Do not specify multiple content types in the schema.

### References
_Are there any links users can visit to find out more?_

https://hackerone.com/reports/3087928

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-mg2h-6x62-wpwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-32442
- https://github.com/fastify/fastify/commit/436da4c06dfbbb8c24adee3a64de0c51e4f47418
- https://github.com/fastify/fastify/commit/f3d2bcb3963cd570a582e5d39aab01a9ae692fe4
- https://hackerone.com/reports/3087928
- https://github.com/fastify/fastify
