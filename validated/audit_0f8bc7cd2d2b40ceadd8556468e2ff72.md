### Title
Missing domain-origin validation in cookie deserialization/set path allows cross-origin cookie domain injection - ([File: modules/networking-common/src/cookie/deserialize.ts])

### Summary
`deserialize()` parses arbitrary `Domain=` attributes from a raw cookie string into `cookie.domain` with no origin check, and `CookieJar.set()` (`modules/networking-mobile/src/cookie/cookie-jar.ts`) only calls `validate()` (name/value checks) — never `assertMatchingDomain()` — before forwarding the cookie (including attacker-controlled `domain`) to the native store. `assertMatchingDomain` exists in `validators.ts` but is dead code, never invoked from any production path.

### Finding Description
`deserialize()` in [1](#0-0)  builds a `Cookie` object by generically mapping every `Key=Value` pair in the string onto the `cookie` record via `toFirstLower(key)`, so a raw string like `sid=abc; Domain=attacker.evil` will produce `{ name: 'sid', value: 'abc', domain: 'attacker.evil' }` with zero validation of the domain against any origin.

`assertMatchingDomain` is defined in `validators.ts` specifically to enforce RFC 6265 domain scoping [2](#0-1) , but it is exported and only ever referenced from its own spec file [3](#0-2) . Grepping the whole repo confirms no production call site invokes it.

`CookieJar.set()` in `networking-mobile` [4](#0-3)  only calls `validate(cookie)` (name/value checks, see `validators.ts` lines 69-72) before forwarding the cookie object — including any attacker-supplied `domain` — to `this.store.set(url, asNativeCookie(cookie), true)`. There is no call to `assertMatchingDomain(cookie.domain, urlDomain)` anywhere in this method, for either the string path (`store.setFromResponse`) or the object path.

### Impact Explanation
If any networking layer in the wallet parses a raw `Set-Cookie`-style string from an untrusted or cross-origin response with `deserialize()` and passes the resulting object into `CookieJar.set()`, the `domain` field is forwarded unchecked to the underlying native cookie store. The `assertMatchingDomain` guard that was designed to prevent this is not wired in anywhere, so there is no code-level defense against a cookie being associated with an attacker-chosen domain. This matches the class of bug in the question (session/auth cookie is not scoped to the origin that legitimately issued it), which could later cause the cookie to be sent to or read by the wrong origin (if native cookie storage APIs are permissive) — a wrong-origin/auth-scoping violation.

### Likelihood Explanation
The flaw itself (missing `assertMatchingDomain` call in `set()`, and unchecked parsing in `deserialize()`) is confirmed directly in production, non-test/non-mock code. However, no actual production call site in this repository was found that calls `deserialize()` on attacker/cross-origin data and then feeds the result into `CookieJar.set()` — the only importers of `@exodus/networking-common/cookie` besides `networking-common` itself are `networking-mobile`'s own module/spec files and mocks. Exploitability therefore depends on an as-yet-unidentified upstream caller performing this exact unsafe composition; within the current codebase this is a latent/defense-in-depth gap rather than a demonstrated end-to-end reachable exploit from an ordinary dapp/origin request.

### Recommendation
Call `assertMatchingDomain(cookie.domain, hostnameOf(url))` inside `CookieJar.set()` for both the string and object code paths (parsing the string with `deserialize()` first if needed), and/or invoke it inside `deserialize()` when an origin is known, so any consumer of these APIs is protected without needing to remember to call `assertMatchingDomain` manually.

### Proof of Concept
```ts
// modules/networking-mobile/src/cookie/cookie-jar.spec.ts (add)
import CookieJar from './cookie-jar'
import deserialize from '@exodus/networking-common/cookie/deserialize'

it('should reject a cookie whose Domain does not match the target origin', async () => {
  const jar = new CookieJar('ios', mockStore)
  const malicious = deserialize('sid=abc; Domain=attacker.evil')

  await expect(jar.set(malicious, 'https://legitimate-wallet-api.com')).rejects.toThrow(
    /third party origin|subdomain/
  )
})
```
Expected (current, failing) behavior: `set()` resolves successfully and `mockStore.set` is called with `domain: 'attacker.evil'`, proving `assertMatchingDomain` was never invoked.

### Citations

**File:** modules/networking-common/src/cookie/deserialize.ts (L58-81)
```typescript
export default function deserialize(cookieString: string): Cookie {
  const [nameValue, ...rest] = cookieString.split('; ')

  assertDefined(nameValue, `Malformed cookie string: ${cookieString}`)

  const { name, value } = deserializeNameAndValue(nameValue)

  const cookie: Record<string, CookieValue> = { name, value }

  rest.forEach((property) => {
    const [key, value] = property.split('=')

    assertDefined(key, `Malformed cookie string: Encountered property without key.`)

    const factory = FACTORIES.get(key)
    if (factory) {
      cookie[factory.key] = factory.getInstance(value)
      return
    }

    cookie[toFirstLower(key)] = value
  })

  return cookie as Cookie
```

**File:** modules/networking-common/src/cookie/validators.ts (L29-48)
```typescript
function assertMatchingDomain(domain: string | undefined, originDomain: string) {
  if (domain === undefined) return

  // Domain matching: https://datatracker.ietf.org/doc/html/rfc6265#section-5.1.3
  if (domain === originDomain) return

  if (isSubdomain(domain, originDomain)) {
    throw new Error(
      `Cannot set a cookie for a subdomain. Tried to set ${domain} with origin ${originDomain}`
    )
  }

  if (isSubdomain(originDomain, domain)) {
    return
  }

  throw new Error(
    `Cannot set a cookie for a third party origin. Tried to set ${domain} with origin ${originDomain}`
  )
}
```

**File:** modules/networking-common/src/cookie/validators.spec.ts (L1-1)
```typescript
import { assertMatchingDomain } from './validators'
```

**File:** modules/networking-mobile/src/cookie/cookie-jar.ts (L85-98)
```typescript
  async set(cookie: string | Cookie, url?: string): Promise<void> {
    if (!url) {
      throw new Error('Host is required')
    }

    if (typeof cookie === 'string') {
      await this.store.setFromResponse(url, cookie)
      return
    }

    validate(cookie)

    await this.store.set(url, asNativeCookie(cookie), true)
  }
```
