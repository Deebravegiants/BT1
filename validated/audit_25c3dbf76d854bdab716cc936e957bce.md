### Title
`keyViewer.getEncodedPrivateKeys` exposes raw private keys via the public SDK API with no gating beyond the wallet-unlock lock state - ([File: features/key-viewer/module/key-viewer.ts])

### Summary
The `TurboSafe.gib` bug lets a privileged role move all funds out of a vault unconditionally, with no rate-limit or collateral check — the only real protection is a governance timelock external to the contract. The closest analog in this repository is `KeyViewer.getEncodedPrivateKeys`, which lets any caller with access to the exposed SDK/RPC surface extract a wallet account's raw private key in cleartext, with the only gate being the keychain's global lock/unlock flag — not per-call user confirmation, scoping, or origin/account isolation.

### Finding Description
`KeyViewer.getEncodedPrivateKeys` takes just a `baseAssetName` and `walletAccount` name, derives the default key path, and calls `keychain.exportKey({ seedId, keyId, exportPrivate: true })` to return the fully decoded private key material to the caller: [1](#0-0) 

This method is wired directly into the public `keyViewerApi` with no additional authorization, confirmation, or origin check layered on top — it is a thin pass-through: [2](#0-1) 

The only protection preventing arbitrary extraction is the keychain's coarse-grained, wallet-wide lock state, enforced in `#assertPrivateKeysUnlocked`/`exportKey`: [3](#0-2) [4](#0-3) 

This mirrors the `gib` pattern: a single function call performs a complete, unconditional extraction of sensitive value (there, all vault assets; here, the raw private key/seed material) once the caller is deemed "privileged" (there, `requiresLocalOrMasterAuth`; here, merely "wallet unlocked"). There is no scoping by requesting origin/dApp, no user-facing confirmation prompt gating this specific call the way transaction signing flows typically require approval, and no limiting of what can be extracted (full private key + xpriv, not just a signature) — the SDK README explicitly documents this as directly callable from the Dev Tools console once the wallet is unlocked: [5](#0-4) 

### Impact Explanation
If this API is reachable from any less-trusted context (e.g., a compromised or malicious UI/renderer, a webview, or any RPC-connected caller once the wallet SDK is unlocked), it grants complete, irreversible compromise of the affected wallet account — direct disclosure of the raw private key allows draining of funds independent of any subsequent transaction-approval UI, exactly analogous to `gib`'s unconditional fund removal. The keychain README itself flags this as a known architectural gap: "Private keys _can_ be exported, via `keychain.exportKey`" and that key material is passed to third-party asset code. [6](#0-5) 

### Likelihood Explanation
Likelihood depends on whether an untrusted caller (malicious webpage/dApp, compromised UI thread, or RPC bridge client) can reach the `keyViewer` namespace of the exposed SDK API without additional user confirmation, similar to how `gib` requires a privileged role. Since the `keyViewerApi` factory does not add any per-call authorization/confirmation and simply forwards to the module method, any code path that can call into the exposed `exodus.keyViewer` API (once the wallet is unlocked) can obtain private keys — unlike transaction-signing flows, which typically show an approval prompt per the web3-provider docs.

### Recommendation
Add an explicit, mandatory user-confirmation/authorization step immediately before `getEncodedPrivateKeys` executes (not just "wallet unlocked"), scope the API to trusted/first-party callers only, and consider excluding it from any RPC/webview-exposed surface that untrusted origins can reach. Log/alert on invocation, and consider requiring a fresh, explicit re-authentication (e.g., PIN/biometric) tied to that specific call rather than relying on the shared global lock state.

### Proof of Concept
1. Unlock the wallet (satisfies `#assertPrivateKeysUnlocked`).
2. From any context that can call the exposed `exodus.keyViewer` API (the README documents this working directly from the Dev Tools console), call:
```js
await exodus.keyViewer.getEncodedPrivateKeys({ walletAccount: 'exodus_0', baseAssetName: 'bitcoin' })
``` [5](#0-4) 
3. The raw private key is returned in cleartext with no further confirmation step, as traced through `getEncodedPrivateKeys` → `keychain.exportKey`: [7](#0-6)

### Citations

**File:** features/key-viewer/module/key-viewer.ts (L52-97)
```typescript
  getEncodedPrivateKeys = async ({
    baseAssetName,
    walletAccount: walletAccountName,
  }: GetEncodedPrivateKeyParams): GetEncodedPrivateKeyReturnValue => {
    const walletAccounts = await this.#walletAccountsAtom.get()
    const walletAccount = walletAccounts[walletAccountName]

    assert(walletAccount, `Wallet account ${walletAccountName} does not exist`)
    assert(
      walletAccount.isSoftware,
      `can only view encoded private key of software wallet accounts, got ${walletAccountName}`
    )

    const asset = this.#assetsModule.getAsset(baseAssetName)
    const purpose = await this.#assetSources.getDefaultPurpose({
      assetName: baseAssetName,
      walletAccount: walletAccountName,
    })
    const { chainIndex, addressIndex } = getDefaultPathIndexes({
      asset,
      walletAccount,
      compatibilityMode: walletAccount.compatibilityMode,
    })

    const keyId = new KeyIdentifier(
      asset.api.getKeyIdentifier({
        purpose,
        accountIndex: walletAccount.index,
        chainIndex,
        addressIndex,
        compatibilityMode: walletAccount.compatibilityMode,
      })
    )

    const keyExport = this.#keychain.exportKey({
      seedId: walletAccount.seedId!,
      keyId,
      exportPrivate: true,
    })

    const addressExport = this.#addressProvider.getDefaultAddress({
      walletAccount,
      assetName: baseAssetName,
    })

    const [{ privateKey }, address] = await Promise.all([keyExport, addressExport])
```

**File:** features/key-viewer/api/index.ts (L10-21)
```typescript
const createKeyViewerApi = ({ keyViewer, logger }: Dependencies) => ({
  keyViewer: {
    async getEncodedPrivateKey(...args: Parameters<KeyViewer['getEncodedPrivateKeys']>) {
      logger.warn(
        'keyViewer.getEncodedPrivateKey is deprecated, use keyViewer.getEncodedPrivateKeys instead'
      )
      const [{ privateKey }] = await keyViewer.getEncodedPrivateKeys(...args)

      return privateKey
    },
    getEncodedPrivateKeys: keyViewer.getEncodedPrivateKeys,
  },
```

**File:** features/keychain/module/keychain.js (L57-60)
```javascript
  #assertPrivateKeysUnlocked(seedIds) {
    const locked = this.#checkPrivateKeysLocked(seedIds)
    assert(!locked, 'private keys are locked')
  }
```

**File:** features/keychain/module/keychain.js (L271-285)
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
```

**File:** features/key-viewer/README.md (L17-19)
```markdown
1. Open the playground https://exodus-hydra.pages.dev/features/key-viewer
2. Try out the some methods via the UI. These corresponds 1:1 with the `exodus.keyViewer` API.
3. Run `await exodus.keyViewer.getEncodedPrivateKeys({ walletAccount: 'exodus_0', baseAssetName: 'bitcoin' })` in the Dev Tools Console.
```

**File:** features/keychain/README.md (L5-9)
```markdown
In its current state, this library aims to provide a good interface for working with cryptographic material. However, it has some security limitations, which are on our roadmap to address:

- Private key material is passed directly to asset libraries which can contain code by third party developers. This is on our roadmap to eliminate by refactoring asset libraries to accept signing functions instead of keys.
- Private keys _can_ be exported, via `keychain.exportKey`
- `keychain.removeAllSeeds()` does not guarantee that private keys get completely cleared from memory
```
