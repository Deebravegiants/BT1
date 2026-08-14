## Analog Found

### Title
Re-invocable wallet seed initialization (`create`/`import`) permits silent seed overwrite - (File: `features/wallet/module/wallet.js`)

### Summary
The `BkdLocker.initialize()` bug is a class of "initializer without a robust one-time guard" — a function that is supposed to run exactly once but instead relies on a value that can be zero/falsy (or is simply never checked) to decide whether initialization already happened. The closest reachable analog in this repo is `Wallet.create()` / `Wallet.import()` in `features/wallet/module/wallet.js`, which is the function that establishes the primary wallet seed and is expected to be a one-time, foundational operation, but contains no internal guard preventing it from being invoked again to overwrite an already-existing seed.

### Finding Description
`Wallet.create()` unconditionally computes a new/derived mnemonic, sets it via `#setSeed`, and updates `#seedMetadataAtom`, without ever calling `this.exists()` or otherwise checking that a seed is not already present: [1](#0-0) 

`Wallet.import()` similarly only validates the mnemonic format before delegating straight to `create()`: [2](#0-1) 

`exists()` is defined and available as the natural initialization-guard primitive (`!!encryptedSeed`), but it is never consulted inside `create`/`import` itself: [3](#0-2) 

This mirrors the `BkdLocker` root cause exactly: a "should run once" state-setting function omits an internal invariant check, and the only reason multiple invocations don't normally happen is that a different layer (application-level lifecycle orchestration, analogous to "trusted callers only") is assumed to gate the call. In the `BkdLocker` case, that assumption failed because `startBoost=0` bypassed the check; here, whether an analogous bypass exists depends on the `Application.create`/`Application.import` methods in `features/application/src/modules/application.ts`, which are documented to wrap wallet creation/import but whose full implementation (specifically, whether they check `wallet.exists()` before calling `wallet.create/import`) I was not able to fully confirm within the available tool budget — I could only confirm the presence of `create`/`import` methods and `walletExists` references in that file, not their exact guard logic.

### Impact Explanation
If `Application.create`/`Application.import` (or any other caller reachable from an untrusted context, such as a dApp-facing RPC bridge or extension message handler) can invoke `wallet.create`/`wallet.import` after a wallet already exists, the primary seed — the wallet's entire secret-key material — would be silently overwritten with attacker-supplied or attacker-known mnemonic data. That is a direct wallet-compromise / fund-theft primitive: subsequent signing operations would use the substituted seed, and the legitimate seed material could be permanently lost or replaced with a seed known to an attacker.

### Likelihood Explanation
Likelihood is uncertain without confirming the application-layer guard. If `Application.create`/`import` independently check `wallet.exists()` before delegating (which is the expected, idiomatic pattern), this is not exploitable end-to-end and the missing guard in `wallet.js` is defense-in-depth only. If no such check exists at the application layer (or if it can be bypassed, e.g. via the `restoring`/`importing` flags path in `application.ts`'s `start()`), then any caller with access to the SDK/API surface could re-trigger seed creation.

### Recommendation
Add an explicit one-time guard inside `Wallet.create()`/`Wallet.import()` itself (e.g., `assert(!(await this.exists()), 'wallet already exists')`), rather than relying solely on upstream callers to prevent re-initialization — mirroring the C4 recommendation to use a dedicated, unambiguous "already initialized" check rather than an implicit/derived one.

### Proof of Concept
Conceptual PoC (pending confirmation of the application-layer guard):
```js
await wallet.create({ mnemonic: legitimateMnemonic, passphrase })
// wallet now holds the user's real seed
await wallet.create({ mnemonic: attackerMnemonic, passphrase: attackerPassphrase })
// SEED_KEY silently overwritten; wallet now signs with attacker's seed
```

**Caveat:** I was unable to fully verify, within the tool budget, whether `Application.create`/`Application.import` in `features/application/src/modules/application.ts` independently block re-creation via a `walletExists` check before calling into `wallet.create`/`wallet.import`. Confirming that code path (lines around the `create`/`import` methods in that file) would be necessary to determine whether this is concretely reachable by an unprivileged caller or only theoretically possible at the module level.

### Citations

**File:** features/wallet/module/wallet.js (L66-69)
```javascript
  exists = async () => {
    const encryptedSeed = await this.walletStorage.get(SEED_KEY)
    return !!encryptedSeed
  }
```

**File:** features/wallet/module/wallet.js (L231-250)
```javascript
  create = makeConcurrent(
    async ({ mnemonic, passphrase } = {}) => {
      mnemonic = mnemonic || (await generateMnemonic({ bitsize: 128 }))

      const dateCreated = this.#clock.now()
      const seedBuffer = await mnemonicToSeed({ mnemonic, format: 'buffer', validate: false })
      const seed = { mnemonic, seed: seedBuffer, dateCreated }
      const seedId = await getSeedId(seedBuffer)

      await this.#setSeed({ seed, passphrase })

      this.#seedMetadataAtom.set((previous) => ({
        ...previous,
        [seedId]: { dateCreated },
      }))

      return { seedId }
    },
    { concurrency: 1 }
  )
```

**File:** features/wallet/module/wallet.js (L252-259)
```javascript
  import = makeConcurrent(
    async ({ mnemonic, passphrase }) => {
      await assertMnemonic(mnemonic, this.#validMnemonicLengths)

      return this.create({ passphrase, mnemonic })
    },
    { concurrency: 1 }
  )
```
