## Title
`isTrusted` treats an undefined `trusted` field as trusted, allowing dApp-origin auto-approval bypass - (`features/connected-origins/module/connections.js`)

### Summary
This is a direct structural analog of the PoolTogether bug: a permissive fallback branch silently upgrades an "unset"/zero-like state into a fully-privileged state. In PoolTogether, `_withdrawableAssets == 0` incorrectly caused `_currentExchangeRate()` to return `_assetUnit` (100% collateralized). In this repo, `ConnectedOrigins.isTrusted` treats a missing/`undefined` `trusted` field the same way it treats an explicit `trusted: true`, silently promoting an origin record to "trusted" status.

### Finding Description
`isTrusted` is implemented as: [1](#0-0) 

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

The `trusted` attribute on a connection record is only set explicitly via `add({ trusted: true, ... })`. However `add` accepts `trusted` as an optional, caller-controlled parameter with no default, and when a record already exists, merges `trusted: trusted ?? value.trusted`: [2](#0-1) 

Because `add` (and thus the ability to create an origin entry with `trusted` left `undefined`) is exposed directly on the public `connectedOriginsApi`: [3](#0-2) 

any caller of `connectedOrigins.add` that omits the `trusted` flag (e.g. a connection-request handshake performed before the user has actually approved the connection, or any other legitimate call path that doesn't explicitly pass `trusted: false`) produces a stored record where `value.trusted === undefined`. `isTrusted` then evaluates `value.trusted === undefined || value.trusted` → `true`, incorrectly reporting the origin as trusted.

This mirrors the PoolTogether root cause precisely: instead of treating the "unset"/zero state as *not privileged* (the safe default), the code special-cases it into the *fully privileged* state via an OR-based fallback ("backward compatibility" comment plays the same role as the implicit 1:1 exchange-rate fallback in the original bug).

### Impact Explanation
`isTrusted` directly gates `getConnectedAccounts`, which returns the user's wallet account addresses (across all wallet accounts) for a given origin: [4](#0-3) 

It also gates `untrust`, since `untrust` only proceeds `if (isTrusted)`: [5](#0-4) 

If an origin record can end up with `trusted: undefined` (e.g. due to a caller not passing the flag, a migration path, or any legitimate "pending connection" record created prior to explicit user approval), the origin is treated by the SDK as fully trusted/auto-connectable without the user ever explicitly approving it — a privilege-bleed across the intended origin/consent isolation boundary (analogous to unauthorized cross-origin/account privilege bypass). This can leak wallet account addresses to an unapproved origin and lets that origin bypass the “eager connect” trust check described in the provider docs (`onlyIfTrusted`), which is explicitly designed to only auto-approve *after* user approval: [6](#0-5) 

### Likelihood Explanation
Likelihood depends on whether any code path (current or future) creates/updates a connection record without an explicit `trusted: true|false`. The `add()` API takes `trusted` as an optional parameter with no default value and is exposed on the public `connectedOriginsApi`, so any caller that forgets or intentionally omits `trusted` triggers the fallback. The presence of the "backward compatibility" comment indicates this exact ambiguous state is expected to occur in the wild (e.g. records created before the `trusted` field existed, or partial `add()` calls that only intend to update `assetNames`/`icon`). This makes the bug reachable via realistic legitimate call patterns even without a malicious origin doing anything unusual.

### Recommendation
Change `isTrusted` to default to `false` (deny) rather than `true` (allow) when `trusted` is unset:
```js
return value.trusted === true
```
If backward compatibility with pre-existing records is required, perform an explicit one-time migration that sets `trusted: true` only for records that were created before the flag existed, rather than treating `undefined` as trusted indefinitely at read-time. Additionally, `add()` should require `trusted` to be explicitly provided (or default it to `false`) instead of allowing it to silently pass through as `undefined`.

### Proof of Concept
```js
// Any call to add() that omits `trusted` creates a record with trusted === undefined
await connectedOrigins.add({
  origin: 'malicious.example',
  name: 'Malicious',
  connectedAssetName: 'solana',
  // note: no `trusted` passed
})

// isTrusted() incorrectly reports true due to `value.trusted === undefined || value.trusted`
const trusted = await connectedOrigins.isTrusted({ origin: 'malicious.example' })
console.log(trusted) // true, despite no explicit user approval

// getConnectedAccounts now leaks wallet addresses for this "trusted" origin
const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'malicious.example' })
console.log(accounts) // wallet account addresses exposed
``` [1](#0-0)

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

**File:** features/connected-origins/module/connections.js (L187-196)
```javascript
  untrust = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })

    if (!isTrusted) return

    const data = await this.#getData()
    const newData = data.filter((connection) => connection.origin !== origin)

    await this.#setData(newData)
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

**File:** features/connected-origins/api/index.js (L1-22)
```javascript
const connectedOriginsApi = ({
  connectedOrigins,
  connectedOriginsAtom,
  connectedAccountsAtom,
}) => ({
  connectedOrigins: {
    get: connectedOriginsAtom.get,
    getAccounts: connectedAccountsAtom.get,
    add: connectedOrigins.add,
    clear: connectedOrigins.clear,
    untrust: connectedOrigins.untrust,
    isTrusted: connectedOrigins.isTrusted,
    isAutoApprove: connectedOrigins.isAutoApprove,
    setFavorite: connectedOrigins.setFavorite,
    setAutoApprove: connectedOrigins.setAutoApprove,
    connect: connectedOrigins.connect,
    disconnect: connectedOrigins.disconnect,
    updateConnection: connectedOrigins.updateConnection,
    clearConnections: connectedOrigins.clearConnections,
    getConnectedAccounts: connectedOrigins.getConnectedAccounts,
  },
})
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
