### Title
Race condition between `Wallet#addSeed` and `Wallet#removeManySeeds` on unsynchronized `extraSeeds` read-modify-write causes lost updates / keychain-storage desync - (File: features/wallet/module/wallet.js)

### Summary
`addSeed` and `removeManySeeds` both perform an unguarded read-modify-write cycle on `walletStorage`'s `extraSeeds` entry via `#getExtraSeeds`/`#setExtraSeeds`, unlike `create`/`import` which are wrapped in `makeConcurrent`. Two overlapping RPC calls (e.g., `addSeed` for seed A racing `removeManySeeds([B])`, or a remove/re-add race on the same seed) can interleave their read and write phases, causing one operation's storage write to be silently overwritten by the other, while each independently still calls `#keychain.addSeed`/`#keychain.removeSeeds`, desynchronizing keychain in-memory key material from persisted `extraSeeds` metadata.

### Finding Description
`addSeed` (features/wallet/module/wallet.js:137-165) does:
```
const seeds = await this.#getExtraSeeds()
...
seeds.push(data)
await this.#setExtraSeeds(seeds)
await this.#seedMetadataAtom.set(...)
return this.#keychain.addSeed(data.seed)
```
`removeManySeeds` (lines 173-193) does:
```
const extraSeeds = await this.#getExtraSeeds()
...
await this.#setExtraSeeds(remainingSeeds)
this.#removeManySeedsMetadata(seedIds)
await this.#keychain.removeSeeds(...)
```
Both `#getExtraSeeds`/`#setExtraSeeds` (lines 213-224) operate directly on `this.walletStorage` with no locking whatsoever, in contrast to `create`/`import` which are explicitly wrapped with `makeConcurrent({ concurrency: 1 })` (lines 231-259) — indicating the authors were aware serialization is required for storage read-modify-write but did not apply it to `addSeed`/`removeManySeeds`.

Because these are `async` functions with multiple `await` points between the read of `extraSeeds` and the write, the JS event loop can interleave two concurrent RPC invocations of these methods (e.g., dapp calling `addSeed` while another call to `removeManySeeds` is in flight, both reachable via the module's public RPC surface since `wallet` module is registered `public: true`). If `removeManySeeds([B])` reads `extraSeeds` (containing A, B) before `addSeed(C)` writes its update, and `addSeed(C)` computes its own `seeds` array (also containing A, B) before `removeManySeeds` writes `remainingSeeds = [A]`, then whichever call's `#setExtraSeeds` executes last overwrites the other's result — e.g. `addSeed` writing `[A, B, C]` after `removeManySeeds` already told the keychain to `removeSeeds([B])`. Net effect: `extraSeeds` storage re-contains seed B's mnemonic/seed bytes even though its key material was removed from keychain (`#keychain.removeSeeds` already executed), or conversely a newly added seed C's metadata is lost from storage while its private key remains loaded in keychain (`#keychain.addSeed(data.seed)` still executes regardless of the storage write's fate, since it's not conditioned on the storage write's outcome).

This breaks the invariant that `extraSeeds` storage and keychain in-memory key state stay consistent, and can also corrupt `#seedMetadataAtom` and keychain accordingly.

### Impact Explanation
This is a lost-update/data-corruption issue in the wallet's persisted `extraSeeds` structure and can desynchronize it from keychain state — e.g. a seed the user intended to remove can reappear in storage (its mnemonic/seed bytes persist) even though it was removed from keychain, or a legitimately added seed's on-disk metadata can silently vanish while its key remains loaded in keychain until the next unlock (at which point `unlock()` re-derives `extraSeeds` from storage, and the vanished seed would be dropped entirely on next unlock, or the reappeared removed seed would be re-added to keychain on next unlock via `unlock()`'s `extraSeeds.map(({ seed }) => this.#keychain.addSeed(seed))` at lines 288-289). This is a persistence integrity bug with a low-severity practical impact bound: it does not directly leak keys to an unprivileged remote attacker or allow signing without authorization, but it does cause silent loss/reintroduction of key material bookkeeping for the local wallet holder, and a "removed" seed's private key material can end up being reloaded into keychain across subsequent unlocks despite user intent to remove it.

### Likelihood Explanation
Exploitation requires the ability to trigger overlapping `addSeed`/`removeManySeeds` calls with precise timing to land the awaited storage operations in an interleaved order — feasible from a dapp or UI surface that can fire concurrent RPC calls (e.g., rapid double-invocation), but requires the wallet to already be unlocked (`#assertWalletIsUnlocked`) and multi-seed support enabled (`#maxExtraSeeds > 0`), and the race window is narrow (bound by the async gap between the storage `get` and `set` calls). It is a genuine race but timing-dependent and requires an application context that permits truly concurrent invocation of these two wallet RPC methods (not serialized by an outer RPC dispatcher) — this outer serialization behavior could not be verified within the available index and is a source of uncertainty for real-world exploitability.

### Recommendation
Wrap `addSeed`, `removeManySeeds` (and ideally `updateSeed`) in `makeConcurrent({ concurrency: 1 })` the same way `create`/`import` are, or introduce a single mutex/queue around all read-modify-write sequences touching `extraSeeds`/`#seedMetadataAtom`, ensuring keychain mutations (`#keychain.addSeed`/`#keychain.removeSeeds`) only occur after the corresponding storage write is durably committed and serialized relative to other seed-mutating calls.

### Proof of Concept
Integration test in `features/wallet/module/__tests__/index.test.js` style:
1. Set up a wallet with multi-seed support (`maxExtraSeeds >= 2`), unlock it, and add two extra seeds A and B via sequential `addSeed` calls so `extraSeeds` = `[A, B]`.
2. Fire concurrently (without awaiting in between): `wallet.removeManySeeds([seedIdB])` and `wallet.addSeed({ mnemonic: mnemonicC })`, using a storage mock/stub whose `get`/`set` introduce a microtask delay (e.g., `setImmediate`/`Promise.resolve().then()`) between calls to force interleaving of the read and write phases.
3. Await both promises, then assert:
   - `walletStorage.get('extraSeeds')` contains a seed set that is fully consistent with one atomic outcome — e.g., either `[A, C]` (B removed, C added) or reflects a defined ordering — and never contains B alongside a lost C, and never re-lists B after removal.
   - `keychain.exportKey({ seedId: seedIdB })` throws/fails (since B was removed) — assert it never spuriously succeeds due to `extraSeeds` re-containing B's bytes after a later unlock triggered by the corrupted storage state.
   - `wallet.getSeedMetadata()` keys match exactly the seed IDs present in `walletStorage.get('extraSeeds')` (no orphaned metadata entries, no missing entries for present seeds).
4. Run the test repeatedly / with randomized interleavings (fuzz over `await` ordering) to demonstrate the lost-update is reproducible under race conditions rather than a one-off flake.