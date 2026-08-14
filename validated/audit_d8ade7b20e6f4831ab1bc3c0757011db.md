### Title
Silent Multi-Chain Scope Escalation for Already-Trusted Origins - ([File: features/connected-origins/module/connections.js])

### Summary
The `ConnectedOrigins.add()` method allows an already-trusted dapp origin to silently expand the set of chains (`assetNames`) it has access to, without any new user confirmation, echoing the exact bug class described in the external report (uncontrolled multi-chain access expansion without informed user consent).

### Finding Description
When a dapp origin is already trusted, `add()` merges any new `assetNames` supplied by the caller into the existing connection's `assetNames` and persists it via `#setAttributes`, without requiring re-approval or any user-facing confirmation step: [1](#0-0) 

The only state carried over/validated is the boolean `trusted` flag; once an origin is trusted for one asset (e.g. Solana), any subsequent `add()` call — even with `trusted` unset — silently grows `assetNames` (e.g. Solana → Ethereum → Optimism) and the connection is treated as fully trusted for all of them: [2](#0-1) 

This is directly reflected in tests demonstrating that a second `add()` call with different/expanded `assetNames` on an already-trusted origin succeeds without any additional confirmation gate: [3](#0-2) [4](#0-3) 

Once assets/chains are added to `assetNames`, `getConnectedAccounts()` exposes addresses for every asset in that list to the origin — again gated only by the single `isTrusted` boolean, not per-chain consent: [5](#0-4) 

The project's own documentation confirms there is no per-chain confirmation step even for active network switches at the provider layer, describing the wallet as intentionally "stateless" with switches not prompting user confirmation: [6](#0-5) 

Combined, these two facts mean: (1) chain/network switching is explicitly by design not confirmed per EIP-3326 handling, and (2) the underlying trust-and-asset-exposure primitive (`connectedOrigins.add`) allows scope escalation (adding new `assetNames`/chains) to a previously-approved origin without a fresh user prompt, which is functionally identical to the reported ShapeShift Snap issue: a connected origin can gain exposure to additional chain-specific address/account data without a distinct approval event recorded for that new chain.

### Impact Explanation
An origin that was approved for access to one chain (e.g. Solana only) can be silently expanded — by a call from the background/API layer using attacker-controlled or dapp-supplied `assetNames` parameters — to also receive addresses for Ethereum, Optimism, or any other supported chain, all under the umbrella of the original single trust decision. This violates the principle of least privilege and can facilitate phishing/address-disclosure risk: a dapp could present itself as needing only one chain's data, get approved, and later obtain addresses/accounts for unrelated chains without the user ever being shown a distinct chain-scope confirmation.

### Likelihood Explanation
I could not verify from the indexed code which specific caller(s) in the RPC bridge invoke `connectedOrigins.add` with dapp/website-controlled `assetNames`/`origin` values (the `apps/*/background/exodus.ts` wiring and web3-provider RPC handlers that call into this API were not fully retrievable via the index — the `add` call sites outside of tests were not found). Without seeing exactly how `origin` and `assetNames` are sourced from the RPC boundary (whether from `sender` metadata verified by the extension host, vs. values passed by the dapp itself), I cannot confirm this is remotely triggerable purely by an untrusted webpage rather than only by first-party UI code following an actual user approval flow.

### Recommendation
Require a distinct, chain-scoped confirmation whenever `assetNames` is expanded for an existing trusted origin in `ConnectedOrigins.add()`, rather than silently merging new asset names into an already-trusted connection. Track per-chain approval state (not just a single `trusted` boolean) and gate `getConnectedAccounts()` per-asset accordingly.

### Proof of Concept
Given the code in `features/connected-origins/module/connections.js`, the following sequence (mirrored by the existing test suite) demonstrates silent scope escalation:
```js
await connectedOrigins.add({ origin: 'dapp.example', connectedAssetName: 'solana', assetNames: ['solana'], trusted: true })
// user approved solana-only access

await connectedOrigins.add({ origin: 'dapp.example', assetNames: ['solana', 'ethereum', 'optimism'] })
// no `trusted` re-confirmation, yet ethereum/optimism addresses become accessible via getConnectedAccounts()
``` [4](#0-3) 

**Note on limitations:** Due to the size limits of the codebase index, I was unable to locate the exact caller(s) that invoke `connectedOrigins.add` from the web3-provider RPC handling paths (e.g., inside `apps/*/background/exodus.ts` or a shared ethereum/solana provider RPC module) to confirm whether `assetNames`/`origin` parameters are fully attacker-controlled or are constrained by extension-level sender validation. I recommend starting a full Devin session with complete repository access to trace the exact RPC call sites feeding into `connectedOrigins.add`/`updateConnection` to conclusively establish exploitability from an untrusted connected dapp.

### Citations

**File:** features/connected-origins/module/connections.js (L140-173)
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

**File:** features/connected-origins/module/__tests__/connections.test.js (L129-158)
```javascript
  test('updates accounts when new assets added', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      assetNames: ['solana'],
      trusted: true,
    })

    await connectedOrigins.add({
      origin: 'exodus.com',
      assetNames: ['solana', 'ethereum'],
    })

    await expect(connectedAccountsAtom.get()).resolves.toEqual({
      exodus_0: {
        addresses: {
          ethereum: '0xbf41610c6D5e6E1DF97f37249D118Cc6FC47d407',
          solana: 'ASwcbiBuegaMrNUuXeN5WDYKoRuDXxMRt5DdStjvdSro',
        },
      },
      exodus_1: {
        addresses: {
          ethereum: '0x1Dc234Aa1c77e3AA781BB2DdF2099489053E11B2',
          solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1',
        },
      },
    })
  })
```

**File:** features/connected-origins/module/__tests__/connections.test.js (L302-327)
```javascript
  test('add new origin with additional assetNames', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'ethereum',
      assetNames: ['ethereum', 'solana', 'optimism'],
    })
    const origins = await connectedOriginsAtom.get()

    expect(origins).toHaveLength(1)
    expect(origins[0]).toMatchObject({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      favorite: false,
      autoApprove: false,
      connectedAssetName: 'ethereum',
      assetNames: ['ethereum', 'solana', 'optimism'],
      activeConnections: [],
    })

    const stored = await connectedOriginsAtom.get()

    expect(stored).toHaveLength(1)
  })
```

**File:** docs/web3-providers/ethereum-rpc-api.md (L43-58)
```markdown
### `wallet_switchEthereumChain`

:::tip Standard

This method is specified by [EIP-3326](https://eips.ethereum.org/EIPS/eip-3326).

:::

Switches to the chain with the specified chain ID.

Unlike other wallets like MetaMask, Exodus is stateless. This means that there
is no concept of "active chain" at the wallet level. When a web3 site requests
switching the chain, the change only affects that site. Switching to a different
chain does not prompt the user for confirmation. Instead, the "active chain"
(from the web3 site's point of view) is displayed when asking for approval when
signing transactions or messages.
```
