### Title
Origin trust/auto-approve state is not re-validated per wallet account, allowing stale consent to authorize actions on newly active accounts - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins` stores `trusted` and `autoApprove` flags keyed only by `origin`, not by the wallet account that was active when consent was granted [1](#0-0) . Once an origin is marked `trusted`/`autoApprove:true`, `isTrusted()` and `isAutoApprove()` only check the origin's stored flags and never re-validate against the wallet account that is currently active [2](#0-1) .

### Finding Description
This mirrors the reported bug class: a piece of "validity" state (`auctionValidityTime` in the original report; `trusted`/`autoApprove` here) is set once and then implicitly assumed to remain correct forever, without being re-checked or reset when the underlying account context changes.

- `add()`/`#addNewItem()` persist `trusted` for an `origin`, independent of which `walletAccount` was active at connection time [3](#0-2) .
- `getConnectedAccounts()` (usable while the wallet is locked, per its own docstring) determines what a connected origin can see purely from `isTrusted({ origin })`, then returns addresses for *all* enabled wallet accounts, with only the *currently active* account swapped to the front — not limited to the account that originally granted consent [4](#0-3) .
- `isAutoApprove({ origin })` similarly returns a boolean based solely on the origin's stored flag, with no reference to which account is now active [5](#0-4) .
- `updateConnectedAccounts()` only refreshes the account list when the *set* of enabled wallet accounts differs (added/removed), not when the *active* account changes, so trust/auto-approve state silently carries over as the active account switches [6](#0-5) .

Because trust/auto-approve is a property of the origin rather than of the (origin, account) pair, a user who once approves/auto-approves a dApp for one account implicitly extends that same standing authorization to any other account they later make active, with no fresh consent check tied to the new account — the same "stale validity, never re-checked on account state change" root cause as the original report.

### Impact Explanation
If a consuming flow (e.g., signing/connection request handling built on top of `isTrusted`/`isAutoApprove`) relies on these origin-level flags to decide whether to prompt the user, switching the active wallet account (e.g., from a low-value/test account to a primary account) after granting `autoApprove` would let the connected origin obtain addresses for, or silently trigger approval flows against, an account the user never explicitly authorized for that origin. This is a cross-account privilege bleed within the same origin trust boundary.

### Likelihood Explanation
Multi-account use is a core, actively-tested feature (`walletAccounts`, `activeWalletAccountAtom`), and users routinely add/switch accounts after connecting to dApps [7](#0-6) . The auto-approve/trust flags are simple booleans that are never re-scoped or re-prompted when the active account changes, so the stale-authorization condition is easy to trigger through ordinary usage (approve dApp → switch account) rather than requiring an unusual attack setup.

### Recommendation
Scope `trusted`/`autoApprove` (and the accounts exposed via `getConnectedAccounts`) to the specific wallet account(s) that were present/consented-to at connection time, or explicitly re-prompt for consent whenever the active wallet account changes for an already-connected origin. At minimum, `getConnectedAccounts` should not expose or imply approval for accounts that weren't part of the original consent, and `isAutoApprove`/`isTrusted` checks used to bypass user prompts should incorporate the currently active `walletAccount` into the trust decision.

### Proof of Concept
1. User connects Account A (`exodus_0`) to `origin` and sets `autoApprove: true` via `setAutoApprove({ origin, value: true })` [8](#0-7) .
2. User adds/switches to Account B (`exodus_1`) via `activeWalletAccountAtom` (no new interaction with `origin`).
3. `origin` calls into a flow that checks `isAutoApprove({ origin })` — this still returns `true`, and `getConnectedAccounts({ origin })` returns addresses with Account B now listed first as the active account [9](#0-8) , without any new consent having been granted for Account B specifically.

### Citations

**File:** features/connected-origins/module/connections.js (L76-106)
```javascript
  #addNewItem = async ({
    origin,
    name,
    icon,
    connectedAssetName,
    assetNames,
    accounts,
    trusted = false,
    favorite = false,
    walletAccount,
  }) => {
    const newOrigin = {
      origin,
      icon,
      name,
      trusted,
      favorite,
      connectedAssetName,
      assetNames,
      accounts,
      autoApprove: false,
      createdAt: Date.now(),
      activeConnections: [],
      walletAccount,
    }

    const data = await this.#getData()
    const newData = [...data, newOrigin]

    await this.#setData(newData)
  }
```

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

**File:** features/connected-origins/module/connections.js (L245-273)
```javascript
  /**
   * Returns the connected accounts for a given origin with the active wallet account sorted first. Can be used while
   * the wallet is locked
   */
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

**File:** features/connected-origins/module/connections.js (L299-314)
```javascript
  updateConnectedAccounts = async () => {
    const walletAccounts = await this.#enabledWalletAccountsAtom.get()
    const connectedAccounts = await this.#connectedAccountsAtom.get()

    const difference = xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))
    if (difference.length === 0) {
      // up-to-date
      return
    }

    const connectedOrigins = await this.#connectedOriginsAtom.get()
    const assetNames = this.#getConnectedAssets(connectedOrigins)
    const updatedAccounts = await this.#getAccounts(assetNames)

    await this.#connectedAccountsAtom.set(updatedAccounts)
  }
```

**File:** features/connected-origins/module/__tests__/connections.test.js (L160-196)
```javascript
  test('returns connected accounts with active wallet account first', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      assetNames: ['solana'],
      trusted: true,
    })

    await connectedOrigins.add({
      origin: 'wayne.foundation',
      name: 'Wayne Foundation',
      icon: 'exodus_icon',
      connectedAssetName: 'ethereum',
      assetNames: ['ethereum'],
      trusted: true,
    })

    await activeWalletAccountAtom.set('exodus_1')

    const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })
    expect(accounts).toEqual([
      {
        name: 'exodus_1',
        addresses: {
          solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1',
        },
      },
      {
        name: 'exodus_0',
        addresses: {
          solana: 'ASwcbiBuegaMrNUuXeN5WDYKoRuDXxMRt5DdStjvdSro',
        },
      },
    ])
  })
```
