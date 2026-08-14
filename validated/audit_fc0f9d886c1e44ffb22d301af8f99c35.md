### Title
`autoApprove` and asset trust state in `ConnectedOrigins` are scoped only by `origin`, not by asset/chain, allowing approval bleed to newly connected assets - (File: `features/connected-origins/module/connections.js`)

### Summary
`ConnectedOrigins` stores a single `autoApprove` boolean and a single `trusted` boolean per `origin`, together with an ever-growing `assetNames` list for that origin, but none of the "is this action allowed" checks (`isTrusted`, `isAutoApprove`) are scoped to which specific asset/chain the approval was originally granted for. This mirrors the `PaladinRewardReserve.approvedSpenders` bug class: a boolean/approval mapping keyed only by an actor (spender / origin) while the "target" of the approval (token / asset) is allowed to be silently changed underneath it via functions that take the target as an arbitrary argument (`transferToken(token, ...)` / `add({ connectedAssetName, assetNames, ... })`).

### Finding Description
`ConnectedOrigins#add` looks up the existing origin entry and, if found, unions the previously stored `assetNames` with any newly supplied `connectedAssetName`/`assetNames`, then calls `#setAttributes` to persist the merged list while leaving `trusted` and `autoApprove` untouched (defaulting to the previous values): [1](#0-0) 

The `trusted`/`autoApprove` flags themselves are stored and read purely by `origin` string, with no binding to which asset(s) the user actually reviewed and approved when they first trusted/auto-approved the origin: [2](#0-1) 

Because `add()` can be called again for an already-trusted, already-auto-approved `origin` with a *new* `connectedAssetName` (e.g. a dApp that first connects on Solana, gets trusted and set to auto-approve, later requests connection/approval for Ethereum on the same `origin`), the new asset is folded into `assetNames` for that origin while `autoApprove`/`trusted` remain `true` from the original grant. `updateConnection` similarly allows swapping `connectedAssetName` for an existing trusted origin without touching `autoApprove`: [3](#0-2) 

This is structurally identical to the reported bug: `approvedSpenders[spender] = true` was set for TokenA, and because the mapping/approval state doesn't record which "target" (token there, asset/chain here) it was scoped to, and the functions that mutate the target (`transferToken(token,...)` there, `add(connectedAssetName,...)` here) accept that target as an arbitrary parameter, a party who already holds "spender"/"auto-approve" status can silently extend it to a new target without the corresponding review step being re-run.

### Impact Explanation
If any UI/RPC surface consuming `connectedOrigins.isAutoApprove({ origin })` (exposed verbatim via `features/connected-origins/api/index.js`) uses that boolean to skip a user confirmation prompt for signing/connection requests, then a dApp origin that earned auto-approval for one chain/asset can obtain silent auto-approval for a completely different asset/chain simply by calling `add`/`updateConnection` with a new `connectedAssetName`, without the user ever explicitly approving auto-signing for that asset. This is a cross-asset privilege bleed within the origin/account trust boundary the module is meant to enforce, potentially leading to unauthorized transaction signing/exposure of accounts on an asset the user never intended to auto-approve.

### Likelihood Explanation
Likelihood is moderate: it requires a dApp (already trusted on one asset) to later request connection for an additional asset on the same origin, which is a normal multi-chain dApp UX flow, not an attacker-only edge case. No additional privileged access is required — any origin already connected can trigger `add` again with a different `connectedAssetName`.

### Recommendation
Scope `trusted` and `autoApprove` (and ideally the whole connection record) per `(origin, assetName)` pair rather than per `origin` alone — mirroring recommendation (2) from the source report (make the approval mapping/keying include the target, e.g. `approved[origin][asset]`). Concretely:
- Store `autoApprove`/`trusted` inside a map keyed by asset within the origin record, or key the whole `connectedOriginsAtom` entries by `(origin, assetName)`.
- When `add()`/`updateConnection()` introduces a new `connectedAssetName`/`assetNames` entry that wasn't previously part of the origin's approved set, reset `autoApprove` to `false` for that new asset and require an explicit re-approval, instead of inheriting the origin-level flag.

### Proof of Concept
1. dApp `https://example.com` connects requesting `connectedAssetName: 'solana'`; user trusts it and later enables `setAutoApprove({ origin: 'https://example.com', value: true })`.
2. Later, `connectedOrigins.add({ origin: 'https://example.com', connectedAssetName: 'ethereum' })` is called (e.g., the dApp adds Ethereum support and calls a "connect" flow again). [4](#0-3) 
3. `assetNames` for the origin now includes `'ethereum'`, but `trusted`/`autoApprove` remain `true` from the original Solana-only grant — see `isTrusted`/`isAutoApprove` reading only origin-level flags: [5](#0-4) 
4. Any subsequent Ethereum signing/connection request from `https://example.com` is now auto-approved even though the user never explicitly consented to auto-approval for Ethereum.

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

**File:** features/connected-origins/module/connections.js (L198-216)
```javascript
  isTrusted = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) {
      return false
    }

    // backward compatibility
    return value.trusted === undefined || value.trusted
  }

  isAutoApprove = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })
    return value?.autoApprove || false
  }

  setAutoApprove = async ({ origin, value }) => {
    return this.#setAttributes({ origin, attributes: { autoApprove: value } })
  }
```

**File:** features/connected-origins/module/connections.js (L275-291)
```javascript
  updateConnection = async ({ origin, icon, connectedAssetName }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const attributes = {}

    if (icon) {
      attributes.icon = icon
    }

    if (connectedAssetName) {
      attributes.connectedAssetName = connectedAssetName
    }

    await this.#setAttributes({ origin, attributes })
  }
```
