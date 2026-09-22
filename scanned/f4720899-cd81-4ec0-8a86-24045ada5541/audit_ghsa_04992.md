# [M] @sigstore/core has DSSE payloadType type-binding failure

## Summary
Severity: Medium
Advisory: GHSA-jfc7-64v2-mr8c
CVE: CVE-2026-48758
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-jfc7-64v2-mr8c
Type: github-advisory

## Affected
- npm: `@sigstore/core` — affected >=0 <3.2.1

## Details
### Impact
The `preAuthEncoding` function in `@sigstore/core` uses Node.js `'ascii'` encoding when converting the PAE (Pre-Authentication Encoding) string to bytes. This allows `payloadType` to be mutated after signing without invalidating the signature, breaking the type-binding guarantee that DSSE is designed to provide.

In `packages/core/src/dsse.ts`, the PAE function builds a string containing `payloadType` and then encodes it with `Buffer.from(prefix, 'ascii')`.

In Node.js, `'ascii'` encoding for string-to-Buffer is equivalent to `'latin1'`, which **truncates characters above U+00FF to their low byte**. This means for any ASCII character, there exist Unicode characters (at U+01xx, U+02xx, etc.) that produce the identical encoded byte:

| Original | Codepoint | Mutant | Codepoint | Encoded byte |
|----------|-----------|--------|-----------|--------------|
| `t`      | U+0074    | `Ŵ`    | U+0174    | `0x74`       |
| `e`      | U+0065    | `ť`    | U+0165    | `0x65`       |

An attacker can substitute every character in `payloadType` with a Unicode variant whose low byte matches, producing **identical PAE bytes** and a passing signature verification.

Additionally, `payloadType.length` returns the JavaScript string length (UTF-16 code units) rather than the UTF-8 byte length required by the DSSE spec, though this is only a contributing factor for non-ASCII types.

#### Reproduction

```javascript
const { preAuthEncoding } = require('@sigstore/core/dist/dsse.js');
const payload = Buffer.from('hello world');

const original = preAuthEncoding('text/plain', payload);
// U+01xx chars whose low bytes match the original ASCII chars
const mutant = preAuthEncoding('\u0174\u0165\u0178\u0174/\u0170\u016c\u0161\u0169\u016e', payload);

console.log('PAE bytes equal:', original.equals(mutant)); // true — should be false
```

## References
- https://github.com/sigstore/sigstore-js/security/advisories/GHSA-jfc7-64v2-mr8c
- https://github.com/sigstore/sigstore-js
