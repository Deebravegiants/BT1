### Title
`CookieJar.set` persists attacker-controlled `Domain`/`Path` cookie attributes without validating them against the requesting `url`, enabling cross-origin cookie leakage - ([File: modules/networking-mobile/src/cookie/cookie-jar.ts])

### Summary
`CookieJar.set` in `modules/networking-mobile/src/cookie/cookie-jar.ts` accepts either a raw Set-Cookie string or a `Cookie` object and persists it via the native cookie store, but never calls the existing `assertMatchingDomain` validator from `modules/networking-common/src/cookie/validators.ts` to check the cookie's own `domain`/`path` attributes against the requesting `url`. This means a cookie whose `Domain` attribute (parsed from an untrusted response) is broader than, or unrelated to, the requesting host can be persisted and later replayed to other hosts, including in `FormDataLike`-carrying requests made via `HttpClient`.

### Finding Description
The `set()` method has two code paths:
- String path: `await this.store.setFromResponse(url, cookie)` — the raw Set-Cookie string is handed directly to the native cookie manager with **no validation at all**, not even the local `validate(cookie)` name/value check. [1](#0-0) 
- Object path: only `validate(cookie)` is called, which checks `name`/`value` character sets, and never checks `domain`/`path`: [2](#0-1) [3](#0-2) 

Critically, `assertMatchingDomain(domain, originDomain)` — a function that exists precisely to reject a cookie whose `domain` doesn't match the request's origin (throwing for third-party or subdomain-mismatch cases) — is defined and unit-tested in `modules/networking-common/src/cookie/validators.ts` but is **never invoked** anywhere in `cookie-jar.ts` or elsewhere in the codebase; it is dead code. [4](#0-3) 

`deserialize()` will happily parse a `Domain=` attribute out of an attacker-supplied Set-Cookie string into the resulting `Cookie.domain` field via the generic `toFirstLower(key)` fallback, since there is no dedicated factory entry excluding/validating `Domain`. [5](#0-4) 

For the object-based `set()` path in particular, since `validate()` is the only guard and it doesn't check `domain`/`path` against `url`, a caller (or code processing a parsed Set-Cookie-like object from an untrusted API response) can construct a `Cookie` with an overly broad `domain` and have it accepted and stored, keyed only by the native store's own internal domain-matching rules — not by this library's logic. The library-level scoping invariant described in `CookieJarSpec.set`'s JSDoc ("Sets a cookie" for `url`) is not actually enforced in code. [6](#0-5) 

### Impact Explanation
If domain/path scoping is not enforced at this layer, a cookie obtained/derived from one origin's response could be persisted with a `domain` attribute broader than intended (e.g., a bare parent domain instead of the specific subdomain that issued it). Later `HttpClient` fetches — including ones carrying `FormDataLike` bodies — to other same-suffix hosts could pick up and transmit that cookie, potentially leaking session/auth-scoped cookie values to hosts that should not receive them. This matches an auth/session token scoping violation.

### Likelihood Explanation
Exploitability is bounded by two factors I could not fully verify from the available code:
1. On mobile, `set()` delegates to the native `@react-native-cookies/cookies` `CookieManager`, whose underlying OS cookie store (WKWebView/CookieManager on iOS, Android system CookieManager) may itself enforce RFC6265 domain-matching independent of this library's own checks — reducing real-world exploitability of the string path, but this is delegated trust, not an in-repo guard.
2. For the **object-based** `set(cookie: Cookie, url)` path, there is no equivalent delegated protection guarantee documented in this repo, and the in-repo `assertMatchingDomain` guard that was clearly built for this purpose is simply not wired in, which is the concrete, verifiable defect. Any code in the codebase that constructs a `Cookie` object from parsed/untrusted data (e.g. via `deserialize()`) and passes it to `set()` bypasses domain scoping entirely at the library level.

I could not locate a web/browser CookieJar implementation or the `HttpClient`/form-request call sites that consume cookies from the jar in this index, so I cannot fully confirm the "later sent unscoped in FormDataLike-carrying requests" leg of the chain beyond the `FormDataLike` type definition itself; this should be verified with a full checkout.

### Recommendation
Call `assertMatchingDomain(cookie.domain, new URL(url).hostname)` (and an equivalent path check) inside `CookieJar.set()` for both the string-deserialized cookie and the object-based cookie, before delegating to `this.store.set`/`this.store.setFromResponse`, so that the existing, already-implemented and tested validator is actually enforced at the point where cookies are persisted.

### Proof of Concept
```ts
// modules/networking-mobile/src/cookie/cookie-jar.spec.ts (add case)
import { CookieJar } from './index'
import { OperatingSystem } from '../shared/types'

it('should reject a cookie whose Domain is broader/mismatched vs the requesting url', async () => {
  const jar = new CookieJar(OperatingSystem.iOS)

  await expect(
    jar.set(
      { name: 'session', value: 'secret', domain: 'evil.com' },
      'https://api.example.com/login'
    )
  ).rejects.toThrow(/third party origin|subdomain/)
})
```
Expected: currently this test **fails** (no throw) because `validate()` does not call `assertMatchingDomain`, demonstrating the missing scoping check.

### Citations

**File:** modules/networking-mobile/src/cookie/cookie-jar.ts (L90-93)
```typescript
    if (typeof cookie === 'string') {
      await this.store.setFromResponse(url, cookie)
      return
    }
```

**File:** modules/networking-mobile/src/cookie/cookie-jar.ts (L95-97)
```typescript
    validate(cookie)

    await this.store.set(url, asNativeCookie(cookie), true)
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

**File:** modules/networking-common/src/cookie/validators.ts (L69-72)
```typescript
function validate(cookie: BaseCookie) {
  validateName(cookie.name)
  validateValue(cookie.value)
}
```

**File:** modules/networking-common/src/cookie/deserialize.ts (L67-79)
```typescript
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
```

**File:** modules/networking-common/src/cookie/types.ts (L41-49)
```typescript
  /**
   * Sets a cookie
   * @param cookie string from Set-Cookie header or Cookie object
   * @param url Not available in RestrictedAccess implementations of the CookieJar
   */
  set(
    cookie: string | Cookie,
    url: RestrictedAccess extends true ? undefined : string
  ): Promise<void>
```
