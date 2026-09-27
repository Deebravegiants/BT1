# [H] Elysia affected by arbitrary code injection through cookie config

## Summary
Severity: High
Advisory: GHSA-8vch-m3f4-q8jf
CVE: CVE-2025-66457
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-8vch-m3f4-q8jf
Type: github-advisory

## Affected
- npm: `elysia` — affected >=0 <1.4.18

## Details
Arbitrary code execution from cookie config. If dynamic cookies are enabled (ie there exists a schema for cookies), the cookie config is injected into the compiled route without first being sanitised.

Availability of this exploit is generally low, as it requires write access to either the Elysia app's source code (in which case the vulnerability is meaningless) or write access to the cookie config (perhaps where it is assumed to be provisioned by the environment). 

However when combined with GHSA-hxj9-33pp-j2cc, this vulnerability allows for a full RCE chain.

### Impact
- aot enabled (default)
- cookie schema passed to route
- Cookie config controllable eg. via env

Example of vulnerable code
```js
new Elysia({
	cookie: {
		secrets: `' + console.log('pwned from secrets') + '`
	},
})
	.get("/", () => "hello world", {
		cookie: t.Cookie({
			foo: t.Any(),
		}),
	})
```

POC: https://github.com/sportshead/elysia-poc

### Patches
Patched by 1.4.17 (https://github.com/elysiajs/elysia/pull/1564)

Reference commit:
- https://github.com/elysiajs/elysia/pull/1564/commits/26935bf76ebc43b4a43d48b173fc853de43bb51e
- https://github.com/elysiajs/elysia/pull/1564/commits/3af978663e437dccc6c1a2a3aff4b74e1574849e

### Workarounds
Sanitize cookie-related env input

```typescript
const overrideUnsafeQuote = (value: string) =>
	// '`' + value + '`'
	'`' + value.replace(/'/g, '\\`').replace(/\${/g, '$\\{') + '`'
```

## References
- https://github.com/elysiajs/elysia/security/advisories/GHSA-8vch-m3f4-q8jf
- https://github.com/elysiajs/elysia/security/advisories/GHSA-hxj9-33pp-j2cc
- https://nvd.nist.gov/vuln/detail/CVE-2025-66457
- https://github.com/elysiajs/elysia/pull/1564
- https://github.com/elysiajs/elysia/commit/26935bf76ebc43b4a43d48b173fc853de43bb51e
- https://github.com/elysiajs/elysia/commit/3af978663e437dccc6c1a2a3aff4b74e1574849e
- https://github.com/elysiajs/elysia
- https://github.com/sportshead/elysia-poc
