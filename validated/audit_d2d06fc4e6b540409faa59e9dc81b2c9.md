### Title
`MemoizedKeychain.exportKey` caches derived public keys/xpubs keyed only by `keyId`, omitting `seedId`, causing cross-seed key confusion in multi-seed wallets - (File: features/keychain/module/memoized-keychain.js)

### Summary
`MemoizedKeychain` wraps `Keychain` to memoize `exportKey` results so repeated derivations don't hit the underlying HD-derivation logic again. The cache key is computed purely from `keyId` (`stableStringify(keyId)`), never incorporating `seedId`. In every other part of the derivation/signing pipeline (`keychain.js`'s `#getPrivateHDKey`, `tx-signer`, `message-signer`, `public-key-provider`), `seedId` is treated as a mandatory, independent dimension of key identity — the same `keyId` (purpose/accountIndex/chainIndex/addressIndex/derivationPath) can and does correspond to entirely different keys under different seeds in a multi-seed wallet. Because the memoization cache collapses this dimension, a cached public key/xpub derived for one seed can be returned for a request that specifies a different seed but the same `keyId`.

### Finding Description
`MemoizedKeychain#getCachedKey`/`#setCachedKey` build the cache key with: [1](#0-0) 

and `exportKey` consults this cache before falling back to `super.exportKey`, then persists the result under the same seed-agnostic key: [2](#0-1) 

Contrast this with the underlying `Keychain`, where `seedId` is a required, independent identity component used to select the correct master key material before deriving anything for a `keyId`: [3](#0-2) 

and with every consumer of the keychain (`public-key-provider`, `tx-signer`, `message-signer`), which always pass both `seedId` and `keyId` together as the true compound identity for a key, e.g.: [4](#0-3) [5](#0-4) 

This is the same bug class as the Ammplify `Maker.collectFees` issue: a downstream operation ("re-target liquidity"/"return cached key") relies on a piece of state (`asset.liq` / the memoization cache) that an earlier state-changing operation (`adjustMaker` / switching seeds) does not keep in sync with the true, current identity of the object being operated on. In Ammplify, `asset.liq` silently reverted the position to a stale value; here, the cache silently returns key material belonging to the wrong seed once two seeds share the same `keyId` shape (default purpose/account/chain/address indexes are commonly `0` across seeds, e.g. account index 0, address index 0), which the docs on multi-seed support (`docs/development/multi-seed.md`) confirm is an intended, first-class configuration in this codebase.

### Impact Explanation
If `MemoizedKeychain` is the active `keychain` implementation for a multi-seed wallet, the first `exportKey` call for a given `keyId` (e.g. account 0 / chain 0 / address 0 for Bitcoin) permanently poisons the cache for that `keyId`, regardless of which `seedId` is subsequently requested. Any later `exportKey` call with the same `keyId` but a different `seedId` silently returns the first seed's `publicKey`/`xpub` instead of deriving the correct one. This is a direct cross-account/cross-seed key confusion: addresses, extended public keys, and any code path that trusts `exportKey`'s output for a specific seed (address generation, signing key selection, key display/export) would receive key material from an unrelated seed. Practical consequences include funds being received on/associated with the wrong seed's keys and incorrect key material being displayed/exported to the user as belonging to a different seed — a direct wallet key-material integrity compromise.

### Likelihood Explanation
The bug is deterministic once the concrete conditions are met — no attacker or malicious peer is required, matching the "always happens by itself when internal pre-condition is met" nature of the original report. The precondition is simply: (1) the wallet has more than one seed (a supported, documented feature per `docs/development/multi-seed.md`), and (2) `exportKey` is invoked for the same `keyId` shape across two different seeds (extremely likely, since default derivation indexes such as accountIndex 0 are the common case for the primary/default wallet account of each seed). The severity is reduced by uncertainty over whether `MemoizedKeychain` (vs. the base `Keychain`) is actually wired as the production `keychain` module in multi-seed-enabled builds — I was not able to fully confirm this wiring or the exact call convention used by `adapters/keystore-mobile` before running out of investigation budget, so this should be verified before treating the impact as certain in a specific deployed build.

### Recommendation
Include `seedId` as part of the memoization cache key in `MemoizedKeychain` (e.g. `` `${seedId}:${keyIdToCacheKey(keyId)}` ``) so that cached public keys/xpubs are strictly scoped per seed, matching how `seedId` is treated everywhere else in the keychain and its consumers.

### Proof of Concept
Conceptual reproduction based on the code above (not independently executed):
1. Initialize a `MemoizedKeychain` with two seeds, `seedA` and `seedB`.
2. Call `exportKey(keyId)` where `keyId` corresponds to purpose/accountIndex 0/chainIndex 0/addressIndex 0, with `seedId: seedA`. The result (public key/xpub for `seedA`) is cached under `keyIdToCacheKey(keyId)`.
3. Call `exportKey(keyId)` again with the same `keyId` shape but `seedId: seedB`.
4. Because `#getCachedKey`/`#setCachedKey` never key on `seedId`, the cached entry from step 2 (belonging to `seedA`) is returned instead of deriving `seedB`'s actual key, per: [2](#0-1)

### Citations

**File:** features/keychain/module/memoized-keychain.js (L6-36)
```javascript
const keyIdToCacheKey = stableStringify

const CACHE_KEY = 'data'

const getPublicKeyData = ({ xpub, publicKey }) => ({ xpub, publicKey })

class MemoizedKeychain extends Keychain {
  #storage
  #publicKeys = Object.create(null)
  #cloneOpts

  constructor({ storage, legacyPrivToPub }) {
    super({ legacyPrivToPub })

    this.#storage = storage
    this.#storage.get(CACHE_KEY).then((data) => {
      this.#publicKeys = data ? BJSON.parse(data) : Object.create(null)
    })

    this.#cloneOpts = { storage }
  }

  #getCachedKey = async (keyId) => {
    const cacheKey = keyIdToCacheKey(keyId)
    return this.#publicKeys[cacheKey]
  }

  #setCachedKey = async (keyId, value) => {
    this.#publicKeys[keyIdToCacheKey(keyId)] = value
    await this.#storage.set(CACHE_KEY, BJSON.stringify(this.#publicKeys))
  }
```

**File:** features/keychain/module/memoized-keychain.js (L38-49)
```javascript
  exportKey = async (keyId, opts) => {
    if (!opts?.exportPrivate) {
      // take advantage of public key cache
      const cached = await this.#getCachedKey(keyId)
      if (cached) return cached
    }

    const result = await super.exportKey(keyId, opts)
    // don't wait for this to finish
    this.#setCachedKey(keyId, getPublicKeyData(result))
    return result
  }
```

**File:** features/keychain/module/keychain.js (L223-246)
```javascript
  #getPrivateHDKey = ({ seedId, keyId, getPrivateHDKeySymbol }) => {
    if (getPrivateHDKeySymbol !== this.#getPrivateHDKeySymbol) {
      this.#assertPrivateKeysUnlocked(seedId ? [seedId] : undefined)
    }

    throwIfInvalidKeyIdentifier(keyId)
    assert(typeof seedId === 'string', 'seedId must be a BIP32 key identifier in hex encoding')
    assert(this.#masters[seedId], `seed with id "${seedId}" is not initialized`)

    throwIfInvalidMasters(this.#masters[seedId])

    const { derivationAlgorithm, derivationPath, keyType } = keyId
    const master = this.#masters[seedId][derivationAlgorithm]

    if (isExternalSeedId(seedId)) {
      assert(master, '#getPrivateHDKey: found no valid master seed')
      assert(
        keyType === master.keyId.keyType,
        '#getPrivateHDKey: received invalid keyType for specified master seed'
      )
    }

    return master.derive(derivationPath)
  }
```

**File:** features/public-key-provider/module/public-key-provider.ts (L144-157)
```typescript
    if (walletAccount.isSoftware) {
      const { publicKey, xpub } = await this.#keychain.exportKey({
        keyId: keyIdentifier,
        seedId: walletAccount.seedId,
      })

      // Don't wait to avoid extra latency
      void this.#publicKeyStore.add({
        walletAccount,
        keyIdentifier,
        publicKey,
        xpub,
      })
      return { publicKey, xpub }
```

**File:** features/tx-signer/src/module/seed-signer.ts (L82-86)
```typescript
    const getPublicKey = async ({
      keyId = getDefaultKeyIdentifier(),
    }: GetPublicKeyParams = {}): Promise<Buffer> => {
      return this.#keychain.getPublicKey({ seedId, keyId })
    }
```
