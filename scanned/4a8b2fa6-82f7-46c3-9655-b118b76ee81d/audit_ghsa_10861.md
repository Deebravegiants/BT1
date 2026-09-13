# [H] Elysia has a string URL format ReDoS

## Summary
Severity: High
Advisory: GHSA-f45g-68q3-5w8x
CVE: CVE-2026-30837
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-f45g-68q3-5w8x
Type: github-advisory

## Affected
- npm: `elysia` — affected >=0 <1.4.26

## Details
### Impact
`t.String({ format: 'url' })` is vulnerable to redos

Repeating a partial url format (protocol and hostname) multiple times cause regex to slow down significantly
```js
'http://a'.repeat(n)
```

Here's a table demonstrating how long it takes to process repeated partial url format
| `n` repeat | elapsed_ms |
| --- | --- |
| 1024 | 33.993 |
| 2048 | 134.357 |
| 4096 | 537.608 |
| 8192 | 2155.842 |
| 16384 | 8618.457 |
| 32768 | 34604.139 |

### Patches
Patched by 1.4.26, please kindly update `elysia` to >= 1.4.26 

Here's how long it takes after the patch
| `n` repeat | elapsed_ms |
| --- | --- |
| 1024 | 0.194 |
| 2048 | 0.274 |
| 4096 | 0.455 |
| 8192 | 0.831 |
| 16384 | 1.632 |
| 32768 | 3.052 |

### Workarounds
1. It's recommended to always limit URL format to a reasonable length
```ts
t.String({
	format: 'url',
	maxLength: 288
})
```

2. If a long URL format is necessary, to patch this without updating to 1.4.26, add the following code to any part of your codebase
```js
import { FormatRegistry } from '@sinclair/typebox'

FormatRegistry.Delete('url')
FormatRegistry.Set('url', (value) =>
	/^(?:https?|ftp):\/\/(?:[^\s:@]+(?::[^\s@]*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u{00a1}-\u{ffff}]+-)*[a-z0-9\u{00a1}-\u{ffff}]+)(?:\.(?:[a-z0-9\u{00a1}-\u{ffff}]+-)*[a-z0-9\u{00a1}-\u{ffff}]+)*(?:\.(?:[a-z\u{00a1}-\u{ffff}]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$/iu.test(
		value
	)
)
```

## References
- https://github.com/elysiajs/elysia/security/advisories/GHSA-f45g-68q3-5w8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-30837
- https://github.com/EdamAme-x/elysia-poc-redos
- https://github.com/elysiajs/elysia
