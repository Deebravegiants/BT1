### Title
Stale wallet-account address cache reused after account removal/reuse leads to funds sent to wrong address - ([File: features/address-provider/module/address-cache/index.js])

### Summary
The ParaSpace bug class is: a removal operation deletes the top-level registry entry for an entity (`assetFeederMap[_asset]`) but leaves a nested mapping (`feederPrice`) untouched, so when the entity identifier is reused, stale data is silently served as if it were fresh. The equivalent pattern exists in the `hydra--003` wallet-accounts / address-cache subsystem: `AddressCache` persists derived receive addresses keyed only by `walletAccountName` + `derivationPath`, and nothing purges those cache entries when the corresponding wallet account is disabled or removed. [1](#0-0) 

### Finding Description
`WalletAccounts.disableMany` and `WalletAccounts.removeMany` delete a wallet account (and its hardware public keys) from `#walletAccountsInternalAtom` / `#hardwareWalletPublicKeys`, but they never touch the `AddressCache` storage, which is a completely separate module keyed only by the wallet account's *name string* (e.g. `"exodus_1"`, `"trezor_1_hp"`): [2](#0-1) [3](#0-2) 

`AddressCache#set` stores `{ address }` for a given `(baseAssetName, walletAccountName, derivationPath)` tuple in a persisted, disk-backed cache, keyed purely by that string tuple — with no linkage to any account/seed identity token that would change when the account is disabled/recreated: [4](#0-3) 

The code that loads/writes this cache into an atom only reacts to `enabledWalletAccountsAtom` to know which caches to load, but never deletes cache entries for names that get disabled or removed; there is an explicit unresolved TODO acknowledging this exact gap:
```
// todo delete address cache for portfolio when deleted
``` [5](#0-4) 

`AddressProvider.getReceiveAddress`/`getReceiveAddresses` can be called with `useCache: true`, in which case the cached address is returned directly without being re-derived or validated against the current key material, as confirmed by the cache-behavior test suite: [6](#0-5) 

The wallet-accounts module reuses account name slots: `fillIndexGapsOnCreation` fills gaps left by disabled/removed accounts with brand-new, unrelated wallet accounts using the *same name* (e.g. `exodus_1`), confirmed by the "should create new wallet account at gap index" / "should re-enable and update disabled wallet account at gap index" tests: [7](#0-6) [8](#0-7) 

For hardware-wallet accounts specifically, `disableMany` fully deletes the account entry and its public keys (rather than just flagging `enabled: false`), and a subsequent test shows the same name (`trezor_1_hp`) can be reused/recreated: [9](#0-8) [10](#0-9) 

Because the `AddressCache` module is never notified of, nor purges, entries for a disabled/removed `walletAccountName`, if that same name string is later reused for a different wallet account (e.g. gap-index reuse for `EXODUS_SRC` accounts, or a hardware-wallet slot such as `trezor_1_hp` being recreated after a device swap/reset), any `getReceiveAddress`/`getReceiveAddresses` call made with `useCache: true` for that name+derivationPath returns the **old account's address**, not the new account's freshly-derivable address — exactly mirroring the ParaSpace pattern where `feederPrice[feeder]` values survive `delete assetFeederMap[_asset]` and get reused once the same `_asset` key reappears.

### Impact Explanation
If a user disables/removes a wallet account and the same name slot is later populated by a different account (different underlying keys — e.g., a different hardware device reusing the same portfolio label/id, or any flow that recreates an account under the same name), any code path that calls the address provider with `useCache: true` will silently hand back a receive address that belongs to the *old*, now-unrelated account rather than the current one. A user directing funds to what they believe is their current account's receive address could have funds sent to an address they no longer control (the stale cached address), resulting in direct, permanent loss of funds — a wallet-compromise/fund-misdirection impact analogous to the ParaSpace liquidation-of-healthy-accounts impact caused by stale price reuse.

### Likelihood Explanation
This requires: (1) a wallet account being disabled/removed, (2) the same name string later being reused by a different account/seed material (via gap-index reuse for regular accounts or via device reconnection/reset for hardware accounts using the same portfolio id), and (3) a caller using `useCache: true` for that combination before the cache is invalidated by other means (e.g. explicit reconciliation via `getMismatches`). The explicit unresolved `// todo delete address cache for portfolio when deleted` comment shows this is a known, currently-unaddressed gap in the codebase, raising confidence that the condition is reachable in real flows (e.g. gap-index account recreation is an intentional, tested feature) even though the exact end-to-end trigger for `useCache: true` on a stale name was not fully traced in this pass.

### Recommendation
When a wallet account is disabled (`disableMany`) or removed (`removeMany`) in `features/wallet-accounts/src/module/wallet-accounts.ts`, emit an event/call into the `AddressCache` module to purge all cache entries keyed by that `walletAccountName` (all `baseAssetName`/`derivationPath` combinations), mirroring the ParaSpace fix of clearing `feederPrice` on `_removeAsset`. Additionally, consider preventing `useCache: true` lookups from returning an address unless it has been validated against currently-active key material, or bind cache entries to an immutable account/seed identifier (not just the reusable name string) so a name recycling event cannot resurrect unrelated stale addresses.

### Proof of Concept
1. Create wallet account `exodus_1` (EXODUS_SRC) or a hardware account `trezor_1_hp`.
2. Call `addressProvider.getReceiveAddress({ ..., walletAccount, useCache: true })` to populate `AddressCache` for that `walletAccountName` — confirmed cache-hit behavior in [6](#0-5) .
3. Disable/remove that account via `walletAccounts.disable('exodus_1')` or `walletAccounts.disableMany(['trezor_1_hp'])` — the wallet-account entry and its public keys are deleted, but nothing calls into `AddressCache` to purge the corresponding entries: [9](#0-8) .
4. Recreate/re-populate an account under the same name (e.g. via `fillIndexGapsOnCreation`, shown feasible in [7](#0-6) , or reconnect a different/reset hardware device reusing the same `trezor_1_hp` id).
5. Call `getReceiveAddress({ ..., walletAccount, useCache: true })` again — `AddressCache#get` returns the old, stale address from step 2 rather than deriving fresh from the new account's key material, since the cache is never invalidated on account removal.

### Citations

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

**File:** features/address-provider/module/address-cache/index.js (L313-317)
```javascript
// todo delete address cache for portfolio when deleted
// todo update headless to not take `addressCache` id & refactor addresses provider to use this instead
const addressCacheModuleDefinition = {
  id: 'addressCache',
  factory: (deps) => new AddressCache({ ...deps }),
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L420-448)
```typescript
  disableMany = async (walletAccountNames: string[]) => {
    const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
    walletAccountNames = walletAccountNames.filter(
      (walletAccount) => currentWalletAccounts[walletAccount]
    )

    if (walletAccountNames.length === 0) return

    const walletAccounts = { ...currentWalletAccounts }

    await this.setActive((oldValue) =>
      walletAccountNames.includes(oldValue) ? WalletAccount.DEFAULT_NAME : oldValue
    )

    for (const walletAccount of walletAccountNames) {
      if (walletAccounts[walletAccount].isHardware) {
        delete walletAccounts[walletAccount]
        delete this.#hardwareWalletPublicKeys[walletAccount]
      } else {
        walletAccounts[walletAccount] = this.#disableWalletAccount(walletAccounts, walletAccount)
      }
    }

    if (equalWalletAccounts(currentWalletAccounts, walletAccounts)) return

    await this.#walletAccountsInternalAtom.set(walletAccounts)
    await this.#savePublicKeys()
    await this.#updateFusion()
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L450-479)
```typescript
  removeMany = async (names: string[]) => {
    if (!this.#fillIndexGapsOnCreation) {
      throw new Error(
        'removeMany can only be used in conjunction with fillIndexGapsOnCreation. Please disable instead.'
      )
    }

    const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
    const walletAccounts = { ...currentWalletAccounts }
    const active = await this.#activeWalletAccountAtom.get()

    for (const name of names) {
      if (name === DEFAULT_WALLET_ACCOUNT) {
        throw new Error("Can't remove default walletAccount")
      }

      if (walletAccounts[name]?.isHardware) delete this.#hardwareWalletPublicKeys[name]
      delete walletAccounts[name]
    }

    if (equalWalletAccounts(currentWalletAccounts, walletAccounts)) return

    if (names.includes(active)) {
      await this.setActive(DEFAULT_WALLET_ACCOUNT)
    }

    await this.#walletAccountsInternalAtom.set(walletAccounts)
    await this.#savePublicKeys()
    await this.#updateFusion()
  }
```

**File:** features/address-provider/__tests__/module/seed/cache.test.js (L58-76)
```javascript
  test('getReceiveAddress() uses address cache if requested', async () => {
    addressCacheGet.mockImplementation(({ baseAssetName, walletAccountName, derivationPath }) => {
      expect(baseAssetName).toBe(assetName)
      expect(walletAccountName).toBe(walletAccount.toString())
      expect(derivationPath).toBe("m/44'/0'/0'/0/0")
      return { address: 'cached-address' }
    })

    const address = await addressProvider.getReceiveAddress({
      assetName,
      walletAccount,
      purpose: 44,
      chainIndex: 1,
      addressIndex: 55,
      useCache: true,
    })

    expect(address.toString()).toBe('cached-address')
  })
```

**File:** features/wallet-accounts/src/module/__tests__/index.test.ts (L343-374)
```typescript
      it('should create new wallet account at gap index', async () => {
        const { walletAccounts } = await prepare({
          walletAccounts: {
            exodus_0: stored.exodus_0,
            exodus_2: { ...stored.exodus_0, index: 2 },
          },
          config: {
            fillIndexGapsOnCreation: true,
          },
        })

        await walletAccounts.create({
          label: 'Potters Big Stash',
          color: '#ff0000',
          icon: 'exodus',
        } as WalletAccountsData)

        await walletAccounts.create({
          label: 'Potters Secret Chamber',
          color: '#3f1381',
          icon: 'exodus',
        } as WalletAccountsData)

        const stash = await walletAccounts.get('exodus_1')

        expect(stash.label).toBe('Potters Big Stash')
        expect(stash.index).toBe(1)

        const chamber = await walletAccounts.get('exodus_3')
        expect(chamber.label).toBe('Potters Secret Chamber')
        expect(chamber.index).toBe(3)
      })
```

**File:** features/wallet-accounts/src/module/__tests__/index.test.ts (L376-394)
```typescript
      it('should re-enable and update disabled wallet account at gap index', async () => {
        const { walletAccounts } = await prepare({
          walletAccounts: {
            exodus_0: stored.exodus_0,
            exodus_1: { ...stored.exodus_0, index: 1, enabled: false },
            exodus_2: { ...stored.exodus_0, index: 2 },
          },
          config: {
            fillIndexGapsOnCreation: true,
          },
        })

        await walletAccounts.create({
          label: 'Potters Big Stash',
          color: '#ff0000',
          icon: 'exodus',
        } as WalletAccountsData)

        const stash = await walletAccounts.get('exodus_1')
```

**File:** features/wallet-accounts/src/module/__tests__/index.test.ts (L750-763)
```typescript
      it('should remove hardware wallet account', async () => {
        const { walletAccounts } = await prepare({
          walletAccounts: {
            ...stored,
            trezor_1_hp: { label: 'Trezor', source: TREZOR_SRC, index: 1, id: 'hp' },
          },
          allowedSources: [TREZOR_SRC, EXODUS_SRC],
        })
        expect(await walletAccounts.get('trezor_1_hp')).toBeDefined()

        await walletAccounts.disable('trezor_1_hp')

        expect(await walletAccounts.get('trezor_1_hp')).toBeUndefined()
      })
```
