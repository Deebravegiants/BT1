# [M] Nodejs ‘undici’ vulnerable to CRLF Injection via Content-Type

## Summary
Severity: Medium
Advisory: GHSA-f772-66g8-q5h3
CVE: CVE-2022-35948
CWE: CWE-74, CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-f772-66g8-q5h3
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <5.8.2

## Details
### Impact

`=< undici@5.8.0` users are vulnerable to _CRLF Injection_ on headers when using unsanitized input as request headers, more specifically, inside the `content-type` header.

Example:

```
import { request } from 'undici'

const unsanitizedContentTypeInput =  'application/json\r\n\r\nGET /foo2 HTTP/1.1'

await request('http://localhost:3000, {
    method: 'GET',
    headers: {
      'content-type': unsanitizedContentTypeInput
    },
})
```

The above snippet will perform two requests in a single `request` API call:

1) `http://localhost:3000/`
2) `http://localhost:3000/foo2`

### Patches

This issue was patched in Undici v5.8.1

### Workarounds

Sanitize input when sending content-type headers using user input.

## For more information
If you have any questions or comments about this advisory:

- Open an issue in [undici repository](https://github.com/nodejs/undici/issues)
- To make a report, follow the [SECURITY](https://github.com/nodejs/node/blob/HEAD/SECURITY.md) document

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-f772-66g8-q5h3
- https://nvd.nist.gov/vuln/detail/CVE-2022-35948
- https://github.com/nodejs/undici/commit/66165d604fd0aee70a93ed5c44ad4cc2df395f80
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v5.8.2
