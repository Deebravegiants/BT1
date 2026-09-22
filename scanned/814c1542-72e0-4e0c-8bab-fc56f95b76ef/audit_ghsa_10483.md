# [M] Hono missing validation of cookie name on write path in setCookie()

## Summary
Severity: Medium
Advisory: GHSA-26pp-8wgv-hjvm
CWE: CWE-113
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-26pp-8wgv-hjvm
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.12

## Details
## Summary

Cookie names are not validated on the write path when using `setCookie()`, `serialize()`, or `serializeSigned()` to generate Set-Cookie headers.

While certain cookie attributes such as domain and path are validated, the cookie name itself may contain invalid characters.

This results in inconsistent handling of cookie names between parsing (read path) and serialization (write path).

## Details

When applications use `setCookie()`, `serialize()`, or `serializeSigned()` with a user-controlled cookie name, invalid values (e.g., containing control characters such as `\r` or `\n`) can be used to construct malformed `Set-Cookie` header values.

For example:

```
Set-Cookie: legit
X-Injected: evil=value
```

However, in modern runtimes such as Node.js and Cloudflare Workers, such invalid header values are rejected and result in a runtime error before the response is sent.

As a result, the reported header injection / response splitting behavior could not be reproduced in these environments.

## Impact

Applications that pass untrusted input as the cookie name to `setCookie()`, `serialize()`, or `serializeSigned()` may encounter runtime errors due to invalid header values.

In tested environments, malformed `Set-Cookie` headers are rejected before being sent, and the reported header injection behavior could not be reproduced.

This issue primarily affects correctness and robustness rather than introducing a confirmed exploitable vulnerability.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-26pp-8wgv-hjvm
- https://github.com/honojs/hono/commit/a586cd72e3f6122792e631ecf1817e5cabb803ec
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.12
