### Title
`getFees` performs no wallet-lock check and can disclose cached tx/account-state metadata while locked - ([File: features/fees/module/index.js])

### Summary
`createFees().getFees` in `features/fees/module/index.js` reads `walletAccountsAtom`, `txLogsAtom`, and `accountStatesAtom` directly with no lock/auth guard of any kind. Lock enforcement in this codebase is implemented per-feature (e.g. `address-provider` explicitly throws `'address-provider: wallet should be unlocked'`), and there is no centralized RPC/IOC middleware that blocks calls while the wallet is locked, so `fees.getFees` is reachable and functional in a locked state.

### Finding Description
`getFees` fetches `walletAccountsAtom.get()`, and — when the asset's legacy `getFee` API is used — `txLogsAtom.get()` and `accountStatesAtom.get()`, then passes the account's cached `accountState` and `txSet` data straight into `baseAsset.api.getFee(...)` and returns the resulting fee object to the caller: [1](#0-0) [2](#0-1) 

There is no lock/auth check anywhere in the module — `logger`/`isLocked`/`locked` do not appear in `features/fees/**` at all, and the module's dependency list (`feeMonitors`, `accountStatesAtom`, `txLogsAtom`, `assetsModule`, `addressProvider`, `walletAccountsAtom`, `logger`) contains nothing that could enforce it: [3](#0-2) 

Separately, `blockchainMetadataAtom` (the source for `accountStatesAtom`/`txLogsAtom`) is not cleared on lock. The blockchain-metadata lifecycle plugin only suppresses **port emission** to the UI when locked (`onLoad({ isLocked })`) and clears data only via `onClear` (wallet deletion) — there is no `onLock` handler that wipes `blockchainMetadataAtom`: [4](#0-3) 

This means the in-memory account state/tx metadata (balances, cursors, previous tx data used for fee calc) persists in the atoms after `wallet.lock()` is called; only the keychain seeds are removed on lock: [5](#0-4) 

Since `getFees` reads these atoms directly with no gating, an attacker who can invoke `fees.getFees` via RPC (e.g. a connected dApp/origin issuing SDK/RPC calls) can retrieve `accountState`/`txSet`-derived data for a chosen `assetName`/`walletAccount` even while the wallet is locked, because:
1. Lock enforcement is not centralized in the RPC/IOC layer — `sdks/headless/src/api/index.js` simply asyncifies and exposes every feature API method without any lock check wrapper.
2. Other privacy-sensitive features (`address-provider`) implement their own explicit lock checks, proving this is an opt-in pattern per-feature, and `fees` opted out.

### Impact Explanation
An unauthenticated/unprivileged caller with access to the wallet's RPC surface while it is locked can extract account/transaction metadata (previously loaded account state and tx log info for a wallet account/asset) via `fees.getFees`, violating the "locked means locked" invariant. This is metadata disclosure (balances/tx-derived cursor and UTXO-like information used in fee computation), not funds theft or signing — a scoped, unlocked-state information disclosure without authentication.

### Likelihood Explanation
High feasibility: no special privileges are needed beyond being able to call the RPC (e.g., a connected dApp or any code path that can reach the SDK API). The wallet only needs to have been previously unlocked once (so the atoms are populated) and then locked; the attacker calls `getFees({ assetName, walletAccount })` afterward. This is fully reproducible with a unit test using the existing `feesModuleDefinition.factory` test harness.

### Recommendation
Add an explicit lock/authentication guard at the start of `getFees` (and any other read path in `features/fees/module/index.js` that touches `accountStatesAtom`/`txLogsAtom`/`walletAccountsAtom`), following the pattern used in `features/address-provider/api/index.js`, rejecting the call (or returning the safe `notLoadedYetDefault`) when the wallet is locked. Additionally, consider clearing/withholding `blockchainMetadataAtom` (and thus `accountStatesAtom`/`txLogsAtom`) contents while locked, mirroring how `address-provider` guards output rather than relying solely on suppressed UI emission.

### Proof of Concept
Using the existing test harness in `features/fees/__tests__/module.test.js`:
1. Set up `feesModule` as in the existing `beforeEach`, and seed `txLogsAtom`/`accountStatesAtom` with sample values (as done in the `'should return value when getFee'` test at lines 128–166).
2. Introduce a `walletLockAtom`/mock auth guard set to locked (`isLocked: true`), matching how `address-provider` tests simulate lock (`sdks/headless/__tests__/address-provider.test.js` lines 91–98, 115–129).
3. Call `await feesModule.getFees({ assetName: 'ethereum', walletAccount })`.
4. Expected (fixed) behavior: the call should reject with a `wallet should be unlocked`-style error, or return `notLoadedYetDefault`, and must NOT invoke `accountStatesAtom.get()`/`txLogsAtom.get()` or pass `accountState`/`txSet` to `baseAsset.api.getFee`.
5. Current (vulnerable) behavior: the call succeeds and returns `{ fee, gasLimit, extraFeeData }` derived from `accountState`/`txSet`, identical to the unlocked-state result, proving the metadata is reachable while locked.

### Citations

**File:** features/fees/module/index.js (L36-53)
```javascript
    getFees: async ({
      assetName,
      walletAccount,
      fromAddress: providedFromAddress,
      toAddress: providedToAddress,
      ...rest
    }) => {
      const asset = await assetsModule.getAsset(assetName)

      const notLoadedYetDefault = { fee: asset.feeAsset.currency.ZERO }
      const baseAsset = asset.baseAsset
      const feeData = await feeMonitors.getFeeData({ assetName: baseAsset.name })
      if (!feeData) {
        return notLoadedYetDefault
      }

      const walletAccountsData = await walletAccountsAtom.get()
      const walletAccountInstance = walletAccountsData[walletAccount]
```

**File:** features/fees/module/index.js (L94-120)
```javascript
      // legacy, from when they were selectors
      if (baseAsset.api?.getFee) {
        const { value: txLogs } = await txLogsAtom.get()
        const txLog = txLogs[walletAccount]?.[assetName]
        if (!txLog) {
          return notLoadedYetDefault
        }

        const { value: accountStates } = await accountStatesAtom.get()
        const accountState = accountStates[walletAccount]?.[baseAsset.name]
        if (!accountState) {
          return notLoadedYetDefault
        }

        const fees = unifyFeeResult(
          baseAsset.api.getFee({
            ...rest,
            address: toAddress, // legacy
            fromAddress,
            toAddress,
            asset,
            accountState,
            txSet: txLog,
            feeData,
          })
        )
        return validateFeeResult({ asset, fees })
```

**File:** features/fees/module/index.js (L133-147)
```javascript
const feesModuleDefinition = {
  id: 'fees',
  type: 'module',
  factory: createFees,
  dependencies: [
    'feeMonitors',
    'accountStatesAtom',
    'txLogsAtom',
    'assetsModule',
    'addressProvider',
    'walletAccountsAtom',
    'logger',
  ],
  public: true,
}
```

**File:** features/blockchain-metadata/plugin/lifecycle.js (L1-45)
```javascript
const createBlockchainLifecyclePlugin = ({ blockchainMetadata, blockchainMetadataAtom, port }) => {
  let subscriptions = []

  const onStart = async () => {
    subscriptions.push(
      blockchainMetadataAtom.observe(({ accountStateChanges, txLogChanges }) => {
        if (txLogChanges) {
          port.emit('txLogs', { changes: txLogChanges })
        }

        if (accountStateChanges) {
          port.emit('accountStates', { changes: accountStateChanges })
        }
      })
    )
  }

  async function emitAll() {
    const { value } = await blockchainMetadataAtom.get()
    port.emit('accountStates', { value: value.accountStates })
    port.emit('txLogs', { value: value.txs })
  }

  const onLoad = async ({ isLocked }) => {
    if (isLocked) return
    emitAll()
  }

  const onUnlock = async () => {
    blockchainMetadata.load().then(() => emitAll())
  }

  const onClear = async () => {
    await blockchainMetadata.clear()
  }

  const onStop = () => {
    subscriptions.forEach((unsubscribe) => unsubscribe())
    subscriptions = []

    blockchainMetadata.stop()
  }

  return { onStart, onUnlock, onClear, onLoad, onStop }
}
```

**File:** features/wallet/module/wallet.js (L276-280)
```javascript
  lock = async () => {
    this.#keychain.removeAllSeeds()

    this.#isLocked = true
  }
```
