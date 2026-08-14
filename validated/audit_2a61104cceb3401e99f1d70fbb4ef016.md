### Title
Encrypted values in `@exodus/storage-encrypted` are not cryptographically bound to their storage key, enabling ciphertext-swapping between wallet storage items - (File: `adapters/storage-encrypted/src/storage.ts`)

### Summary
`@exodus/storage-encrypted`, used by the browser-extension adapters and the headless SDK to encrypt wallet data at rest (e.g. `chrome.storage.local`), encrypts and decrypts values without binding the ciphertext to the storage key (item name) it is stored under. This mirrors the reported bug class: like the Uniswap extension's encrypted mnemonics/private keys that were not bound to their public-address context, values here are encrypted/decrypted independent of which storage "slot" they occupy, so ciphertexts can be swapped between storage items and will decrypt "successfully" into the wrong logical value.

### Finding Description
`createStorageEncrypted` builds a `transformStorage` wrapper whose `onRead`/`onWrite` hooks perform the actual encrypt/decrypt calls: [1](#0-0) 

Note that `transformOnRead` receives the storage `key` as a parameter (used only for logging), but never passes it to `decrypt()`, and `transformOnWrite` never includes the destination key when calling `encrypt()`. The `encrypt`/`decrypt` functions themselves (injected via `cryptoFunctionsPromise`) are typically bound only to a `seedId`/`keyId` pair, e.g.: [2](#0-1) 

and at the crypto layer, `encryptSecretBox`/`decryptSecretBox` use `nacl.secretbox`-style encryption with a random nonce and no additional authenticated data tying the ciphertext to anything other than the derived secret key: [3](#0-2) 

Because a single `encrypt`/`decrypt` pair is shared across every item written into a given encrypted-storage namespace, any two items encrypted under the same `seedId`/`keyId` are interchangeable ciphertexts as far as decryption is concerned — the storage layer does not verify that a decrypted value actually "belongs" to the key it was read from. This exactly matches the root cause described in the report: "Encrypted content is not cryptographically bound to the relevant public address" — here, "relevant storage key."

This encrypted-storage primitive backs the browser-extension adapter used to persist data in `chrome.storage.local`: [4](#0-3) 

### Impact Explanation
An attacker who can write to the underlying unsafe storage (e.g., via a compromised renderer/content-script with access to `chrome.storage.local`, analogous to the Trail of Bits exploit scenario) can swap the ciphertext values stored under two different keys in the encrypted-storage namespace. On next read, the extension will silently decrypt and use the wrong logical value for a given storage key, without any integrity check that the decrypted content actually corresponds to that key's expected context. Depending on what is stored in this namespace (wallet metadata, account configuration, etc., keyed by `EXODUS_KEY_IDS.WALLET_INFO`), this could cause the wallet to associate the wrong data with a given key/account, similar in spirit to the original wrong-address signing scenario, though I could not fully confirm from available code whether raw private keys/mnemonics (as opposed to wallet metadata) are ever persisted through this exact `storage-encrypted` path — mnemonics appear to instead go through `secure-container`/`seco-storage`, which I could not fully audit for the same binding property within the available context.

### Likelihood Explanation
The primary prerequisite is write access to the underlying, unencrypted storage layer (`chrome.storage.local` or the `unsafeStorage`/in-memory equivalent), which is the same "content script/renderer compromise" threat model explicitly used in the original report and permitted by the analog rules for encrypted-storage trust boundaries. Given that access, the swap requires no cryptographic breaking — it is a straightforward transposition of two ciphertext blobs.

### Recommendation
- Include the storage key (item name/context identifier) as additional authenticated data (AAD) when calling `encrypt`/`decrypt` in `transformOnWrite`/`transformOnRead` (`adapters/storage-encrypted/src/storage.ts`), so ciphertexts fail to decrypt (or fail an integrity check) if moved to a different storage key.
- Alternatively, after decryption, validate that the decrypted payload's embedded identifier (if any) matches the storage key it was read from.
- Audit all downstream consumers of `@exodus/storage-encrypted` (headless SDK, browser-extension adapters) to confirm whether sensitive per-account secrets are ever stored through this path, and apply the same context-binding principle everywhere encrypted blobs are keyed by an external identifier.

### Proof of Concept
1. Two items, `key-A` and `key-B`, are written to an encrypted-storage instance unlocked with the same `encrypt`/`decrypt` pair (e.g. via `unlockEncryptedStorageDefinition`), each holding distinct JSON payloads.
2. An attacker with write access to the underlying unsafe storage (e.g. `chrome.storage.local`) swaps the base64 ciphertext strings stored under `key-A` and `key-B` (see `transformOnWrite`/`transformOnRead` in `adapters/storage-encrypted/src/storage.ts`, which do not bind key to ciphertext).
3. When the application subsequently calls `storage.get('key-A')`, `transformOnRead` decrypts the swapped ciphertext successfully (same shared key, no AAD, no post-decryption validation) and returns the payload originally written under `key-B`, and vice versa — demonstrating that ciphertexts are not bound to their storage-key context.

### Citations

**File:** adapters/storage-encrypted/src/storage.ts (L35-62)
```typescript
  const transformOnWrite = async (value: unknown) => {
    if (value === undefined) return

    const { encrypt } = await cryptoFunctions
    const wrapped = JSON.stringify(value)
    const ciphertext = await encrypt(Buffer.from(wrapped))
    return ciphertext.toString('base64')
  }

  const transformOnRead = async (ciphertextB64: string | undefined, key: string) => {
    const { decrypt } = await cryptoFunctions
    if (!ciphertextB64) return

    const ciphertext = Buffer.from(ciphertextB64, 'base64')
    let decrypted
    try {
      decrypted = await decrypt(ciphertext)
    } catch (err) {
      if (swallowDecryptionErrors && isDecryptionError(err as Error)) {
        logger.warn(`Failed to decrypt value for key: ${key}`, err)
        return
      }

      throw err
    }

    return JSON.parse(decrypted.toString())
  }
```

**File:** sdks/headless/src/unlock-encrypted-storage.js (L12-21)
```javascript
const createUnlockEncryptedStorage = ({ cachedSodiumEncryptor, wallet }) => {
  return async (encryptedStorage) => {
    const seedId = await wallet.getPrimarySeedId()
    const keyId = EXODUS_KEY_IDS.WALLET_INFO

    await encryptedStorage.unlock({
      encrypt: (data) => cachedSodiumEncryptor.encryptSecretBox({ data, seedId, keyId }),
      decrypt: (data) => cachedSodiumEncryptor.decryptSecretBox({ data, seedId, keyId }),
    })
  }
```

**File:** features/keychain/module/crypto/sodium.js (L63-70)
```javascript
    encryptSecretBox: async ({ seedId, keyId, data }) => {
      const { privateKey: sodiumSeed } = getPrivateHDKey({ seedId, keyId })
      return sodium.encryptSecret(data, sodiumSeed)
    },
    decryptSecretBox: async ({ seedId, keyId, data }) => {
      const { privateKey: sodiumSeed } = getPrivateHDKey({ seedId, keyId })
      return sodium.decryptSecret(data, sodiumSeed)
    },
```

**File:** libraries/browser-extension-adapters/encrypted-storage/encrypted-storage.js (L1-22)
```javascript
import createStorageEncrypted from '@exodus/storage-encrypted'
import assert from 'minimalistic-assert'
import pDefer from 'p-defer'

const createEncryptedStorage = ({
  unsafeStorage,
  swallowDecryptionErrors = true,
  logger = console,
}) => {
  assert(unsafeStorage, `missing storage`)

  const { promise, resolve } = pDefer()

  const instance = createStorageEncrypted({
    storage: unsafeStorage,
    cryptoFunctionsPromise: promise,
    swallowDecryptionErrors,
    logger,
  })

  return { ...instance, unlock: resolve }
}
```
