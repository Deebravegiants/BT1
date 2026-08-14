### Title
`PublicKeyProvider#exportPublic` derives and returns key material for a wallet account without verifying that `keyIdentifier`'s encoded account index matches `walletAccount.index` - ([File: features/public-key-provider/module/public-key-provider.ts])

### Summary
`PublicKeyProvider#exportPublic` (called by `getPublicKey`/`getExtendedPublicKey`) resolves `walletAccount` purely by name to fetch `walletAccount.seedId`, then blindly passes the caller-supplied `keyIdentifier` to `keychain.exportKey({ keyId: keyIdentifier, seedId: walletAccount.seedId })` with no check that the `keyIdentifier`'s derivation path/account index actually corresponds to `walletAccount.index`. Because software (`exodus`/`seed`) wallet accounts sharing the same `seedId` differ only by the account index embedded in the BIP32/44 derivation path, a caller that supplies a `keyIdentifier` whose account index does not match the named `walletAccount` will still receive valid key material for the *other* account, labeled and cached under the requested account name.

### Finding Description
In [1](#0-0)  `#exportPublic` looks up `walletAccount` only by name/existence: [2](#0-1) 
and then, for software accounts, exports the key using only `walletAccount.seedId` combined with the raw `keyIdentifier` passed in by the caller: [3](#0-2) 
There is no assertion anywhere in this function (nor in `keychain.exportKey`/`#getPrivateHDKey` in `features/keychain/module/keychain.js`) that the `accountIndex`/derivation path encoded in `keyIdentifier` is consistent with `walletAccount.index`. `keychain.exportKey` only validates `seedId` type and that the seed is known/unlocked; it derives whatever path is given: [4](#0-3) .

The public API layer (`features/public-key-provider/api/index.ts`) exposes a bypass path where, if the caller supplies an explicit `keyIdentifier` (instead of `assetName`), the trusted `getKeyIdentifier()` derivation (which pins `accountIndex: walletAccount.index!`) is skipped entirely and the raw params are forwarded directly to `publicKeyProvider.getPublicKey`: [5](#0-4) 
This is the exact API documented for external/dapp consumption (`exodus.publicKeyProvider.getPublicKey`) per the README's dev-console example passing `walletAccount` and a raw `keyIdentifier` together: [6](#0-5) 

For `exodus_*`/`seed` wallet accounts, multiple accounts share the same `seedId` and differ only by the account index in the derivation path [7](#0-6) . Therefore calling `getPublicKey({ walletAccount: 'exodus_0', keyIdentifier: <path with accountIndex 1> })` resolves `seedId` for `exodus_0` but derives and returns the public key for account index 1 under that seed — key material for an account never named/consented to by the caller. The result is also cached via `publicKeyStore.add({ walletAccount, keyIdentifier, publicKey, xpub })`, persisting the mismatched association [8](#0-7) .

### Impact Explanation
This breaks wallet-account isolation: a caller that is only supposed to operate on one named wallet account (e.g. `exodus_0`) can obtain the public key/xpub of an arbitrary other account index under the same seed simply by crafting a `keyIdentifier` with a different account index, without any explicit ownership/consistency check. Exposure of an unintended account's xpub/public key is an information-disclosure/account-isolation violation (address/balance linkage across accounts, xpub-derived address enumeration for an account the caller had no right to query).

### Likelihood Explanation
Exploitability requires only the ability to call `publicKeyProvider.getPublicKey`/`getExtendedPublicKey` with a `keyIdentifier` object — which the API layer permits directly (`'keyIdentifier' in params` bypass) and which the README documents as a normal, directly-invocable dev/console API. No lock bypass, no privileged state, and no additional guard is required beyond knowing/guessing a valid derivation path template for another account index, which is fully deterministic and predictable from asset BIP44 rules. This makes the issue trivial to reproduce whenever a `keyIdentifier` is attacker-influenced while `walletAccount` name/seedId is trusted.

### Recommendation
In `PublicKeyProvider#exportPublic`, after resolving `walletAccount`, validate that the account index encoded in `keyIdentifier.derivationPath` (or an explicit `keyIdentifier.accountIndex` field, if present in `@exodus/key-identifier`) matches `walletAccount.index` before calling `keychain.exportKey`. Reject the request (throw) on mismatch instead of silently deriving and returning the other account's key. Also consider removing the API-layer bypass that allows passing raw `keyIdentifier` alongside a `walletAccount` string without re-deriving/verifying it from `walletAccount.index`.

### Proof of Concept
Unit test in `features/public-key-provider/module/__tests__/public-key-provider.test.ts` style:
```ts
it('does not return key material for a different account index than walletAccount', async () => {
  // Setup: walletAccounts atom has 'exodus_0' (index: 0, seedId: SEED) and no explicit 'exodus_1' entry consented to by caller
  const keyIdentifierForAccountIndex1 = new KeyIdentifier({
    derivationAlgorithm: 'BIP32',
    keyType: 'secp256k1',
    derivationPath: "m/44'/60'/1'/0/0", // account index 1, NOT 0
  })

  await expect(
    publicKeyProvider.getPublicKey({
      walletAccount: 'exodus_0',
      keyIdentifier: keyIdentifierForAccountIndex1,
    })
  ).rejects.toThrow(/account.*mismatch/i) // EXPECTED after fix; currently resolves successfully with account-1 key material
})
```
Expected (post-fix) assertion: the call throws/rejects due to account-index mismatch instead of silently returning `keychain.exportKey({ keyId: keyIdentifierForAccountIndex1, seedId: walletAccounts['exodus_0'].seedId })`'s result as if it belonged to `exodus_0`.

### Citations

**File:** features/public-key-provider/module/public-key-provider.ts (L112-158)
```typescript
  #exportPublic = async ({
    walletAccount: walletAccountName,
    keyIdentifier,
  }: GetPublicKeyParams): Promise<PublicKeys> => {
    assert(walletAccountName, 'Missing required param "walletAccount"')
    assert(keyIdentifier, 'Missing required param "keyIdentifier"')

    // backwards compat for callers that today pass a WalletAccount instance
    if (typeof walletAccountName !== 'string') {
      this.#logger.warn('expected walletAccount to be a string', walletAccountName)
      walletAccountName = (<WalletAccount>walletAccountName).toString()
    }

    const walletAccounts = await this.#walletAccountsAtom.get()
    const walletAccount = walletAccounts[walletAccountName]
    assert(walletAccount, `Wallet account with name ${walletAccountName} does not exist`)

    // Ensure key identifier is of the right type and frozen
    keyIdentifier = new KeyIdentifier(keyIdentifier)

    const buildMetadata = await this.#getBuildMetadata()

    if (buildMetadata.dev || walletAccount.isHardware) {
      const cached = await this.#getCachedPublicKey({
        keyIdentifier,
        walletAccountName,
      })
      if (cached) {
        return cached
      }
    }

    if (walletAccount.isSoftware) {
      const { publicKey, xpub } = await this.#keychain.exportKey({
        keyId: keyIdentifier,
        seedId: walletAccount.seedId,
      })

      // Don't wait to avoid extra latency
      void this.#publicKeyStore.add({
        walletAccount,
        keyIdentifier,
        publicKey,
        xpub,
      })
      return { publicKey, xpub }
    }
```

**File:** features/keychain/module/keychain.js (L271-299)
```javascript
  async exportKey({ seedId, keyId, exportPrivate, exportPublic = true }) {
    assert(typeof seedId === 'string', 'seedId must be a string')

    if (exportPrivate) {
      this.#assertPrivateKeysUnlocked([seedId])
    }

    keyId = new KeyIdentifier(keyId)

    const hdkey = this.#getPrivateHDKey({
      seedId,
      keyId,
      getPrivateHDKeySymbol: this.#getPrivateHDKeySymbol,
    })
    const privateKey = hdkey.privateKey
    let publicKey = null

    if (exportPublic) {
      publicKey = await this.#getPublicKeyFromHDKey({ hdkey, keyId })
    }

    const { xpriv, xpub } = hdkey.toJSON()
    return {
      xpub: exportPublic ? xpub : null,
      xpriv: exportPrivate ? xpriv : null,
      publicKey,
      privateKey: exportPrivate ? privateKey : null,
    }
  }
```

**File:** features/public-key-provider/api/index.ts (L84-95)
```typescript
  return {
    publicKeyProvider: {
      async getPublicKey(params: GetKeyParams) {
        if ('keyIdentifier' in params) {
          return publicKeyProvider.getPublicKey(params)
        }

        return publicKeyProvider.getPublicKey({
          keyIdentifier: await getKeyIdentifier(params),
          walletAccount: params.walletAccount,
        })
      },
```

**File:** features/public-key-provider/README.md (L29-38)
```markdown
```js
await exodus.publicKeyProvider.getPublicKey({
  walletAccount: 'exodus_0',
  keyIdentifier: {
    derivationAlgorithm: 'BIP32',
    derivationPath: "m/44'/0'/0'/0/0",
    keyType: 'secp256k1',
  },
})
```
```

**File:** libraries/models/src/wallet-account/index.ts (L112-122)
```typescript
  source: WalletAccountSource
  index: number | null
  id?: string | number
  label: string
  model?: string
  lastConnected?: number
  is2FA?: boolean
  color?: string
  icon?: string
  enabled: boolean
  seedId?: string
```
