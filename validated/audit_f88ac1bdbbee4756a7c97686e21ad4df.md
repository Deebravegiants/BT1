## Analysis

The Alchemix bug pattern is: a security-limiting action (Flux minting) is properly rate-limited in one code path (`reset`/`vote`, gated by `onlyNewEpoch`) but reachable through a second, unguarded path (`poke`) that shares the same internal logic (`_vote` → `accrueFlux`), allowing unlimited repeated triggering of a security-sensitive operation.

The closest analog I can find in this repository is `@exodus/auth-mobile`'s PIN verification, which has **no attempt limiting whatsoever** — unlike typical wallet-lock flows that at least fail with generic errors, `isCorrectPin` is a bare, stateless equality check that can be invoked an unbounded number of times. [1](#0-0) 

```js
isCorrectPin = async (input) => {
  const pin = await this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY))
  return !!pin && pin === input
}
```

`setPin` enforces only a length constraint (exactly 6 digits, i.e. up to 10^6 combinations), with no complexity or rate requirements: [2](#0-1) 

The `authAtom`'s `shouldAuthenticate`/`hasPin` flags gate UI access to "protectworthy resources such as the mnemonic phrase," per the feature's own documentation: [3](#0-2) 

`isCorrectPin` is exposed directly on the public SDK API surface (`exodus.auth.isCorrectPin`), reachable from the calling application/UI without any additional gating, cooldown, exponential backoff, or attempt counter: [4](#0-3) 

I searched the module directory and tests for any throttling, attempt-counter, or lockout logic and found none — the only test coverage is a simple correctness check with no rate-limiting assertions: [5](#0-4) 

This satisfies the "unguarded repeated-call" bug class (a security check reachable without limitation, unlike what a similarly-purposed guarded function would enforce) and lands squarely in the permitted "auth" trust boundary, with a concrete unauthorized-access/auth-bypass impact (brute-forcing a 6-digit numeric PIN in at most 1,000,000 local calls to defeat the PIN gate protecting the mnemonic/private key material).

### Title
Unbounded PIN Verification Attempts Enable Local Brute-Force Bypass of Auth Gate - (File: `features/auth-mobile/module/auth.js`)

### Summary
`Auth.isCorrectPin` performs a raw string comparison against the stored 6-digit PIN with no attempt counter, cooldown, exponential backoff, or lockout of any kind. Because `hasPin`/`shouldAuthenticate` is the gate that the host application uses to decide whether to reveal protect-worthy resources (per the feature's own README, e.g. the mnemonic phrase), an attacker with local/session access to the wallet UI/API (e.g. a malicious co-installed app, unattended device, or compromised UI layer) can call `isCorrectPin` up to 10^6 times to recover the PIN and defeat the auth gate.

### Finding Description
`setPin` only validates PIN length (exactly 6 digits) — [2](#0-1)  — giving a maximum keyspace of 1,000,000 combinations. `isCorrectPin` checks the candidate against the stored secret with no state tracking of failed attempts, no delay, and no maximum-attempts enforcement: [1](#0-0) . Unlike a properly hardened credential check (which would track failures and apply increasing delays/lockouts), this function can be invoked in a tight loop indefinitely, as confirmed by both the module implementation and its test suite, which has no coverage for attempt limits: [5](#0-4) . This mirrors the reported bug class where a security-relevant action lacked the rate limiting that a properly-designed sibling function otherwise implied should exist.

### Impact Explanation
Successful brute-forcing of the PIN allows an attacker with local access to the wallet application (but without the correct PIN) to satisfy `shouldAuthenticate`/unlock UI-gated access to sensitive wallet data such as the mnemonic phrase, as documented in the feature's own usage notes: [3](#0-2) . This is a direct auth-bypass path toward private key material exposure, which can lead to full wallet compromise/theft of funds.

### Likelihood Explanation
Likelihood is high for any local attacker able to invoke SDK methods repeatedly (e.g., malicious app with shared device access, automated script driving the UI, or any code with access to the `exodus.auth` API surface documented at [4](#0-3) ). A 6-digit numeric PIN is fully exhausted well within seconds to minutes of unthrottled local calls.

### Recommendation
Add attempt tracking (persisted counter with increasing delay/backoff or hard lockout after N failed attempts) inside `isCorrectPin`, mirroring the protection that PIN-based auth systems are expected to have. Consider also enforcing this at the `keystore`/OS level (e.g., using OS-level rate limiting like `reactNativeKeychain`'s biometric access control) rather than relying solely on the JS-level flag.

### Proof of Concept
```js
// Given a wallet with a 6-digit PIN already set:
for (let i = 0; i <= 999999; i++) {
  const candidate = String(i).padStart(6, '0')
  if (await exodus.auth.isCorrectPin(candidate)) {
    console.log('PIN found:', candidate)
    break
  }
}
// No lockout, delay, or attempt cap is ever triggered — the loop
// runs to completion and recovers the PIN.
```

### Citations

**File:** features/auth-mobile/module/auth.js (L115-126)
```javascript
  setPin = async (value) => {
    value = value.trim()

    if (value.length !== 6) {
      throw new InvalidPasscodeLengthError()
    }

    await this.#keystore.setSecret(this.#key(AUTH_KEYSTORE_PIN_KEY), value)
    await this.#mergeIntoAtom({ hasPin: true })

    await this.#eventLog.record({ event: 'pin_auth_set' })
  }
```

**File:** features/auth-mobile/module/auth.js (L128-131)
```javascript
  isCorrectPin = async (input) => {
    const pin = await this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY))
    return !!pin && pin === input
  }
```

**File:** features/auth-mobile/README.md (L19-27)
```markdown
```js
await exodus.auth.setPin('123456') // set 6 number pin
await exodus.auth.isCorrectPin('645123') // false

await exodus.auth.enableBioAuth() // enables bio authentication such as fingerprint or face id

await exodus.auth.bio.trigger() // start the bio authentication process
await exodus.auth.bio.stop() // abort
```
```

**File:** features/auth-mobile/README.md (L29-36)
```markdown
If you're building a feature that requires access to authentication details, you can depend on `authAtom` and observe changes:

```js
authAtom.observe(({ hasBioAuth, biometry, hasPin, shouldAuthentiate }) => {
  // shouldAuthenticate is true if either a pin was set or bio auth enabled
  // (inidicator for the UI to restrict access to protectworthy resources such as the mnemonic phrase)
  // biometry is available biometry variant
})
```

**File:** features/auth-mobile/module/__tests__/auth.test.js (L196-203)
```javascript
  describe('isCorrectPin', () => {
    test('returns true for correct PIN, false otherwise', async () => {
      expect(await auth.isCorrectPin('123456')).toBe(false)
      await auth.setPin('123456')
      expect(await auth.isCorrectPin('123456')).toBe(true)
      expect(await auth.isCorrectPin('654321')).toBe(false)
    })
  })
```
