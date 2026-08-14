### Title
`fees.getFees` RPC bypasses the wallet lock check enforced by `addressProviderApi`, disclosing cached receive addresses/fees while locked - ([File: features/fees/module/index.js])

### Summary
`exodus.fees.getFees({ assetName, walletAccount })` is exposed to callers via `feesModuleApi` (`features/fees/api/index.js`), which is a thin pass-through with no `lockedAtom` check. Internally, `getFees` derives `fromAddress` by calling the raw `addressProvider` module (not `addressProviderApi`), which also has no lock check, so cached/derivable address data can be returned to an unprivileged caller while the wallet is locked.

### Finding Description
`createFees` in `features/fees/module/index.js` calls `addressProvider.getReceiveAddress({ assetName, walletAccount: walletAccountInstance, useCache: true })` directly: [1](#0-0) 

This `addressProvider` dependency is the raw module (`features/address-provider/module/address-provider.js`), which has no lock gate at all - unlike `addressProviderApi`, which explicitly wraps every method with `withWalletAccountInstance`, and rejects when `lockedAtom.get()` is true: [2](#0-1) 

The `fees` module is exposed to RPC/dapp callers through `feesApiDefinition`, which simply forwards the module with zero additional checks: [3](#0-2) 

`getReceiveAddress({ useCache: true })` can be satisfied from `addressCache`/`knownAddresses` without touching the keychain/seed material at all, as shown by the cache-behavior tests exercising `useCache: true` returning cached addresses directly: [4](#0-3) 

So the call path `exodus.fees.getFees(...)` → `fees` module → raw `addressProvider.getReceiveAddress({ useCache: true })` → address cache never passes through the `lockedAtom.get()` check that exists specifically in `addressProviderApi`. A `grep` across the repo confirms `lockedAtom.get()` is checked in only two places (`features/address-provider/api/index.js` and `sdks/headless/src/api/reporting.js`) - there is no global RPC-level lock gate that uniformly protects every exposed `type: 'api'` surface. (Note: the `public: true` flag seen on module/atom definitions is unrelated to RPC exposure - it is a DI-container cross-namespace visibility flag from `@exodus/dependency-injection`, confirmed by `libraries/dependency-injection/src/container.ts` and its tests; it does not gate lock/auth.)

Consequently, calling `rpc.fees.getFees({ assetName: 'bitcoin', walletAccount: 'exodus_0' })` while `lockedAtom` is `true` will not be rejected outright the way the equivalent `exodus.addressProvider.getReceiveAddress` call would be (which throws `'address-provider: wallet should be unlocked'`). If the requested wallet account's address/xpub was previously cached (e.g., the account was used/derived before the wallet was locked, or is a hardware wallet, or dev-mode mocked xpub), `getFees` will succeed and return a real `fromAddress` and fee data without requiring the unlock check.

### Impact Explanation
This is a lock-boundary bypass that leaks account address/fee data to an unprivileged origin while the wallet is locked, when the equivalent, security-reviewed `addressProviderApi` surface explicitly blocks the same underlying operation. It does not expose private key material (the keychain is empty when locked, so for uncached addresses the call will instead throw/return a default rather than derive new keys), but it does violate the "locked means locked" invariant for previously-derived address data, which the codebase's own address-provider API treats as sensitive enough to gate behind `lockedAtom`.

### Likelihood Explanation
Reachable from any dapp/origin allowed to call the SDK's `fees` API via RPC, with no special privilege required beyond ordinary RPC access - the same access an origin has to call `exodus.fees.getFees` legitimately per the feature's own README. It is fully reproducible: the precondition is simply `lockedAtom === true` and a wallet account/asset combination whose address has previously been cached (a common state after any prior unlocked usage).

### Recommendation
Add a `lockedAtom` check to `feesModuleApi`/`createFees`, mirroring `withWalletAccountInstance` in `features/address-provider/api/index.js`, so `getFees` (and any other RPC-exposed accessor that indirectly calls `addressProvider`) rejects while the wallet is locked. Alternatively, have the `fees` module depend on `addressProviderApi`'s locked-aware wrapper rather than the raw `addressProvider` module.

### Proof of Concept
Integration test (extending `features/fees/__tests__/module.test.js` pattern):
```js
it('should reject getFees when wallet is locked', async () => {
  const lockedAtom = createInMemoryAtom({ defaultValue: true })
  // Pre-populate addressCache/knownAddresses with a cached address for exodus_0/bitcoin
  // as would occur from prior unlocked usage.
  feesModule = createFees({
    feeMonitors, accountStatesAtom, txLogsAtom, assetsModule, logger,
    addressProvider, walletAccountsAtom, lockedAtom, // (not currently a dependency)
  })

  await expect(
    feesModule.getFees({ assetName: 'bitcoin', walletAccount: 'exodus_0' })
  ).rejects.toThrow(/locked/)
})
```
Expected (current, vulnerable) behavior: the call resolves with fee/address data instead of throwing, in contrast to `exodus.addressProvider.getReceiveAddress` under the same locked precondition, which is asserted to reject in `sdks/headless/__tests__/address-provider.test.js` lines 91-98.

### Citations

**File:** features/fees/module/index.js (L55-68)
```javascript
      async function resolveFromAddress() {
        if (providedFromAddress) {
          return providedFromAddress
        }

        const addressObject = await addressProvider.getReceiveAddress({
          assetName: asset.name,
          walletAccount: walletAccountInstance,
          useCache: true,
        })
        return addressObject.toString()
      }

      const fromAddress = await resolveFromAddress()
```

**File:** features/address-provider/api/index.js (L12-18)
```javascript
  const withWalletAccountInstance =
    (fn) =>
    async ({ walletAccount, ...rest }) => {
      if (await lockedAtom.get()) throw new Error('address-provider: wallet should be unlocked')
      const walletAccounts = await walletAccountsAtom.get()
      return fn({ ...rest, walletAccount: walletAccount && walletAccounts[walletAccount] })
    }
```

**File:** features/fees/api/index.js (L1-8)
```javascript
const createFeesApi = ({ fees }) => ({ fees })

const feesApiDefinition = {
  id: 'feesModuleApi',
  type: 'api',
  factory: createFeesApi,
  dependencies: ['fees'],
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
