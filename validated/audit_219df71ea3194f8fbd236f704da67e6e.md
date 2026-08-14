### Title
Unauthorized wallet destruction via `wallet!clear` RPC method bypassing `applicationWalletApi`-level lock/consent gate - ([File: sdks/headless/src/api/index.js])

### Summary
The `featureApis.wallet` `Proxy` `get` trap in `sdks/headless/src/api/index.js` only intercepts property names that exist in `applicationWalletApi`; any method name on the raw `wallet` feature module that is *not* one of those explicitly wrapped/gated names falls through to `target[prop]`, i.e. the unguarded raw module method. `wallet.clear` (defined in `features/wallet/module/wallet.js` and exposed via `features/wallet/api/index.js` as `clear: wallet.clear`) is exactly such a method: it is not present in `applicationWalletApi` (which only exposes `delete`, mapped to the presumably-gated `application.delete`), so calling it over RPC reaches the raw `wallet.clear()` implementation directly.

### Finding Description
`sdks/headless/src/api/index.js` builds `applicationWalletApi` as an explicit allow-list of deprecated/gated wallet-related operations (`addSeed`, `start`, `stop`, `load`, `unload`, `create`, `lock`, `unlock`, `import`, `delete`, `getMnemonic`, `setBackedUp`, `changePassphrase`, `changeLockTimer`, `restartAutoLockTimer`, `restoreFromCurrentPhrase`) [1](#0-0) . It then wraps `featureApis.wallet` in a `Proxy` whose `get` trap returns `applicationWalletApi[prop]` only `if (prop in applicationWalletApi)`, otherwise falling through to `target[prop]`, i.e. the raw `wallet` feature-module method [2](#0-1) .

The raw `wallet` feature module exposes `clear` directly from the `Wallet` class instance: `clear: wallet.clear` in `features/wallet/api/index.js` [3](#0-2) . `Wallet#clear` in `features/wallet/module/wallet.js` locks the wallet and deletes the seed, extra seeds, generated passphrase, and passphrase-set flag from storage, with **no unlock/passphrase/consent check** at all: `clear = async () => { this.lock(); await Promise.all([this.walletStorage.delete(SEED_KEY), this.walletStorage.delete(EXTRA_SEEDS_KEY), this.walletStorage.delete(GENERATED_PASSPHRASE_KEY), this.walletStorage.delete(HAS_USER_SET_PASSPHRASE_KEY), this.#seedMetadataAtom.set(undefined)]) }` [4](#0-3) . Compare this to other privileged wallet mutations in the same module, such as `removeManySeeds`, which explicitly calls `this.#assertWalletIsUnlocked()` before mutating state [5](#0-4) ; `clear` has no equivalent guard.

Because `wallet!clear` is not one of the keys in `applicationWalletApi`, the RPC layer (`@exodus/sdk-rpc`, which flattens the SDK object and exposes `namespace!method` names via `flattenObject`) [6](#0-5)  reaches this unguarded raw method through the `Proxy`'s fallback branch rather than through any lock/consent-checked `application`-level entry point. An unprivileged RPC caller (e.g. a dapp/webview client using `createRPCClient`) can therefore invoke `wallet!clear` and immediately wipe the seed, extra seeds, and passphrase state regardless of lock state, with no passphrase or unlock precondition — unlike `application.delete`, which is the intended/gated deletion path referenced by `applicationWalletApi.delete`.

### Impact Explanation
This is a destructive, irreversible loss-of-funds-adjacent vulnerability: calling `wallet!clear` deletes the encrypted seed and passphrase-related storage keys without any authentication, unlock, or passphrase confirmation, matching a "destructive wallet-state mutation" / denial-of-wallet impact. Any RPC-capable caller reachable through the SDK boundary (e.g. an embedding dapp/host process that only has access to the "wallet" namespace and not privileged `application`-level access) can wipe wallet secrets, forcing the user into wallet loss (or at minimum a disruptive forced-restore flow) without ever going through the `application`-level lock/consent gate that `applicationWalletApi` was designed to enforce.

### Likelihood Explanation
Feasibility is high and requires no special preconditions beyond ordinary RPC access to the `wallet` namespace exposed by the headless SDK API (`sdks/headless/src/api/index.js`). The attacker does not need to know a passphrase, does not need the wallet to be unlocked, and does not need to defeat any guard — the raw `clear` method performs no checks whatsoever. The bug is deterministic and trivially repeatable: every call to `wallet!clear` succeeds and wipes state, regardless of lock state.

### Recommendation
Ensure the `Proxy` get trap denies (or routes to an explicitly application-gated equivalent) any raw feature-module method that performs privileged state mutation, rather than defaulting to `target[prop]` for anything not in the allow-list. Concretely: either remove `clear` from the RPC-exposed `wallet` API surface entirely (require callers to go exclusively through `application.delete`), or add an explicit `assertWalletIsUnlocked`/consent check inside `Wallet#clear` itself so it cannot be invoked destructively from an unauthenticated context, and change the `Proxy` to throw/deny access for any raw method not explicitly allow-listed rather than silently falling through to `target[prop]`.

### Proof of Concept
Integration test using `createRPCClient`/`createRPC` helper (as in `sdks/headless/__tests__/utils/rpc.js`) against a headless SDK instance:
1. Start the application, create a wallet with a passphrase, then lock it (`exodus.application.lock()`), or simply do not unlock it after `create`.
2. Using the RPC client (or the flattened API exposed by `createDomainSerialization`/`createProcessRPC`), invoke the raw method path `wallet!clear` (i.e. `client.wallet.clear()` under `createRPCClient`).
3. Assert: currently this resolves successfully and immediately wipes `SEED_KEY`, `EXTRA_SEEDS_KEY`, `GENERATED_PASSPHRASE_KEY`, `HAS_USER_SET_PASSPHRASE_KEY` from `walletStorage`, and `exodus.wallet.exists()` subsequently resolves to `false` — with no passphrase supplied and while the wallet is locked.
4. Expected/fixed behavior: the call should be rejected (e.g. `METHOD_NOT_FOUND` or an explicit auth/lock error) unless routed through the gated `application.delete` (AUTH_BOUNDARY), and `wallet.exists()` should remain `true` after the rejected call.

### Citations

**File:** sdks/headless/src/api/index.js (L51-68)
```javascript
  const applicationWalletApi = {
    addSeed: application.addSeed,
    start: deprecated(application.start),
    stop: deprecated(application.stop),
    load: deprecated(application.load),
    unload: deprecated(application.unload),
    create: deprecated(application.create),
    lock: deprecated(application.lock),
    unlock: deprecated(application.unlock),
    import: deprecated(application.import),
    delete: deprecated(application.delete),
    getMnemonic: deprecated(application.getMnemonic),
    setBackedUp: deprecated(application.setBackedUp),
    changePassphrase: deprecated(application.changePassphrase),
    changeLockTimer: deprecated(application.changeLockTimer),
    restartAutoLockTimer: deprecated(application.restartAutoLockTimer),
    restoreFromCurrentPhrase: deprecated(application.restoreFromCurrentPhrase),
  }
```

**File:** sdks/headless/src/api/index.js (L70-79)
```javascript
  // featureApis.wallet is a proxy when the wallet sdk is used from a separate process, do not spread!
  featureApis.wallet = new Proxy(featureApis.wallet, {
    get(target, prop) {
      if (prop in applicationWalletApi) {
        return applicationWalletApi[prop]
      }

      return target[prop]
    },
  })
```

**File:** features/wallet/api/index.js (L1-23)
```javascript
const createWalletApi = ({ wallet }) => {
  return {
    wallet: {
      exists: wallet.exists,
      hasPassphraseSet: wallet.hasPassphraseSet,
      isLocked: wallet.isLocked,
      getMnemonic: wallet.getMnemonic,
      getSeedMetadata: wallet.getSeedMetadata,
      getPrimarySeedId: wallet.getPrimarySeedId,
      getExtraSeedIds: wallet.getExtraSeedIds,
      addSeed: wallet.addSeed,
      updateSeed: wallet.updateSeed,
      removeManySeeds: wallet.removeManySeeds,
      removeSeed: wallet.removeSeed,
      create: wallet.create,
      import: wallet.import,
      clear: wallet.clear,
      lock: wallet.lock,
      unlock: wallet.unlock,
      changePassphrase: wallet.changePassphrase,
    },
  }
}
```

**File:** features/wallet/module/wallet.js (L173-176)
```javascript
  removeManySeeds = async (seedIds) => {
    this.#assertMultiSeedSupport()
    await this.#assertWalletIsUnlocked()

```

**File:** features/wallet/module/wallet.js (L261-272)
```javascript
  clear = async () => {
    this.lock()

    // Avoid using this.walletStorage.clear as it's not implemented in mobile
    await Promise.all([
      this.walletStorage.delete(SEED_KEY),
      this.walletStorage.delete(EXTRA_SEEDS_KEY),
      this.walletStorage.delete(GENERATED_PASSPHRASE_KEY),
      this.walletStorage.delete(HAS_USER_SET_PASSPHRASE_KEY),
      this.#seedMetadataAtom.set(undefined),
    ])
  }
```

**File:** libraries/sdk-rpc/src/rpc.ts (L10-20)
```typescript
export const flattenObject = <T>(obj: T, path: string[] = []): { [name: string]: Fn } => {
  if (typeof obj === 'function') {
    return { [serializePath(path)]: obj as Fn }
  }

  if (typeof obj !== 'object' || !obj) return {}

  return Object.keys(obj).reduce((acc, key) => {
    return { ...acc, ...flattenObject(obj[key as keyof T], [...path, key]) }
  }, {})
}
```
