## Analysis

The Axelar report describes a class of bug where a **trust boundary that is supposed to be scoped to one context (a specific chain) can be silently widened through a secondary registration path that doesn't re-validate against the original authorization**, letting an attacker escalate access beyond what was originally approved.

The closest reachable analog in this codebase is in the **connected-origins** trust store, which governs which third-party websites (dApps) are authorized to access wallet addresses/accounts, in `features/connected-origins/module/connections.js`.

### Root cause

`ConnectedOrigins.add()` is the single entry point used both for the *initial* trust grant (typically gated by a user-approval popup, per `docs/web3-providers/solana-provider-api.md`) and for *subsequent* updates to an already-connected origin (e.g., reconnecting, switching assets, "eagerly connecting" with `onlyIfTrusted`). [1](#0-0) 

When `value` (the existing origin record) is truthy, the code merges the new `assetNames` into the origin's asset scope, but the `trusted` flag is preserved from the pre-existing record if the caller does not explicitly override it:

```js
trusted: trusted ?? value.trusted,
assetNames: [...allConnectedAssetNames],
```

This means an origin that is already `trusted: true` (approved once for asset A) can have its `assetNames` scope silently expanded to include asset B via a later, lower-friction `add()` call (e.g. a reconnect/eager-connect flow) — without the flag ever going through a fresh, asset-specific consent decision. Once `assetNames` includes the new asset, `getConnectedAccounts()` exposes addresses for that asset to the origin purely based on the pre-existing `trusted` bit: [2](#0-1) 

### Why this matters

This is structurally the same bug pattern as the Axelar finding: a **secondary, less-scrutinized channel (a follow-up `add()`/reconnect call) is used to expand what a previously-authorized-but-narrowly-scoped party can access**, because the code re-uses a coarse trust flag (`trusted`) instead of validating the specific new grant (the new `assetName`) against user consent. In the ITS analog, "deploy token manager from a different chain" bypassed the original chain-scoped balance tracking; here, "add with new assetNames for an already-connected origin" bypasses the original per-asset consent scope by inheriting the origin-level `trusted` bit.

However, I want to flag an important caveat before finalizing: I could not find, within indexed content, the actual dapp-provider/background-script call sites that invoke `connectedOrigins.add()` on `connect()`/reconnect (e.g. solana/ethereum provider plugin code), so I cannot confirm from this index whether the UI layer requires a fresh approval popup for the *specific* asset each time, or if it truly relies solely on `trusted`/`isTrusted` as shown here. The wiki/index coverage for provider plugin implementation directories appears to be excluded. If you need to confirm the exact caller behavior (whether it re-prompts per-asset), a Devin session with full repo access to `features/*/plugin` and provider background modules would be necessary to trace the call sites precisely.

Given this, I can present the finding but with reduced confidence on exploitability, since it depends on code I could not directly inspect.

### Title
Silent Cross-Asset Trust Scope Expansion via `ConnectedOrigins.add()` - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins#add` merges new `assetNames` into an already-trusted origin's record while defaulting `trusted` to the origin's pre-existing value (`trusted ?? value.trusted`) rather than requiring a fresh, asset-scoped approval, allowing the origin's data access to expand from the asset(s) it was actually approved for to any asset later included in a subsequent `add()` call.

### Finding Description
`add()` at [1](#0-0)  computes `allConnectedAssetNames` as the union of the newly requested `connectedAssetName`/`assetNames` and the origin's previously stored `assetNames`, then persists this union along with `trusted: trusted ?? value.trusted`. Because `trusted` is inherited when not explicitly passed, any code path that calls `add()` again for an already-trusted origin (reconnect, eager connect, asset-switch flows) can extend the `assetNames` array that `getConnectedAccounts()` later uses to expose addresses, at [2](#0-1) , without the underlying `trusted` boolean ever being re-derived from a fresh, asset-specific user decision.

### Impact Explanation
If any caller (background/provider plugin) invokes `add()` on behalf of a dApp without gating the specific new `assetName` behind its own approval UI (relying instead on the origin's overall `trusted` state), a previously-approved dApp for e.g. `ethereum` could gain silent access to the user's `solana`/other chain addresses via `getConnectedAccounts()`, which is an account-isolation/privilege-bleed issue across asset scopes.

### Likelihood Explanation
Likelihood depends entirely on the provider/background call sites that invoke `connectedOrigins.add()`, which were not available in the indexed content for this repository. If those call sites always pass an explicit `trusted` value tied to a fresh popup approval per asset, this is not exploitable; if any call site reconnects/adds assets using the stored/default `trusted` value, it is directly exploitable. This uncertainty should be resolved by a full-repository review.

### Recommendation
`add()` should not implicitly widen `assetNames` for an already-trusted origin without an explicit, per-asset consent flag passed by the caller; `trusted` should never default from `value.trusted` when new `assetNames`/`connectedAssetName` are being introduced that weren't part of the original consent.

### Proof of Concept
Not concretely demonstrable from the indexed code alone, since the dApp-facing provider/background call sites that invoke `add()` on reconnect were not found in the index. A full-repo audit of `features/*/plugin` and provider background modules calling `connectedOrigins.add()` is needed to confirm whether reconnection flows ever call `add()` with new `assetNames` while relying on `trusted` inheriting from the stored record.

### Citations

**File:** features/connected-origins/module/connections.js (L140-185)
```javascript
  add = async ({
    connectedAssetName,
    origin,
    name,
    icon,
    assetNames = [],
    trusted,
    favorite,
    walletAccount,
  }) => {
    const value = await this.#getOrigin({ origin })

    const allConnectedAssetNames = new Set([
      connectedAssetName,
      ...assetNames,
      ...(value?.assetNames ?? []),
    ])

    if (value) {
      await this.#setAttributes({
        origin,
        attributes: {
          icon: icon ?? value.icon,
          name: name ?? value.name,
          connectedAssetName: connectedAssetName ?? value.connectedAssetName,
          trusted: trusted ?? value.trusted,
          favorite: favorite ?? value.favorite,
          assetNames: [...allConnectedAssetNames],
          walletAccount: walletAccount ?? value.walletAccount,
        },
      })

      return
    }

    await this.#addNewItem({
      origin,
      icon,
      name,
      connectedAssetName,
      trusted,
      favorite,
      assetNames: [...allConnectedAssetNames],
      walletAccount,
    })
  }
```

**File:** features/connected-origins/module/connections.js (L249-256)
```javascript
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

    const value = await this.#getOrigin({ origin })
    const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(
      (name, index, ary) => Boolean(name) && ary.indexOf(name) === index
    )
```
