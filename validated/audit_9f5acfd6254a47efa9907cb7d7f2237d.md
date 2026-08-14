### Title
`assetSources` RPC methods lack a lock-state gate, enabling wallet-account enumeration while locked - ([File: features/asset-sources/module/asset-sources.ts])

### Summary
The `assetSources` module is registered with `public: true` and its `getSupportedPurposes`, `getDefaultPurpose`, and `isSupported` methods are exposed 1:1 through the RPC API in `features/asset-sources/api/index.ts` without any `lockedAtom` check. This contrasts directly with the sibling `address-provider` module, whose API explicitly wraps every wallet-account-consuming method with a `lockedAtom.get()` guard before touching wallet account data.

### Finding Description
`features/asset-sources/module/asset-sources.ts` defines `AssetSources` with three public methods: [1](#0-0) 

`#getWalletAccount` looks up the requested `walletAccount` id directly in `#walletAccountsAtom` and throws `UnknownWalletAccountError` if it's absent, otherwise returns the `WalletAccount` instance (including `compatibilityMode`/`isMultisig`) which then flows into `getSupportedPurposes` from `module/utils.ts`, whose output (e.g. `[84, 86, 44]` vs `[84, 49]`) differs by compatibility mode: [2](#0-1) 

These methods are exposed as-is via the RPC API layer, with no lock check anywhere in the chain: [3](#0-2) 

Compare this to `features/address-provider/api/index.js`, which is the established pattern in this codebase for gating wallet-account-derived RPC calls behind the lock state: [4](#0-3) 

`asset-sources` has no analogous `lockedAtom` dependency or check — its module's dependency list is only `['assetsAtom', 'walletAccountsAtom', 'availableAssetNamesByWalletAccountAtom']`, and the api factory only depends on `assetSources`: [5](#0-4) 

Because `walletAccountsAtom` is a storage-backed atom (via `filter(walletAccountsInternalAtom, ...)` over a `createStorageAtomFactory`-backed atom) that persists non-seed account metadata to disk, it is capable of holding real account data independent of the in-memory unlock/keychain state: [6](#0-5) [7](#0-6) 

An RPC caller can invoke `getSupportedPurposes`/`getDefaultPurpose`/`isSupported` with a guessed `walletAccount` id while the wallet is locked. `UnknownWalletAccountError` vs a valid purposes array acts as a distinguishing oracle for account existence, and the returned purposes array leaks `compatibilityMode`/`isMultisig`-derived metadata, none of which should be observable pre-unlock per this codebase's own established "locked means locked" invariant (as enforced elsewhere in `address-provider`).

### Impact Explanation
This allows an unauthenticated/locked-state RPC caller to enumerate whether a given `walletAccount` id exists and to infer its `compatibilityMode`/`isMultisig` classification purely from the shape of the purpose array or from the presence/absence of `UnknownWalletAccountError`. This is metadata/account-existence leakage across the lock trust boundary — not key or secret disclosure, but a violation of the "locked means locked" invariant and an account/metadata enumeration primitive.

### Likelihood Explanation
Reaching this code only requires that (a) the `assetSources` module/API is exposed on the RPC surface consuming dapp/host bridge — which it is, being `public: true` and included in `createExodus` via `assetSources(config.assetSources)` — and (b) the `walletAccountsAtom` already contains persisted account data (true whenever the wallet previously existed/was unlocked once and the app process retains storage-backed atom state, or if storage isn't process-lifecycle gated to unlock). No privileged state, keys, or social engineering are needed; a straightforward RPC call while `lockedAtom` is `true` suffices.

### Recommendation
Add a `lockedAtom` dependency to `assetSourcesApiDefinition` (or to the `AssetSources` module) and gate `getSupportedPurposes`, `getDefaultPurpose`, and `isSupported` behind an explicit `if (await lockedAtom.get()) throw new Error(...)` check, mirroring `features/address-provider/api/index.js`'s `withWalletAccountInstance` pattern, before any wallet-account lookup or metadata is returned.

### Proof of Concept
Integration test (modeled after `sdks/headless/__tests__/address-provider.test.js`):
```js
test('should not leak wallet account existence/metadata via assetSources while locked', async () => {
  // wallet is locked (no exodus.application.unlock called)
  await expect(
    exodus.assetSources.getSupportedPurposes({
      walletAccount: WalletAccount.DEFAULT_NAME,
      assetName: 'bitcoin',
    })
  ).rejects.toThrow(/wallet should be unlocked|locked/i)

  await expect(
    exodus.assetSources.getDefaultPurpose({
      walletAccount: WalletAccount.DEFAULT_NAME,
      assetName: 'bitcoin',
    })
  ).rejects.toThrow(/wallet should be unlocked|locked/i)
})
```
Expected (current, vulnerable) behavior: calls resolve successfully (or throw `UnknownWalletAccountError` for a nonexistent id), distinguishing valid from invalid account ids and returning purpose metadata without requiring unlock. Expected (fixed) behavior: both calls reject uniformly with a lock-state error regardless of whether `walletAccount` exists.

### Citations

**File:** features/asset-sources/module/asset-sources.ts (L55-72)
```typescript
  #getWalletAccount = async (walletAccount: string): Promise<WalletAccount> => {
    const all = await this.#walletAccountsAtom.get()
    if (!all[walletAccount]) {
      throw new UnknownWalletAccountError(walletAccount)
    }

    return all[walletAccount]!
  }

  getSupportedPurposes = async ({ walletAccount, assetName }: AssetSource): Promise<number[]> => {
    typeforce(types.assetSource, { walletAccount, assetName }, true)

    const walletAccountInstance = await this.#getWalletAccount(walletAccount)
    return getSupportedPurposes({
      asset: await this.#getAsset(assetName),
      walletAccount: walletAccountInstance,
    })
  }
```

**File:** features/asset-sources/module/asset-sources.ts (L94-102)
```typescript
const createAssetSources = (opts: Dependencies) => new AssetSources(opts)

const assetSourcesDefinition = {
  id: MODULE_ID,
  type: 'module',
  factory: createAssetSources,
  dependencies: ['assetsAtom', 'walletAccountsAtom', 'availableAssetNamesByWalletAccountAtom'],
  public: true,
} as const satisfies Definition
```

**File:** features/asset-sources/module/utils.ts (L13-45)
```typescript
export const getSupportedPurposes = (opts: GetSupportedPurposesOpts) => {
  typeforce(
    {
      asset: types.asset,
      walletAccount: types.walletAccount,
    },
    opts,
    true
  )

  const {
    asset,
    walletAccount: { compatibilityMode, isMultisig },
  } = opts

  const baseAsset = asset.baseAsset
  const apiExists = !!baseAsset.api?.getSupportedPurposes

  assert(
    !isMultisig || apiExists,
    'baseAsset must have api.getSupportedPurposes for a multisig WalletAccount'
  )

  if (apiExists) {
    // we seem to be having two different APIs for getSupportedPurposes, one that expects compatibilityMode separately, and one that expects it on walletAccount
    const supportedPurposes = baseAsset.api?.getSupportedPurposes!({
      ...opts,
      compatibilityMode,
      isMultisig,
    })
    assert(supportedPurposes?.length, 'at least one purpose must be supported')
    return supportedPurposes
  }
```

**File:** features/asset-sources/api/index.ts (L8-15)
```typescript
const createAssetSourcesApi = ({ assetSources }: Dependencies) =>
  ({
    assetSources: {
      getSupportedPurposes: assetSources.getSupportedPurposes,
      getDefaultPurpose: assetSources.getDefaultPurpose,
      isSupported: assetSources.isSupported,
    },
  }) as const
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

**File:** features/wallet-accounts/src/atoms/wallet-accounts.ts (L1-12)
```typescript
import { filter } from '@exodus/atoms'
import type { WalletAccountsInternalAtom } from '../types.js'

// for read-only usage
// modules like txLogsMonitors should wait atom observer to emit any account before start
export default function createWalletAccountsAtom({
  walletAccountsInternalAtom,
}: {
  walletAccountsInternalAtom: WalletAccountsInternalAtom
}) {
  return filter(walletAccountsInternalAtom, (value) => !!value)
}
```

**File:** features/wallet-accounts/src/atoms/wallet-accounts-internal.ts (L14-24)
```typescript
export default function createWalletAccountsInternalAtom({
  storage,
}: {
  storage: Storage<SerializedWalletAccounts>
}) {
  const atomFactory = createStorageAtomFactory({ storage })

  const walletAccountsAtom = atomFactory({
    key: 'walletAccounts',
    isSoleWriter: true,
  })
```
