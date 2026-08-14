I have sufficient evidence to confirm this finding.

### Title
CookieJar.set() in networking-mobile never validates cookie.domain against the target url, allowing cross-origin cookie injection via `@react-native-cookies` domain override - ([File: modules/networking-mobile/src/cookie/cookie-jar.ts])

### Summary
`CookieJar.set` in `modules/networking-mobile/src/cookie/cookie-jar.ts` only calls `validate(cookie)` (name/value character checks) before forwarding the cookie object to the native `@react-native-cookies` store, but never calls `assertMatchingDomain(cookie.domain, originDomainFromUrl)` even though that helper exists and is exported from `@exodus/networking-common/cookie`. This means any caller invoking `set()` with a `Cookie` object carrying an attacker-chosen `domain` field is not blocked at the JS layer from writing a cookie scoped to a different origin than the `url` argument.

### Finding Description
`CookieJar.set` at [1](#0-0)  takes a `Cookie` object with an optional `domain` field and a `url` argument, calls `validate(cookie)` (which only checks for forbidden characters in `name`/`value`, per `modules/networking-common/src/cookie/validators.ts` lines 69-72), and then directly calls `this.store.set(url, asNativeCookie(cookie), true)`. The `domain` property is passed through unchanged by `asNativeCookie` at [2](#0-1) .

The `assertMatchingDomain` function, defined and tested in `modules/networking-common/src/cookie/validators.ts` lines 29-48 (and its dedicated spec at `modules/networking-common/src/cookie/validators.spec.ts`), is designed specifically to reject a `domain` value that does not match (or is not a legitimate parent of) the origin domain derived from the request URL — throwing `Cannot set a cookie for a third party origin` or `Cannot set a cookie for a subdomain`. It is exported alongside `validate` from `@exodus/networking-common/cookie` (`modules/networking-common/src/cookie/index.ts`), and `CookieJar.set` imports only `validate`, not `assertMatchingDomain` [3](#0-2) . This confirms the guard exists in the codebase but is dead code with respect to the mobile `CookieJar` — it is never invoked at the call site that matters.

However, I could not locate any reachable call site in this codebase where an unprivileged dapp/webview origin can directly invoke `CookieJar.set(cookie, url)` with an attacker-controlled `domain` field and an arbitrary/mismatched `url`. The only in-repo caller of `.set()` besides tests is `os/android.ts`'s `clearByName`, which calls `this.set({ name, value: '' }, host)` with no `domain` field at all [4](#0-3) . No web3-browser/dapp-webview bridge code exposing this `CookieJar.set` API to postMessage/RPC input was found in this repository's indexed contents.

### Impact Explanation
If a privileged internal caller (e.g. a future web3-browser bridge) ever calls `CookieJar.set` with a `url` derived from the current dapp origin but a `cookie.domain` value taken from unsanitized dapp-supplied input (e.g. from a `Set-Cookie`-like structured message rather than a raw string, or a custom header parser), the missing `assertMatchingDomain` check means the JS layer would not stop a cross-origin `domain` value from reaching the native cookie store. Depending on native `@react-native-cookies`/WebKit/CookieManager enforcement (which is platform code outside this repo and not verifiable here), this could allow a dapp to set state that is later read as another origin's cookie, potentially affecting session-based auto-approval flows tied to cookies for that other origin. However, this repository does not contain the RPC/bridge code that would grant a dapp origin control over `cookie.domain` and cause `set()` to be called with a mismatched `url`, so the concrete unauthorized-signing/session-hijack chain described in the prompt is not demonstrated in-repo.

### Likelihood Explanation
Low, as currently used within this repository. The only caller (`clearByName`) never supplies a `domain` field, and no dapp-facing bridge that maps untrusted webview `postMessage`/`fetch`-triggered input into `CookieJar.set()` calls with a `Cookie.domain` field is present in the indexed code. The missing guard is a real gap relative to the `assertMatchingDomain` helper's intended purpose, but exploitability depends entirely on a caller (not found here) that forwards attacker-controlled `domain` values.

### Recommendation
Call `assertMatchingDomain(cookie.domain, new URL(url).hostname)` inside `CookieJar.set` immediately after `validate(cookie)` and before forwarding to `this.store.set`, mirroring the exported-but-unused helper's intent, so that any current or future caller is protected regardless of how `Cookie.domain` is populated.

### Proof of Concept
```ts
// modules/networking-mobile/src/cookie/cookie-jar.spec.ts (extension)
import { CookieJar } from './index'
import { OperatingSystem } from '../shared/types'

it('should reject cookie.domain that does not match the target url origin', async () => {
  const jar = new CookieJar(OperatingSystem.iOS)
  await expect(
    jar.set({ name: 'session', value: 'forged', domain: 'victim.com' }, 'https://attacker.com')
  ).rejects.toThrow(/third party origin/)
})
```
Expected current behavior: the promise resolves (native mock `store.set` is called with `domain: 'victim.com'` and `url: 'https://attacker.com'`), confirming no domain-matching guard is enforced — demonstrating the gap, though not a full exploit chain absent a concrete untrusted caller in this repo. [1](#0-0) [5](#0-4)

### Citations

**File:** modules/networking-mobile/src/cookie/cookie-jar.ts (L1-8)
```typescript
import {
  Cookie,
  CookieJar as CookieJarSpec,
  GetAllOptions,
  GetOptions,
  RemoveOptions,
  validate,
} from '@exodus/networking-common/cookie'
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

**File:** modules/networking-mobile/src/cookie/cookie-jar.ts (L110-116)
```typescript
function asNativeCookie({ expires, value, ...rest }: Cookie): NativeCookie {
  return {
    ...rest,
    value: value ?? '',
    expires: expires?.toUTCString(),
  }
}
```

**File:** modules/networking-mobile/src/cookie/os/android.ts (L1-15)
```typescript
import { CookieJar } from '../index'

export function clearByName(this: CookieJar, host: string, name: string): Promise<unknown> {
  /* Android does not support removing a cookie by name, we have to keep an
   * eye on this and see if this has any unexpected consequences.
   * An alternative implementation could be to get all cookies, remove them
   * from the cookie store and write only the ones back that don't match "name" */
  return this.set(
    {
      name,
      value: '',
    },
    host
  )
}
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
