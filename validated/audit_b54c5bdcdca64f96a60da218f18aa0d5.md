### Title
Connected-origins account cache serves stale wallet-account addresses to dApps instead of querying the authoritative address provider - ([File: features/connected-origins/module/connections.js])

### Summary
The Sherlock report describes a Solidity `Controller` that sends treasury funds to an immutable, self-cached `treasury` address instead of querying the vault's authoritative, updatable `treasury` value — so callers act on a stale copy of a security-relevant address rather than the current source of truth. The analogous pattern in `hydra` is in the `connected-origins` feature: `ConnectedOrigins#getWalletAccountAddresses` returns an address cached on `connectedAccountsAtom` instead of always re-deriving it from the authoritative `addressProvider`, and this cached value is what gets exposed to connected dApps via `getConnectedAccounts`. [1](#0-0) 

### Finding Description
`#getWalletAccountAddresses` first checks for an `existingAddress` on the `connectedAccountsAtom` cache and returns it verbatim, only falling back to `addressProvider.getDefaultAddress` when no cached entry exists: [1](#0-0) 

This cache is written once per wallet account/asset when an origin is first added (`add` → `#setData` → `#getAccounts` → `#getWalletAccountAddresses`), and is only refreshed wholesale in `updateConnectedAccounts`, and even then only when the *set* of enabled wallet accounts changes (`xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))`), not when an individual account's derived address changes: [2](#0-1) 

Meanwhile, the codebase's own `address-provider`/`address-cache` module explicitly documents and tests the scenario where a previously cached address can be wrong and later needs to be corrected/resynced (a "mismatch" flow, e.g. after re-derivation detects the previously stored address was incorrect): [3](#0-2) [4](#0-3) 

Because `ConnectedOrigins` treats its own `connectedAccountsAtom` snapshot as authoritative rather than re-querying `addressProvider` (the actual source of truth, which itself reconciles mismatches), a stale/incorrect address that predates a mismatch correction — or any address computed under previously incorrect derivation parameters — remains permanently cached and is what gets served to connected origins via `getConnectedAccounts`: [5](#0-4) 

This mirrors the Y2K bug class exactly: a downstream consumer (`Controller`/`ConnectedOrigins`) holds its own cached copy of a value that has an authoritative, updatable source of truth (`Vault.treasury()`/`addressProvider`), and never re-reads from that source, so updates/corrections never propagate to where the value is actually used.

### Impact Explanation
`getConnectedAccounts` is the function that answers "which addresses does this wallet account own" to a connected/trusted origin (the dApp-facing account list, analogous to `eth_accounts`) and is explicitly documented to work "while the wallet is locked," i.e., it is a primary account-disclosure surface across the origin trust boundary. If the cached address is stale/incorrect relative to what the address provider (and thus the actual receive/signing flow) currently derives, a dApp is told about an address that:
- may not correspond to the address a counterparty would actually be shown/asked to pay in the live receive flow, or
- may differ from what other wallet subsystems (fee calculation, receive screen, signing input) treat as canonical,

creating a cross-boundary state-consistency break between what is disclosed to origins and the wallet's authoritative address state. This is a direct analog of "funds always go to the wrong/stale destination because the consumer never re-reads the current value," which was the crux of the M-3 finding's impact.

### Likelihood Explanation
The condition requires the underlying derivation/address-provider value for an already-cached wallet account/asset pair to change after the origin connection was first established (the exact "mismatch" scenario the `address-cache` module is built to detect and correct). Given the codebase maintains dedicated mismatch-detection/correction logic for addresses, such staleness is an anticipated, not merely theoretical, occurrence — but it is not attacker-triggerable on demand, only reachable when a legitimate address recalculation/correction occurs after a dApp has already been connected.

### Recommendation
`#getWalletAccountAddresses` (and by extension `getConnectedAccounts`) should always resolve addresses from `addressProvider.getDefaultAddress` (the authoritative source, which itself performs mismatch detection/reconciliation) rather than preferring the `connectedAccountsAtom` cache, or the cache must be invalidated/refreshed whenever the address provider corrects a mismatch for that wallet account/asset — mirroring the recommended fix of always querying the vault's live `treasury()` value instead of a locally cached copy.

### Proof of Concept
Not applicable as a standalone exploit — this is a state-consistency defect, not a remotely triggerable exploit chain. It can be demonstrated by: (1) connecting an origin so `connectedAccountsAtom` caches address `A` for `exodus_0`/`ethereum`; (2) causing the address-provider/address-cache to detect and correct a mismatch for that same wallet account/asset to address `B` (as exercised by the existing test at `features/address-provider/module/address-cache/__tests__/module.test.js:433-490`); (3) calling `connectedOrigins.getConnectedAccounts({ origin })` and observing it still returns the stale address `A` instead of the corrected `B`, because `connections.js:123-138` never re-queries `addressProvider` once a cache entry exists. [1](#0-0)

### Citations

**File:** features/connected-origins/module/connections.js (L123-138)
```javascript
  #getWalletAccountAddresses = async (walletAccount, assetNames) => {
    const connectedAccounts = await this.#connectedAccountsAtom.get()
    const entries = await Promise.all(
      assetNames.map(async (assetName) => {
        const existingAddress = connectedAccounts[walletAccount]?.addresses[assetName]
        if (existingAddress) {
          return [assetName, existingAddress]
        }

        const address = await this.#addressProvider.getDefaultAddress({ assetName, walletAccount })
        return [assetName, address.toString()]
      })
    )

    return Object.fromEntries(entries)
  }
```

**File:** features/connected-origins/module/connections.js (L249-273)
```javascript
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

    const value = await this.#getOrigin({ origin })
    const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(
      (name, index, ary) => Boolean(name) && ary.indexOf(name) === index
    )

    const activeWalletAccount = await this.#activeWalletAccountAtom.get()
    const accounts = await this.#connectedAccountsAtom.get()

    const connectedAccounts = []
    for (const name of Object.keys(accounts)) {
      if (name === activeWalletAccount) continue
      connectedAccounts.push({ name, addresses: pick(accounts[name].addresses, assetNames) })
    }

    connectedAccounts.unshift({
      name: activeWalletAccount,
      addresses: pick(accounts[activeWalletAccount].addresses, assetNames),
    })

    return connectedAccounts
  }
```

**File:** features/connected-origins/module/connections.js (L299-314)
```javascript
  updateConnectedAccounts = async () => {
    const walletAccounts = await this.#enabledWalletAccountsAtom.get()
    const connectedAccounts = await this.#connectedAccountsAtom.get()

    const difference = xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))
    if (difference.length === 0) {
      // up-to-date
      return
    }

    const connectedOrigins = await this.#connectedOriginsAtom.get()
    const assetNames = this.#getConnectedAssets(connectedOrigins)
    const updatedAccounts = await this.#getAccounts(assetNames)

    await this.#connectedAccountsAtom.set(updatedAccounts)
  }
```

**File:** features/address-provider/module/address-cache/__tests__/module.test.js (L433-490)
```javascript
  it('supports sync down when a mismatch was detected scheduled to sync up', async () => {
    /**
     * 1. visit receive address screen -> re-derives the address
     * 2. we notice there is a mismatch & want to re-sync the address to fusion -> set synced to false
     * 3. fusion syncs down & clobbers the synced flag -> leaving us with the incorrect address in fusion & we never push up the correct address
     */
    await addressCache.load()
    jest.useFakeTimers()

    // Setup the address cache with a mismatch
    await expect(
      simulateFusionProcessBatch([
        { data: { exodus_0: { [btcFirstPathWithAsset]: 'incorrect address' } } },
      ])
    ).resolves.toBe(undefined)

    // Verify the address cache is wrong before starting
    expect(await addressCacheAtom.get()).toEqual({
      caches: {
        exodus_0: {
          [btcFirstPathWithAsset]: {
            synced: true,
            address: 'incorrect address',
          },
        },
        exodus_1: {},
      },
      mismatches: {},
    })

    // we notice there is a mismatch & want to re-sync the address to fusion -> set synced to false
    await addressCache.set({
      walletAccountName: 'exodus_0',
      baseAssetName: 'bitcoin',
      derivationPath: btcFirstPath,
      address: 'correct address',
    })

    // Verify the address cache has properly detected the mismatch
    // and is ready to push the correct address to fusion
    expect(await addressCacheAtom.get()).toEqual({
      caches: {
        exodus_0: {
          [btcFirstPathWithAsset]: {
            synced: false,
            address: 'correct address',
          },
        },
        exodus_1: {},
      },
      mismatches: {
        [btcFirstPathWithAsset]: {
          cached: 'incorrect address',
          derived: 'correct address',
        },
      },
    })

```

**File:** features/address-provider/module/address-cache/index.js (L248-302)
```javascript
  async set({ baseAssetName, walletAccountName, derivationPath, multisigDataIndex, address }) {
    assert(typeof walletAccountName === 'string', 'expected string "walletAccountName"')
    assert(typeof derivationPath === 'string', 'expected string "derivationPath"')
    assert(typeof baseAssetName === 'string', 'expected string "baseAssetName"')
    assert(
      multisigDataIndex === undefined || typeof multisigDataIndex === 'number',
      'expected number "multisigDataIndex"'
    )
    assert(!!address, 'expected "address"')
    if (this.#config.disabled) return
    await this.#loaded.promise

    address = address.toString()
    const path = getCachePath({
      baseAssetName,
      walletAccountName,
      derivationPath,
      multisigDataIndex,
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

    await this.#update(addressCacheChanges)
  }
```
