#No
Vulnerability found for this question.

Based on my review of `features/auth-mobile/module/auth.js`, `hasPin()` and `isCorrectPin()` are both stateless, one-shot checks against a PIN secret stored in the keystore [1](#0-0) [2](#0-1) . Neither function creates, caches, or persists any "unlocked" session/scope object that could be reused later or across an account switch — there is no session token, no unlock flag tied to `isCorrectPin`'s result, and nothing in `Auth` that binds to a wallet account at all. The class only tracks `hasPin`/`hasBioAuth`/`hasDeviceAuth`/`shouldAuthenticate` in `authAtom` via `#mergeIntoAtom` [3](#0-2) , which are global flags about whether authentication is configured, not per-account unlocked state.

Separately, wallet seed unlocking (`Wallet#unlock`/`Wallet#lock`) is unrelated to the PIN module and operates on the keychain/seed layer, not per-account [4](#0-3) . Wallet-account switching (`WalletAccounts#setActive`) merely changes which already-derived account is "active" among unlocked seeds and performs no PIN check or unlock operation itself [5](#0-4) .

Since there is no shared "unlocked" state produced by `isCorrectPin`/`hasPin` that could be carried over into a different account's protected operations, and no code path connects PIN verification results to account-switch RPCs, the premise of the question (reuse of a validated PIN-unlock result across an account switch) has no basis in the actual code. This does not meet the bar for a reproducible, file/function-supported exploit.

### Citations

**File:** features/auth-mobile/module/auth.js (L45-45)
```javascript
  hasPin = () => this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY)).then(Boolean)
```

**File:** features/auth-mobile/module/auth.js (L96-113)
```javascript
  #mergeIntoAtom = async (params) => {
    await this.#authAtom.set((current) => {
      const data = {
        ...current,
        ...params,
      }

      const { hasBioAuth, biometry, hasPin, hasDeviceAuth } = data

      data.hasBioAuth = hasBioAuth && !!biometry
      data.shouldAuthenticate = hasDeviceAuth || hasBioAuth || hasPin

      if (isEqual(current, data)) return current

      this.#logger.info('Updated auth data', data)
      return data
    })
  }
```

**File:** features/auth-mobile/module/auth.js (L128-131)
```javascript
  isCorrectPin = async (input) => {
    const pin = await this.#keystore.getSecret(this.#key(AUTH_KEYSTORE_PIN_KEY))
    return !!pin && pin === input
  }
```

**File:** features/wallet/module/wallet.js (L274-298)
```javascript
  isLocked = async () => this.#isLocked

  lock = async () => {
    this.#keychain.removeAllSeeds()

    this.#isLocked = true
  }

  unlock = async ({ passphrase } = {}) => {
    try {
      const { seed } = await this.#getSeed({ passphrase })
      const primarySeedId = await this.#keychain.addSeed(seed)
      this.#primarySeedIdAtom.set(primarySeedId)

      const extraSeeds = await this.#getExtraSeeds()
      await Promise.all(extraSeeds.map(({ seed }) => this.#keychain.addSeed(seed)))

      this.#isLocked = false

      return { primarySeedId }
    } catch (err) {
      this.#logger.debug('unlock() failed: wrong password', err)
      throw new Error('Wrong password. Try again.')
    }
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L542-548)
```typescript
  setActive = async (value: string | ((oldValue: string) => string)) => {
    if (typeof value === 'function') {
      return this.#activeWalletAccountAtom.set(value)
    }

    return this.#activeWalletAccountAtom.set(value)
  }
```
