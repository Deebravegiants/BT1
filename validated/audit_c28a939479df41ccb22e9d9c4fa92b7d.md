### Title
`encryptedStorage.unlock()` is a one-shot `pDefer` resolver, causing WALLET_INFO storage to remain permanently keyed to the first wallet's seed after `wallet.clear()` + re-import - ([File: libraries/browser-extension-adapters/encrypted-storage/encrypted-storage.js])

### Summary
`createEncryptedStorage` wires its `unlock` method directly to a `pDefer().resolve`, and `@exodus/storage-encrypted` only ever awaits that promise once via `cryptoFunctionsPromise.then(...)`, caching the resolved `{ encrypt, decrypt }` pair for the lifetime of the storage instance. Because native JS Promises can only be resolved once, any `unlock()` call after the first is silently ignored, so encrypt/decrypt closures bound to the *first* seed's `seedId` (captured in `createUnlockEncryptedStorage`) remain in effect even after the wallet is cleared and a new one is imported and unlocked in the same process.

### Finding Description
- `createEncryptedStorage` (`libraries/browser-extension-adapters/encrypted-storage/encrypted-storage.js:5-22`) does `const { promise, resolve } = pDefer()` and exposes `unlock: resolve`. [1](#0-0) 
- `createStorageEncrypted` in `adapters/storage-encrypted/src/storage.ts:29-33` does `const cryptoFunctions = cryptoFunctionsPromise.then((functions) => {...})`, i.e. it derives a single, permanently memoized promise from `cryptoFunctionsPromise`. All subsequent reads/writes (`transformOnRead`/`transformOnWrite`) `await cryptoFunctions`, which resolves once and forever to whatever value the *first* `resolve()` call provided. [2](#0-1) 
- `createUnlockEncryptedStorage` (`sdks/headless/src/unlock-encrypted-storage.js:12-21`) captures `seedId = await wallet.getPrimarySeedId()` at call time and builds new encrypt/decrypt closures bound to that `seedId`, then calls `encryptedStorage.unlock({ encrypt, decrypt })`. [3](#0-2) 
- This unlock function is invoked on every `application.hook('unlock', ...)` (`sdks/headless/src/index.js:153-160`), i.e. every time `application.unlock()` runs - including after `wallet.clear()` + `wallet.import({ mnemonic: otherMnemonic })` + a second `unlock()` in the same process. [4](#0-3) 
- Because `pDefer`'s `resolve` is a no-op after the first resolution, the second `unlockEncryptedStorage(storage)` call - now carrying the new wallet's `seedId` - has **no effect** on the already-resolved `cryptoFunctionsPromise`. The `encryptedStorage` (`adapters.storage` in the headless SDK, i.e. the WALLET_INFO storage) keeps using the encrypt/decrypt closures bound to the **first** seed forever, for the remaining life of the process.
- The adapter/storage instance is not necessarily recreated across a clear+import+restart cycle within one process: `sdks/headless/__tests__/clear.test.js` explicitly reuses the same `adapters` object (and therefore the same `storage`/`migrateableStorage` `encryptedStorage` instances created once via `createEncryptedStorage(unsafeStorage)` in `sdks/headless/__tests__/adapters/index.js:52,59`) across a delete/restart cycle, only swapping the `port`. [5](#0-4) [6](#0-5) 
- No guard exists anywhere in `wallet.clear()` (`features/wallet/module/wallet.js:261-272`) or in the `onClear`/`onUnlock` hook wiring to reset/recreate `encryptedStorage`'s underlying `pDefer` or to detect that a second `unlock()` call must actually re-key the storage. [7](#0-6) 

### Impact Explanation
After `wallet.clear()` + `wallet.import({ mnemonic: otherMnemonic })` + `application.unlock()`, all subsequent `encryptedStorage.get/set/batchGet/batchSet` calls for the WALLET_INFO namespace continue to invoke `cachedSodiumEncryptor.encryptSecretBox`/`decryptSecretBox` with the **first** wallet's `seedId`, not the newly imported wallet's `seedId`. This causes state authenticity failure across wallet identity changes: WALLET_INFO for wallet B is silently encrypted/decrypted under wallet A's key, causing either silent decryption failures (data loss/corruption for wallet B, swallowed by `swallowDecryptionErrors: true`) or, worse, actual cross-wallet data confusion if any residual ciphertext from wallet A is read back under wallet B's session. This is a genuine wallet/state-integrity bug matching "cross-wallet key/state confusion" impact.

### Likelihood Explanation
This requires only ordinary, unprivileged, in-process API usage supported by the SDK: `wallet.clear()`, `wallet.import()`, and `application.unlock()` invoked twice within the same running process/background instance - a normal "delete wallet, import a different one" flow that does not necessarily force a full process restart with fresh adapters (as demonstrated by `sdks/headless/__tests__/clear.test.js` reusing the same `adapters.storage` instance across a restart cycle). This is straightforward to reproduce deterministically every time the flow occurs, with no external attacker action needed beyond triggering the standard wallet lifecycle sequence.

### Recommendation
Do not rely on a single-shot `pDefer` for `encryptedStorage.unlock()`. Instead:
- Recreate the `pDefer`/`cryptoFunctionsPromise` (and thus the underlying `createStorageEncrypted` instance) whenever the primary seed identity changes (on `wallet.clear()` and again on the next `unlock()`), or
- Change `createEncryptedStorage`'s `unlock` to replace the resolved crypto functions on each call (e.g., using a mutable ref/atom that `transformOnRead`/`transformOnWrite` read live from, instead of memoizing `cryptoFunctionsPromise.then(...)` once), ensuring the latest `seedId`-bound encrypt/decrypt pair is always used.
- Add an explicit `onClear` hook that resets/recreates the encrypted storage's crypto binding so that a new `unlock()` after `wallet.clear()` actually re-keys storage.

### Proof of Concept
Integration test (extending `sdks/headless/__tests__/encrypted-storage.test.js`):
```js
test('encryptedStorage should re-key after clear + reimport + unlock', async () => {
  const mnemonicA = 'menu memory fury language physical wonder dog valid smart edge decrease worth'
  const mnemonicB = 'legal winner thank year wave sausage worth useful legal winner thank yellow'

  await exodus.application.import({ passphrase, mnemonic: mnemonicA })
  await exodus.application.unlock({ passphrase })
  const seedIdA = await exodus.wallet.getPrimarySeedId()

  await adapters.storage.set('key', 'value-for-A')

  await exodus.wallet.clear()
  await exodus.application.import({ passphrase, mnemonic: mnemonicB })
  await exodus.application.unlock({ passphrase })
  const seedIdB = await exodus.wallet.getPrimarySeedId()

  // Spy on cachedSodiumEncryptor to capture actual seedId used for WALLET_INFO ops
  const encryptSpy = jest.spyOn(cachedSodiumEncryptor, 'encryptSecretBox')
  await adapters.storage.set('key2', 'value-for-B')

  // Expected (fixed) behavior: encryptSpy called with { seedId: seedIdB }
  // Actual (vulnerable) behavior: encryptSpy called with { seedId: seedIdA }
  expect(encryptSpy).toHaveBeenCalledWith(
    expect.objectContaining({ seedId: seedIdB })
  )
})
```
Expected failing assertion on current code: `encryptSpy` is called with `seedId: seedIdA` (the stale, first-imported wallet's seed) instead of `seedIdB`, proving the WALLET_INFO storage never re-keyed after the wallet identity changed.

### Citations

**File:** libraries/browser-extension-adapters/encrypted-storage/encrypted-storage.js (L5-22)
```javascript
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

**File:** adapters/storage-encrypted/src/storage.ts (L29-46)
```typescript
  const cryptoFunctions = cryptoFunctionsPromise.then((functions) => {
    assert(typeof functions.encrypt === 'function', 'encrypt not a function')
    assert(typeof functions.decrypt === 'function', 'decrypt not a function')
    return functions
  })

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

**File:** sdks/headless/src/index.js (L153-160)
```javascript
    application.hook('unlock', async () => {
      if (typeof storage.unlock === 'function') unlockEncryptedStorage(storage)

      // normally unlocked during migrations, also unlock here just in case
      if (typeof migrateableStorage.unlock === 'function') {
        unlockEncryptedStorage(migrateableStorage)
      }
    })
```

**File:** sdks/headless/__tests__/adapters/index.js (L47-67)
```javascript
  return {
    assetPlugins: createAssetPlugins(),
    createLogger,
    legacyPrivToPub: createLegacyPrivToPub(),
    unsafeStorage,
    storage: createEncryptedStorage(unsafeStorage),
    fusion: createFusion({ channelData: overrides.channelData }),
    fetch: createFetch(),
    fetchival,
    freeze: createFreeze(),
    env: createEnv(),
    getBuildMetadata: createGetBuildMetadata(),
    migrateableStorage: createEncryptedStorage(unsafeStorage),
    iconsStorage: createIconsStorage(),
    customTokensStorage: createCustomTokensStorage(),
    port: new Emitter(),
    synchronizedTime: SynchronizedTime,
    ...multiProcessAdapters,
    ...singleProcessAdapters,
    ...overrides,
  }
```

**File:** features/wallet/module/wallet.js (L261-272)
```javascript
  clear = async () => {
    this.lock()

    // Avoid using this.walletStorage.clear as it's not implemented in mobile
    await Promise.all([
      this.walletStorage.delete(SEED_KEY),
      this.walletStorage.delete(EXTRA_SEEDS_KEY),
      this.walletStorage.delete(GENERATED_PASSPHRASE_KEY),
      this.walletStorage.delete(HAS_USER_SET_PASSPHRASE_KEY),
      this.#seedMetadataAtom.set(undefined),
    ])
  }
```
