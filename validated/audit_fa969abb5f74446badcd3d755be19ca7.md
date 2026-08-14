Based on my investigation, I confirmed the described path is real: no cryptographic re-derivation ever happens on the read side.

### Title
Fusion sync channel can poison an already-`synced` address-cache entry with an unverified address, which `AddressProvider#getAddress` then trusts without re-derivation - ([File: features/address-provider/module/address-cache/utils.js])

### Summary
`diffCaches` in `features/address-provider/module/address-cache/utils.js` only protects a *not-yet-synced* local entry from being clobbered by a mismatching `fromSync` push; it does not protect an already-`synced: true` entry from being overwritten by a mismatching `fromSync` push. Since `AddressCache#get()` never re-derives or validates a stored address against the wallet's public key, and `AddressProvider#getAddress` defaults `useCache: true` and returns the cached value verbatim, a forged/corrupted fusion batch can permanently replace a legitimately-derived address for an existing `walletAccount/path` key.

### Finding Description
`diffCaches` computes, for each incoming `(walletAccount, path)` entry: [1](#0-0) 
Only the branch `fromSync && addressMismatch && !existing?.synced` preserves the local value; this guards the race where a value we scheduled to push up (`synced:false`) conflicts with a stale sync-down. If `existing.synced === true` (i.e. the entry was previously derived and confirmed), that guard is bypassed, and the `else if (newAddress || addressMismatch || justSynced)` branch unconditionally accepts the incoming `fromSync` value as authoritative, setting `isDifferent = true` and writing the attacker-supplied address into the diff.

The call path is: `fusion.channel({processBatch})` receives an external batch, wraps every value with `synced: true` and calls `#update({caches}, {fromSync:true})`: [2](#0-1) 
`#update` calls `diffCaches`, and if `isDifferent`, persists the result directly to the atom and to disk with no additional check: [3](#0-2) 
No component ever re-derives the address from the wallet's public key to confirm the cached value is authentic — `AddressCache#get` is a pure storage read: [4](#0-3) . And the consumer, `AddressProvider#getAddress`, defaults to `useCache = true` and returns the cached address immediately, skipping derivation entirely when a cache hit exists: [5](#0-4) 

The only place a mismatch is ever flagged/self-healed is inside `AddressCache#set()`, which is only invoked when the address is freshly re-derived (i.e., when `useCache:false` or on first derivation) — not on every read: [6](#0-5) 
Once a poisoned entry lands with `synced: true`, ordinary `getAddress({ useCache: true })` calls will never trigger re-derivation/mismatch-detection again, so the incorrect address persists indefinitely.

### Impact Explanation
If the fusion sync channel is compromised, corrupted, or MITM'd (network/remote response), an attacker can overwrite the wallet's cached receive/change address for an existing, previously-verified `walletAccount/path` entry with an arbitrary address they control. Because `getAddress()` trusts the cache by default, the wallet UI/downstream logic (e.g., "your receive address") can be silently redirected to the attacker's address, resulting in the user depositing funds to an address they do not control — a direct fund-loss / wallet-integrity impact, not merely a display glitch.

### Likelihood Explanation
Exploitability depends on the attacker being able to inject/modify a fusion channel batch for a given wallet, which the audit scope explicitly grants as a precondition. Given that, the exploit path requires no further interaction: the malicious batch is processed automatically as soon as it arrives, and the corrupted, `synced:true` state persists silently (no user or app-level warning, unlike the local `set()`-mismatch path which does log/track mismatches).

### Recommendation
In `diffCaches`, do not trust `fromSync` address changes for existing entries purely based on their `synced` flag; any `addressMismatch` for an existing `walletAccount/path` (synced or not) should require independent re-derivation/verification against the wallet's derived public key before being accepted, or at minimum should be routed through the same mismatch-detection/quarantine mechanism used by `AddressCache#set()` (i.e., record in `mismatches` and keep the previously-derived address authoritative) rather than blindly overwriting the cache.

### Proof of Concept
Integration test extending `features/address-provider/module/address-cache/__tests__/module.test.js`:
1. Load `addressCache`, derive/set a legitimate address for `exodus_0`/`btcFirstPath` via `.set()`, then simulate a fusion round-trip (`simulateFusionProcessBatch`) with the same address so the entry becomes `synced: true`.
2. Simulate a second, forged `simulateFusionProcessBatch` call for the same `walletAccount/path` key but with a different ("attacker") address.
3. Assert `addressCacheAtom.get()` still returns the original, legitimately-derived address for that path (expected/fixed behavior) — currently it will return the attacker's address, proving `diffCaches` accepted unverified sync data over an already-trusted entry.
4. Additionally call `addressProvider.getAddress({..., useCache: true})` for that path and assert it returns the legitimately-derived address, not the poisoned one, demonstrating the downstream signing/receive-address impact.

### Citations

**File:** features/address-provider/module/address-cache/utils.js (L106-121)
```javascript
    for (const path in subCache) {
      const existing = get(cache1, [walletAccount, path])
      const incoming = subCache[path]
      const newAddress = !existing
      const addressMismatch = !newAddress && existing.address !== incoming.address
      needsSync = needsSync || existing?.synced === false
      const justSynced = !existing?.synced && incoming.synced
      if (fromSync && addressMismatch && !existing?.synced) {
        // We have an address scheduled to sync up, that is mismatching with a
        // sync down, in this case we actually prefer the one scheduled to sync up.
        set(result, [walletAccount, path], existing)
      } else if (newAddress || addressMismatch || justSynced) {
        isDifferent = true
        set(result, [walletAccount, path], incoming)
      }
    }
```

**File:** features/address-provider/module/address-cache/index.js (L57-70)
```javascript
    const { isDifferent, needsSync, diff } = diffCaches(
      preState.caches,
      addressCacheChanges.caches,
      fromSync
    )
    if (isDifferent) {
      const postState = merge(Object.create(null), preState, {
        ...addressCacheChanges,
        caches: diff, // diffCaches can modify the cache
      })

      await this.#addressCacheAtom.set(postState)
      await this.#writeToDisk?.(postState)
    }
```

**File:** features/address-provider/module/address-cache/index.js (L138-156)
```javascript
      processBatch: async (batch) => {
        batch = batch.map(({ data }) => data)
        // each item:
        // {
        //   [walletAccount]: {
        //     [path]: address
        //   }
        // }

        const data = merge(...batch)
        const withSyncedFlag = mapValues(data, (cache, walletAccount) =>
          mapValues(cache, (address, path) => ({
            address,
            synced: true,
          }))
        )

        await this.#update({ caches: withSyncedFlag }, { fromSync: true })
      },
```

**File:** features/address-provider/module/address-cache/index.js (L222-240)
```javascript
  get = async ({ baseAssetName, walletAccountName, derivationPath, multisigDataIndex }) => {
    assert(typeof walletAccountName === 'string', 'expected string "walletAccountName"')
    assert(typeof derivationPath === 'string', 'expected string "derivationPath"')
    assert(typeof baseAssetName === 'string', 'expected string "baseAssetName"')
    assert(
      multisigDataIndex === undefined || typeof multisigDataIndex === 'number',
      'expected number "multisigDataIndex"'
    )
    const addressCache = await this.#addressCacheAtom.get()

    const path = getCachePath({
      baseAssetName,
      walletAccountName,
      derivationPath,
      multisigDataIndex,
    })

    return get(addressCache, ['caches', ...path])
  }
```

**File:** features/address-provider/module/address-cache/index.js (L266-299)
```javascript
    })

    const currentValue = await this.get({
      baseAssetName,
      walletAccountName,
      derivationPath,
    })

    const addressCacheChanges = Object.create(null)

    if (currentValue && currentValue.address) {
      const mismatch = currentValue.address.toString() !== address.toString()
      if (!mismatch) return

      this.#logger.info(
        'addressCache miss match!',
        baseAssetName,
        path,
        currentValue,
        address.toString()
      )

      const derivationPath = path[1]
      set(addressCacheChanges, ['mismatches', derivationPath], {
        cached: currentValue.address.toString(),
        derived: address.toString(),
      })
    }

    set(addressCacheChanges, ['caches', ...path], {
      ...currentValue,
      synced: false,
      address,
    })
```

**File:** features/address-provider/module/address-provider.js (L73-128)
```javascript
      useCache = true,
    } = opts
    const walletAccountName = walletAccount.toString()
    await this.#assertAssetSourceIsSupported({ walletAccount: walletAccountName, assetName })

    if (purpose) {
      const supportedPurposes = await this.#assetSources.getSupportedPurposes({
        walletAccount: walletAccountName,
        assetName,
      })

      assert(
        supportedPurposes.includes(purpose),
        `purpose "${purpose}" is not supported for asset "${assetName}" in wallet "${walletAccount}"`
      )
    }

    const asset = this.#getAsset(assetName)

    const { baseAsset } = asset

    const keyIdArgs = baseAsset.api.getKeyIdentifier({
      purpose,
      accountIndex: walletAccount.index,
      chainIndex,
      addressIndex,
      compatibilityMode: walletAccount.compatibilityMode,
    })

    const keyIdentifier = new KeyIdentifier(keyIdArgs)
    const canUseCache = !asset.api.features?.abstractAccounts
    const cached =
      canUseCache && useCache
        ? await this.#addressCache.get({
            walletAccountName,
            baseAssetName: asset.baseAsset.name,
            derivationPath: keyIdentifier.derivationPath,
            multisigDataIndex,
          })
        : undefined

    const { purpose: derivedPurpose } = parseDerivationPath(keyIdentifier.derivationPath)

    if (cached) {
      const path = createPath({ chainIndex, addressIndex })
      return Address.fromJSON({
        meta: {
          path,
          purpose: derivedPurpose,
          keyIdentifier,
          walletAccount: walletAccountName,
          ...(Number.isInteger(multisigDataIndex) ? { multisigDataIndex } : Object.create(null)),
        },
        ...cached,
      })
    }
```
