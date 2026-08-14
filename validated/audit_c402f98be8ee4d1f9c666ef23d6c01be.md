## Confirmed test (line 370-375):
```js
test('isTrusted return true for trusted origin', async () => {
  await connectedOriginsAtom.set([{ origin: 'exodus.com' }])
  const result = await connectedOrigins.isTrusted({ origin: 'exodus.com' })
  expect(result).toBe(true)
})
```
This confirms the codebase itself expects/documents that an entry with no `trusted` field is treated as trusted.

### Title
`isTrusted()` treats a missing/undefined `trusted` field as trusted-by-default, allowing an origin record to gain full trust without explicit user approval - (File: `features/connected-origins/module/connections.js`)

### Summary
The pattern in the C4 report — a state field that is *not explicitly initialized* being interpreted as an already-"matured"/privileged value instead of the safe default — has a direct analog in `ConnectedOrigins.isTrusted()`. Instead of a `userGaugeProfitIndex` defaulting to a value that grants unearned rewards, here the `trusted` attribute defaulting to `true` grants unearned dApp trust, exposing account addresses (`getConnectedAccounts`) and enabling the `untrust`/eager-connect/auto-approve web3 provider flow without the user ever explicitly approving that origin.

### Finding Description
`ConnectedOrigins#isTrusted` is defined as: [1](#0-0) 

```js
isTrusted = async ({ origin }) => {
  const value = await this.#getOrigin({ origin })
  if (!value) {
    return false
  }
  // backward compatibility
  return value.trusted === undefined || value.trusted
}
```

Any connected-origin record that lacks an explicit `trusted: false` (i.e. `trusted` is `undefined`) is treated as trusted. This mirrors the `ProfitManager` bug: a check for the "unset" sentinel state (`0`/`undefined`) is interpreted permissively rather than defensively.

`add()` only sets `trusted` when the caller explicitly passes it — when creating a new item, `trusted` defaults to `false` via `#addNewItem`'s parameter default [2](#0-1) , but when *updating* an existing record (`if (value) { ... trusted: trusted ?? value.trusted ... }`) [3](#0-2) , if neither the caller nor the stored `value.trusted` supplies a boolean, `trusted` remains `undefined` in storage, and any subsequent `isTrusted()` call returns `true`.

`isTrusted()` directly gates `getConnectedAccounts()`, which returns wallet addresses for every enabled wallet account to the calling origin without further checks: [4](#0-3) . It also gates `untrust()`.

### Impact Explanation
If an origin record ends up persisted with `trusted: undefined` (e.g., through a partial/legacy `add()` call path, a migration, or any code path that stores a `connectedOrigins` entry without setting the `trusted` boolean), `isTrusted()` silently grants full trust. This causes `getConnectedAccounts()` to disclose the addresses of all enabled wallet accounts to that origin without the explicit "connect approval" popup flow the product documents (see the Solana provider docs describing `connect()`/`onlyIfTrusted` as requiring prior explicit user approval) [5](#0-4) . This is a cross-origin/account privilege bleed: an origin is granted "trusted" status (address disclosure, eager reconnect eligibility) it was never explicitly granted by the user, which the test suite's `isTrusted return true for trusted origin` case for `{ origin: 'exodus.com' }` (no `trusted` field at all) confirms is the actual, intended-by-code behavior rather than an edge case bug — it's a hardcoded design decision labeled "backward compatibility" that fails open.

### Likelihood Explanation
Reachability depends on some code path writing a `connectedOrigins` entry without the `trusted` field/value (e.g., a legacy-stored record loaded from disk before the field existed, or an `add()` call for an already-registered origin where trusted was never set). Because the module's own unit and integration tests explicitly encode "no trusted field ⇒ isTrusted() === true" as expected behavior, this is a real, low-effort-to-trigger condition once any such record exists, but I could not fully confirm within available context whether an attacker-controlled (dApp-triggered) code path can create such an entry as opposed to only legacy/migrated data, since the repository index did not surface the RPC bridge / web3-provider handler code that calls `connectedOrigins.add()` from a page context.

### Recommendation
Change `isTrusted()` to fail closed: treat `trusted !== true` (i.e., default to `false`) rather than treating `undefined` as trusted. If backward compatibility with pre-existing records is required, perform an explicit one-time migration that sets `trusted: true` only for origins that were previously stored under the old trust model (e.g., gated by a schema/version flag), rather than interpreting the ambiguous "unset" state as trusted indefinitely going forward.

### Proof of Concept
```js
// features/connected-origins/module/__tests__/connections.test.js already demonstrates the fail-open behavior:
test('isTrusted return true for trusted origin', async () => {
  await connectedOriginsAtom.set([{ origin: 'exodus.com' }]) // no `trusted` field at all
  const result = await connectedOrigins.isTrusted({ origin: 'exodus.com' })
  expect(result).toBe(true) // <- origin is granted trust despite never being explicitly trusted
})

// Consequence: getConnectedAccounts() will disclose addresses for such an origin:
await connectedOriginsAtom.set([{ origin: 'attacker.example' }])
const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'attacker.example' })
// accounts is populated (not []), because isTrusted() short-circuits to true
```

### Citations

**File:** features/connected-origins/module/connections.js (L76-86)
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
```

**File:** features/connected-origins/module/connections.js (L158-173)
```javascript
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

**File:** features/connected-origins/module/connections.js (L198-207)
```javascript
  isTrusted = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) {
      return false
    }

    // backward compatibility
    return value.trusted === undefined || value.trusted
  }
```

**File:** features/connected-origins/module/connections.js (L249-272)
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
```

**File:** docs/web3-providers/solana-provider-api.md (L80-102)
```markdown
#### Eagerly Connecting

After the user approves a Web3 site's connection to Exodus, the site becomes
trusted. This allows the site to automatically connect to Exodus on subsequent
visits or page refreshes. This is referred to as "eagerly connecting".

If you want to try to eagerly connect, you can pass the `onlyIfTrusted` option
to `connect()`.

```typescript
try {
  await window.exodus.solana.connect({ onlyIfTrusted: true })
} catch (err) {
  // { code: 4001, message: 'User rejected the request.' }
}
```

:::tip

When using this flag, Exodus will only connect if the site is trusted and won't
bother your users with a pop-up if they have not connected to Exodus before.

:::
```
