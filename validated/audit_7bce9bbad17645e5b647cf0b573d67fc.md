### Title
`Wallet.updateSeed` mutates persisted `seedMetadata` storage without checking the wallet-lock invariant enforced by sibling methods - ([File: features/wallet/module/wallet.js])

### Summary
`Wallet.updateSeed` (`features/wallet/module/wallet.js:199-211`) never calls `#assertWalletIsUnlocked`, unlike `addSeed` (`features/wallet/module/wallet.js:137-138`) and `removeManySeeds` (`features/wallet/module/wallet.js:173-175`). Any caller with access to the public `wallet.updateSeed` API (exposed verbatim in `features/wallet/api/index.js:12`) can therefore write to `seedMetadataAtom`'s persisted `seedMetadata` storage entry while the wallet is locked and no seed material has been loaded into the keychain.

### Finding Description
`updateSeed` only validates that `seedId` and `label` are truthy, then unconditionally performs `this.#seedMetadataAtom.set(...)`: [1](#0-0) 
Compare this to `addSeed`, which calls `await this.#assertWalletIsUnlocked()` as its very first statement before touching any storage: [2](#0-1) 
and `removeManySeeds`, which does the same: [3](#0-2) 
`#assertWalletIsUnlocked` simply checks the in-memory `#isLocked` flag: [4](#0-3) 
`updateSeed` is exposed on the public SDK API surface identically to `addSeed`/`removeSeed`: [5](#0-4) 
There is also no check that `seedId` refers to an existing seed (primary or extra) — the spread `...previous[seedId]` on an undefined key simply produces `{ label, dateUpdated }` for an arbitrary attacker-supplied `seedId`, so a caller can inject metadata entries for seed IDs that don't even exist in the wallet.

### Impact Explanation
Because `updateSeed` bypasses the lock check that every other mutating wallet method enforces, an unprivileged caller with access to the `wallet` API (e.g., an embedding dapp/SDK consumer) can write/overwrite entries in the persisted `seedMetadata` storage (label, `dateUpdated`, and arbitrary keys for non-existent `seedId`s) while the wallet is locked and no passphrase/unlock has occurred. This is a genuine violation of the "no wallet-state mutation while locked" invariant that the module otherwise enforces consistently. However, the mutation is confined to non-secret metadata (labels, timestamps) — no mnemonic, seed, or private key material is read, disclosed, or signed, and no keychain/signing state is touched. It does not grant unauthorized signing, secret disclosure, account/origin bypass, or privilege persistence over key material; the practical effect is metadata corruption/spoofing (e.g., renaming seeds, injecting bogus metadata records) rather than fund or key compromise.

### Likelihood Explanation
Trivially reproducible: any caller that can invoke `wallet.updateSeed({ seedId, label })` — the same trust boundary that already allows calling `wallet.create`/`wallet.getSeedMetadata` — can trigger this while `isLocked() === true`, with no passphrase, unlock, or privileged state required.

### Recommendation
Add `await this.#assertWalletIsUnlocked()` as the first statement in `updateSeed`, mirroring `addSeed` and `removeManySeeds`, and additionally validate that `seedId` corresponds to an existing primary or extra seed before mutating `seedMetadataAtom`.

### Proof of Concept
Integration test added to `features/wallet/module/__tests__/index.test.js`:
```js
it('does not allow updating seed metadata while wallet is locked', async () => {
  await wallet.create()
  // wallet.create() leaves the wallet locked (see existing test 'wallet is still locked after create()')
  await expect(wallet.isLocked()).resolves.toEqual(true)

  await expect(
    wallet.updateSeed({ seedId: 'arbitrary-or-nonexistent-seed-id', label: 'Attacker Label' })
  ).rejects.toThrow(/locked/)

  // Confirms no metadata was injected/mutated while locked
  const metadata = await seedMetadataAtom.get()
  expect(metadata).not.toHaveProperty('arbitrary-or-nonexistent-seed-id')
})
```
Expected current (buggy) behavior: the call resolves without throwing and `seedMetadataAtom` contains the injected `arbitrary-or-nonexistent-seed-id` entry, proving the lock-bypass invariant break. Expected behavior after fix: the call rejects with `'wallet is locked'` and storage remains unchanged.

### Citations

**File:** features/wallet/module/wallet.js (L61-64)
```javascript
  #assertWalletIsUnlocked = async () => {
    const isLocked = await this.isLocked()
    assert(!isLocked, 'wallet is locked')
  }
```

**File:** features/wallet/module/wallet.js (L137-138)
```javascript
  addSeed = async ({ mnemonic, label, compatibilityMode }) => {
    await this.#assertWalletIsUnlocked()
```

**File:** features/wallet/module/wallet.js (L173-175)
```javascript
  removeManySeeds = async (seedIds) => {
    this.#assertMultiSeedSupport()
    await this.#assertWalletIsUnlocked()
```

**File:** features/wallet/module/wallet.js (L199-211)
```javascript
  updateSeed = async ({ seedId, label }) => {
    assert(seedId, 'missing seedId to update seed metadata')
    assert(label, 'missing label to update seed metadata')

    await this.#seedMetadataAtom.set((previous) => ({
      ...previous,
      [seedId]: {
        ...previous[seedId],
        label,
        dateUpdated: this.#clock.now(),
      },
    }))
  }
```

**File:** features/wallet/api/index.js (L1-23)
```javascript
const createWalletApi = ({ wallet }) => {
  return {
    wallet: {
      exists: wallet.exists,
      hasPassphraseSet: wallet.hasPassphraseSet,
      isLocked: wallet.isLocked,
      getMnemonic: wallet.getMnemonic,
      getSeedMetadata: wallet.getSeedMetadata,
      getPrimarySeedId: wallet.getPrimarySeedId,
      getExtraSeedIds: wallet.getExtraSeedIds,
      addSeed: wallet.addSeed,
      updateSeed: wallet.updateSeed,
      removeManySeeds: wallet.removeManySeeds,
      removeSeed: wallet.removeSeed,
      create: wallet.create,
      import: wallet.import,
      clear: wallet.clear,
      lock: wallet.lock,
      unlock: wallet.unlock,
      changePassphrase: wallet.changePassphrase,
    },
  }
}
```
