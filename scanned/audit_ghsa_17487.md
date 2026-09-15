# [C] Elysia vulnerable to prototype pollution with multiple standalone schema validation

## Summary
Severity: Critical
Advisory: GHSA-hxj9-33pp-j2cc
CVE: CVE-2025-66456
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-hxj9-33pp-j2cc
Type: github-advisory

## Affected
- npm: `elysia` — affected >=1.4.0 <1.4.17

## Details
Prototype pollution vulnerability in `mergeDeep` after merging results of two standard schema validations with the same key. Due to the ordering of merging, there must be an `any` type that is set as a `standalone` guard, to allow for the `__proto__` prop to be merged.

When combined with GHSA-8vch-m3f4-q8jf this allows for a full RCE by an attacker.

### Impact
Routes with more than 2 standalone schema validation, eg. zod

Example vulnerable code:
```typescript
import { Elysia } from "elysia"
import * as z from "zod"

const app = new Elysia()
	.guard({
		schema: "standalone",
		body: z.object({
			data: z.any()
		})
	})
	.post("/", ({ body }) => ({ body, win: {}.foo }), {
		body: z.object({
			data: z.object({
				messageId: z.string("pollute-me"),
			})
		})
	})
```

### Patches
Patched by 1.4.17 (https://github.com/elysiajs/elysia/pull/1564)

Reference commit:
- https://github.com/elysiajs/elysia/pull/1564/commits/26935bf76ebc43b4a43d48b173fc853de43bb51e
- https://github.com/elysiajs/elysia/pull/1564/commits/3af978663e437dccc6c1a2a3aff4b74e1574849e

### Workarounds
Remove `__proto__` key from body

Example plugin for removing `__proto__` from body

```typescript
new Elysia()
	.onTransform(({ body, headers }) => {
		if (headers['content-type'] === 'application/json')
			return JSON.parse(JSON.stringify(body), (k, v) => {
				if (k === '__proto__') return

				return v
			})
	})
```

## References
- https://github.com/elysiajs/elysia/security/advisories/GHSA-8vch-m3f4-q8jf
- https://github.com/elysiajs/elysia/security/advisories/GHSA-hxj9-33pp-j2cc
- https://nvd.nist.gov/vuln/detail/CVE-2025-66456
- https://github.com/elysiajs/elysia/pull/1564
- https://github.com/elysiajs/elysia/commit/26935bf76ebc43b4a43d48b173fc853de43bb51e
- https://github.com/elysiajs/elysia/commit/3af978663e437dccc6c1a2a3aff4b74e1574849e
- https://github.com/elysiajs/elysia
- https://github.com/sportshead/elysia-poc
