### Title
Origin's `walletAccount` binding can be silently rebound to a different wallet account on repeat `add()` calls without new consent - (File: features/connected-origins/module/connections.js)

### Summary
The `add()` method's update path merges a caller-supplied `walletAccount` into an already-trusted origin's record using `walletAccount: walletAccount ?? value.walletAccount`, with no check that the new value matches the value present at the time `trusted` was first granted. This allows a second `add()` call for an already-trusted origin to overwrite the bound `walletAccount` field, effectively transferring the origin's `trusted`/`autoApprove` privileges to a different wallet account without a fresh consent flow.

### Finding Description
`add()` at [1](#0-0)  first loads the existing record via `#getOrigin` and, when a record already exists (`value` truthy), calls `#setAttributes` merging fields including:

```
walletAccount: walletAccount ?? value.walletAccount,
``` [2](#0-1) 

Critically, `trusted: trusted ?? value.trusted` preserves the existing trust flag when the caller omits `trusted` on the follow-up call, while `walletAccount` is independently taken from the caller's input when provided. This means a caller can send `add({ origin, walletAccount: 'B' })` (omitting `trusted`) against an origin that is already trusted with `walletAccount: 'A'`, and the merge logic will retain `trusted: true` from the stored value while overwriting `walletAccount` to `'B'`. `#setAttributes` performs an unconditional object spread merge (`{ ...connection, ...attributes }`) with no validation that `walletAccount` is unchanged or that trust boundaries are respected [3](#0-2) .

Downstream consumers `isAutoApprove` and `getConnectedAccounts` read directly from this mutated record: `isAutoApprove` returns `value?.autoApprove` [4](#0-3) , and any autoApprove/trust state associated with the origin now applies with the rebindable `walletAccount` value stored in the same record, with no re-verification against the account bound at the time trust/autoApprove was granted.

There is no code in this file that pins `walletAccount` immutably once `trusted` becomes `true`, nor any requirement that changing `walletAccount` re-run a consent/approval flow. The existing test suite only verifies that repeated `add()` calls don't duplicate origin entries (`'not trust again trusted origin'` test) [5](#0-4) , and does not assert that `walletAccount` is immutable after initial trust grant — confirming no invariant test currently guards this behavior.

### Impact Explanation
If an already-trusted origin's `walletAccount` field can be silently changed by a follow-up `add()` call, any trust or `autoApprove` privilege previously granted for wallet account A becomes applicable to wallet account B without the user re-approving that specific account. This is a privilege-persistence / wrong-account-binding issue: trust granted for one account is transferred to a different account via caller-supplied input rather than fresh user consent, matching a wrong-account-access impact class.

### Likelihood Explanation
The precondition is simply that an origin has already been trusted once (a normal, expected state for any dapp a user has connected to). The exploit requires only a second `add()` call with a different `walletAccount` value and no `trusted` field (relying on `trusted ?? value.trusted` to preserve prior trust while `walletAccount` is overwritten). This is straightforward and repeatable using only the module's public `add()` method — no privileged state, keys, or social engineering are required. Whether this method is reachable directly from an untrusted dapp's RPC/messaging surface (vs. gated behind a wallet-UI approval step upstream) could not be conclusively traced from the available index; the module is registered as `public: true` and is exercised directly from `sdks/headless/__tests__/connected-origins.test.js`, suggesting it is part of an externally-callable module surface, but the exact upstream caller/gating code between a dapp RPC request and this `add()` invocation was not found in the indexed context.

### Recommendation
In `add()`, when updating an already-trusted origin (`value.trusted` is true) and a `walletAccount` is supplied that differs from `value.walletAccount`, require the caller to go through an explicit re-consent/approval step (e.g., reset `trusted`/`autoApprove` to `false` and require a fresh trust grant) rather than silently merging the new `walletAccount` into the existing trusted record. At minimum, once `trusted: true`, `walletAccount` should not be mutable via `add()` without simultaneously requiring `trusted`/`autoApprove` to be explicitly re-affirmed by the caller.

### Proof of Concept
```js
test('walletAccount rebinding after trust grant requires re-consent', async () => {
  await connectedOrigins.add({
    origin: 'exodus.com',
    name: 'Exodus',
    connectedAssetName: 'solana',
    trusted: true,
    walletAccount: 'exodus_0',
  })
  await connectedOrigins.setAutoApprove({ origin: 'exodus.com', value: true })

  // Second call from the same "origin" caller, no explicit trusted flag, different walletAccount
  await connectedOrigins.add({
    origin: 'exodus.com',
    walletAccount: 'exodus_1',
  })

  const origins = await connectedOriginsAtom.get()
  const record = origins.find((o) => o.origin === 'exodus.com')

  // Expected (secure) behavior: walletAccount binding unchanged, or trust/autoApprove reset
  expect(record.walletAccount).toBe('exodus_0')
  // OR, if rebinding is intentionally supported, autoApprove/trusted must be revoked:
  // expect(record.trusted).toBe(false)
  // expect(await connectedOrigins.isAutoApprove({ origin: 'exodus.com' })).toBe(false)
})
```
This test currently fails against the code as written (`record.walletAccount` becomes `'exodus_1'` while `trusted`/`autoApprove` remain unchanged), demonstrating the silent rebinding.

### Citations

**File:** features/connected-origins/module/connections.js (L51-64)
```javascript
  #setAttributes = async ({ origin, attributes }) => {
    const item = await this.#getOrigin({ origin })

    if (!item) return

    const data = await this.#getData()

    const newData = data.map((connection) => {
      if (origin !== connection.origin) return connection
      return { ...connection, ...attributes }
    })

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

**File:** features/connected-origins/module/connections.js (L209-212)
```javascript
  isAutoApprove = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })
    return value?.autoApprove || false
  }
```

**File:** features/connected-origins/module/__tests__/connections.test.js (L329-347)
```javascript
  test('not trust again trusted origin', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      trusted: true,
    })
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      trusted: true,
    })

    const origins = await connectedOriginsAtom.get()
    expect(origins).toHaveLength(1)
  })
```
