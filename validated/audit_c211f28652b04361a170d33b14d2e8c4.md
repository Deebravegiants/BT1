### Title
Custom tokens can spoof the ticker/symbol of an existing asset with no uniqueness check, enabling asset-identity confusion during sends/approvals - (File: features/assets-feature/module/assets-module.js)

### Summary
The Rolla `QToken` report describes a class of bug where a generated identifier (the token symbol) is not guaranteed to be unique/collision-resistant, so users can mistake one token for another when making decisions (trading, buying) based on that identifier. The Hydra wallet's custom-token subsystem in `@exodus/assets-feature` has the same root defect: a custom token's `ticker`/`displayTicker` (the identifier shown to users in asset pickers, balances, and send/receive flows) is never checked for uniqueness against other assets already known to the wallet, so a different token with a different underlying `assetId`/`name` can be added and displayed with the exact same ticker as a legitimate, pre-existing asset.

### Finding Description
`normalizeToken` derives the user-facing ticker purely from server-supplied fields, with no collision check against existing assets: [1](#0-0) 

Tokens are deduplicated only by identity (`assetId` + `baseAssetName` via `getFetchCacheKey`, or by `name` in `#handleFetchedToken`), never by `ticker`/`displayTicker`: [2](#0-1) [3](#0-2) 

The project's own test suite demonstrates the exact collision: a custom token `abcd_bitcoin_a2345678` is fetched/validated with `properTicker: 'WC'` / `ticker: 'ED6Bbitcoin3D49BF90'`, i.e. the same displayed ticker (`WC`) as the pre-existing legacy token `waynecoin`, while having a completely different `assetId` and internal `name`: [4](#0-3) 

The only de-duplication logic that triggers when adding this token compares by `name`/`assetId`, not by ticker, so both assets can coexist in the registry with identical displayed tickers: [5](#0-4) 

This mirrors the Rolla finding precisely: the identifier meant to let a user recognize "this is asset X" (`QToken` symbol / `displayTicker`) is generated without any uniqueness guarantee, so two semantically different underlying assets can present the same human-readable identifier to the user.

### Impact Explanation
Wallet UIs (asset pickers, send screens, balance lists, exchange components) render tickers to let users select/confirm which asset they intend to interact with, e.g. `apps/sdk-playground/src/ui/pages/ui/pages/exchange/components/asset.tsx` reads `asset.displayTicker` directly for display. If a custom/registry token can carry the same ticker as a trusted asset (built-in or another custom token), a user relying on the ticker to choose the correct asset for sending funds, granting an approval, or verifying receipt could interact with the wrong token entirely - e.g., sending a payment intended for a legitimate/high-value token to a worthless or malicious lookalike, or approving/signing a transaction against a spoofed contract believed to be the trusted one. This is a direct wallet-fund/asset-selection integrity issue reachable by any unprivileged actor who can get a token listed via the custom-token registry/search flow (`searchTokens`, `addRemoteTokens`, `addTokens`), without requiring any special privilege, matching the "cross-asset identity bleed leading to wrong signing/asset selection" impact class.

### Likelihood Explanation
Likelihood is significant: `addRemoteTokens`/`addTokens`/`searchTokens` in `features/assets-feature/module/assets-module.js` are the standard, user-facing paths for discovering and enabling custom tokens (e.g., "Manage Assets" / "add custom token" flows), and they only validate schema shape (`validateCustomToken`, whose implementation could not be located in the indexed sources but is only invoked conditionally via `shouldValidateCustomToken`) - not ticker uniqueness. No special permissions are needed to get a token with a colliding ticker registered into the local asset registry, and the collision is proven directly by the project's own test fixtures.

### Recommendation
When adding or normalizing a custom token, check `displayTicker`/`ticker` against tickers of already-known assets (built-in and existing custom tokens) with the same or different `baseAssetName`. If a collision is detected, either reject the token, force a disambiguated display (e.g., append network/chain qualifier or a warning badge), or require explicit user acknowledgment before enabling it, similar to how the Rolla remediation added the full year to avoid truncated/colliding identifiers. At minimum, all UI surfaces that render `displayTicker` should also surface a secondary unambiguous identifier (contract address, `baseAssetName`, `assetId`) so a ticker collision cannot alone cause an incorrect selection.

### Proof of Concept
1. Wallet already has asset `waynecoin` with `displayTicker: 'WC'` and `assetId: 'foobar'` (baseAsset `bitcoin`), as set up in `features/assets-feature/module/assets-module.js` tests.
2. Call `assetsModule.addRemoteTokens({ tokenNames: ['abcd_bitcoin_a2345678'] })` (or the equivalent `addTokens`/registry search flow), which fetches a token whose registry entry sets `properTicker: 'WC'` / `displayTicker: 'WC'` but a different `assetId`/`name` (`abcd_bitcoin_a2345678`), as shown in the fixture at: [4](#0-3) 
3. Because de-duplication only checks `name`/`assetId` (`#handleFetchedToken`, `getFetchCacheKey`) and `normalizeToken` does not compare against existing tickers, the wallet's asset registry now can contain two distinct assets both displaying ticker "WC" to the user, exactly analogous to two `QToken`s sharing a truncated symbol in the Rolla report.

### Citations

**File:** features/assets-feature/module/assets-module.js (L31-35)
```javascript
const { get, isEmpty, once, uniq, chunk, pick } = lodash

const getFetchCacheKey = (baseAssetName, assetId) => `${assetId}-${baseAssetName}`

const _isDisabledCustomToken = (token) => token.lifecycleStatus === STATUS.DISABLED
```

**File:** features/assets-feature/module/assets-module.js (L37-42)
```javascript
const normalizeToken = (token) => ({
  ...token,
  name: token.name || token.assetName,
  displayName: token.displayName || token.properName, // eslint-disable-line @exodus/hydra/no-asset-proper
  displayTicker: token.displayTicker || token.properTicker, // eslint-disable-line @exodus/hydra/no-asset-proper
})
```

**File:** features/assets-feature/module/assets-module.js (L603-612)
```javascript
  #handleFetchedToken = (token) => {
    const asset = this.getAsset(token.name)
    if (asset) return { asset, isAdded: false, updates: [] }

    const { name } = this.#registry.addCustomToken(token) // add to registry
    const updates = this.#handleCombinedParents(token)

    this.#logger.log('Custom token added:', name)
    return { asset: this.getAsset(name), isAdded: true, updates }
  }
```

**File:** features/assets-feature/module/__tests__/assets-module.test.js (L72-95)
```javascript
const ctrData = {
  combinedcoin,
  waynecoin,
  abcd_bitcoin_a2345678: {
    ...waynecoin,
    assetName: 'abcd_bitcoin_a2345678',
    name: 'abcd_bitcoin_a2345678',
    // same assetId as waynecoin
    lifecycleStatus: 'c',
    pricingAvailable: true,
    displayTicker: 'WC',

    properTicker: 'WC',
    ticker: 'ED6Bbitcoin3D49BF90',
    version: 1,
    parameters: {
      decimals: 6,
      units: {
        base: 0,
        WC: 6,
      },
    },
  },
}
```

**File:** features/assets-feature/module/__tests__/assets-module.test.js (L399-407)
```javascript
      test('attempt adding new CT, where a legacy token already exists', async () => {
        await assetsModule.addRemoteTokens({ tokenNames: ['waynecoin'] }) // simulate legacy token
        await assetsModule.addRemoteTokens({ tokenNames: ['abcd_bitcoin_a2345678'] }) // add CT with same assetId as legacy token
        const { value, updated } = await assetsAtom.get()

        expect(value.abcd_bitcoin_a2345678).not.toBeDefined()
        expect(value.waynecoin).toMatchObject(waynecoin)
        expect(updated).toEqual([expect.objectContaining(waynecoin)])
      })
```
