Based on my research, I found a plausible structural analog to the Ajna `moveQuoteToken()` bankruptcy-accounting bug inside `@exodus/wallet-accounts`. I was not able to fully inspect the `disable()` and `setExternalAddress()` implementations before running out of iterations, so treat the completeness claims below as based on what I could verify (`removeMany`, `getNextIndex`/`shouldDeriveIndex` in `utils.ts`, and the atom wiring in `index.ts`).

### Title
Stale external wallet address bleeds into a reused wallet-account slot after `removeMany()` - (File: `features/wallet-accounts/src/module/wallet-accounts.ts`)

### Summary
The Ajna bug is a case where one function that drains a shared "bucket" resets its accounting to a clean state, while a sibling function performing the analogous drain does not, so a future depositor into that same bucket silently inherits stale accounting. `@exodus/wallet-accounts` has the same class of defect: `removeMany()` [1](#0-0)  only resets `#hardwareWalletPublicKeys[name]` when the removed account `isHardware`, but never clears the per-account `externalWalletAddressesAtom` entry keyed by the same wallet-account name. Because `fillIndexGapsOnCreation` deliberately treats removed/disabled slots as reusable "gaps" [2](#0-1) , a subsequently created account can be assigned the exact same wallet-account name/index as the removed one, and will inherit the old, un-cleared `externalWalletAddressesAtom` record for that name.

### Finding Description
- `externalWalletAddressesAtom` stores custodial/external deposit addresses keyed by wallet-account name, e.g. `{ polymarket_0: { matic: '0xABC' } }`, as shown in the module's own tests [3](#0-2) .
- `removeMany(names)` deletes the wallet account entry and, only for hardware accounts, deletes `#hardwareWalletPublicKeys[name]`; there is no equivalent cleanup call for `externalWalletAddressesAtom` for any removed name [1](#0-0) .
- `getNextIndex()` — used by `createMany()`/`create()` — when `fillIndexGapsOnCreation` is enabled, only counts *enabled* accounts as "existing" and returns the first missing gap index, meaning a disabled/removed account's index (and by extension its canonical name, e.g. `exodus_1`) becomes available for reuse by a brand-new, logically unrelated wallet account [2](#0-1) , a behavior explicitly exercised in the test suite for "gap index" creation [4](#0-3) .
- This is structurally identical to the Ajna root cause: two different removal paths for the same conceptual bucket state (hardware keys vs. external addresses) are not kept consistent, and the "bucket" (wallet-account name/index) can be reused by a future entrant without its stale sub-ledger being wiped — precisely the "future depositor inherits diluted/incorrect accounting" pattern from the report.
- I was not able to verify, in the time available, whether `disable()` or another lifecycle path (e.g. a plugin subscribed to wallet-account removal) separately clears `externalWalletAddressesAtom`. If such cleanup exists elsewhere, this finding would be invalidated; I could not confirm this either way.

### Impact Explanation
If the gap is real, a new wallet account created after a previous one occupying the same name/index was removed via `removeMany()` would display or use the old account's external/custodial deposit address(es) stored under that name. Since external addresses are used for receiving funds for custodial-style assets, an address belonging to a deleted/replaced account bleeding into a new account is a direct account-isolation violation with wallet-fund-safety implications (a user could be shown or could use a deposit address that no longer corresponds to a key/account they control in the way they expect).

### Likelihood Explanation
Requires `fillIndexGapsOnCreation: true` (opt-in per integrator/config) and a user or client explicitly removing a wallet account with `removeMany()` and later creating a new one — a normal, unprivileged, user-triggered workflow (delete account → create new account) with no attacker/malicious-peer involvement, so the trigger conditions are realistic and reachable from ordinary UI actions on any integrator that enables this config flag.

### Recommendation
In `removeMany()`, clear any per-wallet-account sub-ledgers keyed by the removed name — specifically reset the corresponding `externalWalletAddressesAtom` entry (not just `#hardwareWalletPublicKeys`) — mirroring the cleanup already done for hardware public keys, so a reused index/name always starts from a clean accounting state, analogous to how Ajna's `removeQuoteToken()` bankruptcy check needed to be mirrored in `moveQuoteToken()`.

### Proof of Concept
1. Configure `walletAccounts` with `fillIndexGapsOnCreation: true`.
2. Create `exodus_1` and call `walletAccounts.setExternalAddress({ walletAccount: 'exodus_1', assetName: 'matic', address: '0xOLD' })`.
3. Call `walletAccounts.removeMany(['exodus_1'])` — per `removeMany()`'s code path, only `#hardwareWalletPublicKeys['exodus_1']` would be deleted (and only if it was hardware); `externalWalletAddressesAtom['exodus_1']` is left untouched.
4. Call `walletAccounts.create(...)` for a new non-hardware Exodus account; per `getNextIndex()`, it reuses index `1` and becomes `exodus_1` again.
5. Query `externalWalletAddressesAtom.get()` — if not cleared elsewhere, it would still report `{ exodus_1: { matic: '0xOLD' } }` for the brand-new account.

Note: step 5's outcome depends on code paths I could not fully inspect (`disable()`, any wallet-account-removal plugin hooks); this PoC should be executed/validated in the full repository to confirm before treating this as a confirmed vulnerability.

### Citations

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

**File:** features/wallet-accounts/src/module/utils.ts (L47-75)
```typescript
export const getNextIndex = ({
  walletAccounts,
  seedId,
  source,
  compatibilityMode,
  fillIndexGapsOnCreation,
}: GetNextIndexParams) => {
  const existing = Object.values(walletAccounts)
    .filter(
      (w) =>
        w.source === source &&
        w.compatibilityMode === compatibilityMode &&
        w.seedId === seedId &&
        !w.id &&
        (!fillIndexGapsOnCreation || w.enabled)
    )
    .sort((a, b) => (a.index ?? 0) - (b.index ?? 0))

  if (fillIndexGapsOnCreation) {
    return (
      [...existing.keys()].find((i) => existing[Number(i)]?.index !== Number(i)) ?? existing.length
    )
  }

  const indexes = existing
    .map(({ index }) => index)
    .filter((i): i is number => typeof i === 'number')
  return Math.max(-1, ...indexes) + 1
}
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

**File:** features/wallet-accounts/src/module/__tests__/index.test.ts (L858-870)
```typescript
    describe('setExternalAddress', () => {
      it('should set an address for a wallet account and asset', async () => {
        const { walletAccounts, externalWalletAddressesAtom } = await prepare()

        await walletAccounts.setExternalAddress({
          walletAccount: 'polymarket_0',
          assetName: 'matic',
          address: '0xABC',
        })

        const stored = await externalWalletAddressesAtom.get()
        expect(stored).toEqual({ polymarket_0: { matic: '0xABC' } })
      })
```
