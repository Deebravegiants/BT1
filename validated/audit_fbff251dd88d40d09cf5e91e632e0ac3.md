### Title
`wallet.updateSeed` accepts arbitrary/forged `seedId` with no ownership check and no lock check, allowing seed-metadata injection - (File: `features/wallet/module/wallet.js`)

### Finding Description
`updateSeed` only asserts that `seedId` and `label` are truthy strings, then unconditionally merges an entry into `#seedMetadataAtom` keyed by that `seedId`: [1](#0-0) 

Compare this with sibling mutators on the same atom:
- `addSeed` calls `#assertWalletIsUnlocked()` before writing metadata and derives `seedId` itself from a verified seed (`getSeedId(seed)`), so the key is always a real, owned seed. [2](#0-1) 
- `removeManySeeds`/`removeSeed` also call `#assertWalletIsUnlocked()` before touching metadata. [3](#0-2) 

`updateSeed` has neither guard: no `#assertWalletIsUnlocked()` call, and no check that `seedId` exists in `#primarySeedIdAtom` / `#getExtraSeeds()` / current `#seedMetadataAtom` keys before writing. Because the atom write is `{...previous, [seedId]: {...previous[seedId], label, dateUpdated}}`, when `seedId` is unknown, `previous[seedId]` is `undefined`, so a brand-new metadata object `{ label, dateUpdated }` (no `dateCreated`) is silently created for that foreign/forged id.

`updateSeed` is exposed directly on the public wallet RPC/API surface with no additional wrapping: [4](#0-3)  and the module itself is declared `public: true` [5](#0-4) , so any caller with access to the wallet API (e.g. dapp/RPC caller) can invoke `wallet.updateSeed({seedId, label})` regardless of `isLocked()` state and regardless of whether `seedId` corresponds to any seed the wallet actually manages.

### Impact Explanation
An attacker-controlled call can inject arbitrary entries into `seedMetadataAtom` for ids that do not correspond to any real seed, or overwrite label/`dateUpdated` fields on existing seed metadata, even while the wallet is locked. Since `getSeedMetadata()`/`seedMetadataAtom` is read elsewhere (e.g., account-listing UI, label display) this can corrupt UI display (spoofed labels/account entries) and pollute persisted metadata state with entries unrelated to any actual owned seed. It does not expose secrets, does not enable signing, and does not bypass authentication for spending/export operations — impact is limited to metadata integrity/UI-display corruption, not fund loss or key disclosure.

### Likelihood Explanation
Fully reachable by any unprivileged caller with access to the `wallet` API surface — no unlock, no passphrase, and no ownership proof of `seedId` are required, since `updateSeed` performs no `#assertWalletIsUnlocked()` check and no membership check against known seed ids. This is trivially and repeatably triggerable with a single RPC call.

### Recommendation
In `updateSeed`, add `await this.#assertWalletIsUnlocked()` (matching `addSeed`/`removeManySeeds`) and validate that `seedId` already exists among known seed ids (primary seed id or `#getExtraSeeds()`/current `#seedMetadataAtom` keys) before merging, rejecting with an error (e.g., `'No seed matches seedId.'`) otherwise so metadata can only be updated for seeds the wallet actually owns.

### Proof of Concept
Unit test additions to `features/wallet/module/__tests__/index.test.js`:
```js
it('rejects updateSeed for a seedId that does not correspond to any owned seed', async () => {
  await wallet.create()
  await wallet.unlock()

  await expect(
    wallet.updateSeed({ seedId: 'nonexistent-or-foreign-id', label: 'malicious' })
  ).rejects.toThrow(/no seed matches/i)

  const metadata = await seedMetadataAtom.get()
  expect(metadata).not.toHaveProperty('nonexistent-or-foreign-id')
})

it('rejects updateSeed while wallet is locked', async () => {
  await wallet.create() // still locked after create()

  await expect(
    wallet.updateSeed({ seedId: 'any-id', label: 'malicious' })
  ).rejects.toThrow(/locked/i)
})
```
Expected current behavior (proving the bug): both calls resolve without throwing and the metadata atom ends up containing the forged `seedId` entry — demonstrating unauthenticated metadata injection.

### Citations

**File:** features/wallet/module/wallet.js (L137-165)
```javascript
  addSeed = async ({ mnemonic, label, compatibilityMode }) => {
    await this.#assertWalletIsUnlocked()

    const seed = await mnemonicToSeed({ mnemonic, format: 'buffer', validate: false })
    const seedId = await getSeedId(seed)
    if (seedId === (await this.#primarySeedIdAtom.get())) {
      throw new Error('Seed already present')
    }

    const dateCreated = this.#clock.now()
    const data = { mnemonic, seed, dateCreated, compatibilityMode }
    const seeds = await this.#getExtraSeeds()
    if (seeds.length >= this.#maxExtraSeeds) {
      throw new Error('Maximum number of seeds reached')
    }

    if (seeds.some((seed) => seed.mnemonic === mnemonic)) {
      throw new Error('Seed already present')
    }

    seeds.push(data)
    await this.#setExtraSeeds(seeds)
    await this.#seedMetadataAtom.set((previous) => ({
      ...previous,
      [seedId]: { dateCreated, label, compatibilityMode },
    }))

    return this.#keychain.addSeed(data.seed)
  }
```

**File:** features/wallet/module/wallet.js (L173-197)
```javascript
  removeManySeeds = async (seedIds) => {
    this.#assertMultiSeedSupport()
    await this.#assertWalletIsUnlocked()

    const primarySeedId = await this.#primarySeedIdAtom.get()
    if (seedIds.includes(primarySeedId)) {
      throw new Error('Cannot remove primary seed')
    }

    const extraSeeds = await this.#getExtraSeeds()
    const extraSeedsIds = new Map(
      await Promise.all(extraSeeds.map(async (seed) => [seed, await getSeedId(seed.seed)]))
    )

    const remainingSeeds = extraSeeds.filter((seed) => !seedIds.includes(extraSeedsIds.get(seed)))
    const seedsToRemove = extraSeeds.filter((seed) => seedIds.includes(extraSeedsIds.get(seed)))

    await this.#setExtraSeeds(remainingSeeds)
    this.#removeManySeedsMetadata(seedIds)
    await this.#keychain.removeSeeds(seedsToRemove.map((seed) => seed.seed))
  }

  removeSeed = (seedId) => {
    return this.removeManySeeds([seedId])
  }
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

**File:** features/wallet/module/wallet.js (L357-372)
```javascript
const walletDefinition = {
  id: 'wallet',
  type: 'module',
  factory: createWallet,
  dependencies: [
    'keychain',
    'primarySeedIdAtom',
    'seedStorage',
    'unsafeStorage',
    'config',
    'logger',
    'seedMetadataAtom',
    'clock?',
  ],
  public: true,
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
