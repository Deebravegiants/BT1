No vulnerability found for this question.

**Analysis:** The `last_recorded` fast path in `record()` only skips work when the *current* call's `(address, module_name)` exactly matches the *immediately preceding* call's `(address, module_name)` [1](#0-0) . This is purely a performance optimization to avoid a hash lookup/allocation on consecutive re-fetches of the same module (which happens because a single module load makes several back-to-back internal fetches of the same key) [2](#0-1) .

If the check fails to match (e.g., alternating between address A and B: A, B, A, B, ...), the code falls through to the non-skip branch every single time, inserting the key into `module_reads` (an `FxHashSet<StateKey>`) [3](#0-2) . Correctness of the final recorded set (`into_recorded_reads`) depends entirely on `FxHashSet::insert`, which is idempotent and dedups by key regardless of call order or interleaving [4](#0-3) . There is no code path where a module read is dropped without being inserted — the `last_recorded` check can only ever cause a redundant re-insert of the *same* key to be skipped, since it requires an exact match on both address and module name. Alternating A/B never triggers the skip for a mismatched key, so both A and B are always recorded. The proposed proof idea does not correspond to an actual defect in the logic.

### Citations

**File:** aptos-move/aptos-vm-types/src/module_and_script_storage/read_recording.rs (L38-41)
```rust
    /// The previously recorded `(address, name)`. Recording sits above the module cache, and one
    /// module resolution makes several back-to-back fetches of the same key (a load charges the
    /// module's size then fetches it; the module is re-fetched to resolve the types it defines),
    /// so skipping such a run here avoids a set lookup and key construction per cheap cache hit.
```

**File:** aptos-move/aptos-vm-types/src/module_and_script_storage/read_recording.rs (L58-61)
```rust
    /// Returns the state keys of modules fetched so far, deduplicated by key.
    pub fn into_recorded_reads(self) -> FxHashSet<StateKey> {
        self.module_reads.into_inner()
    }
```

**File:** aptos-move/aptos-vm-types/src/module_and_script_storage/read_recording.rs (L63-80)
```rust
    #[inline]
    fn record(&self, address: &AccountAddress, module_name: &IdentStr) {
        {
            // Fast path: a run of accesses to the same module needs no further work. Only an
            // exact (address, name) match is skipped, so the recorded set is identical either
            // way.
            let last = self.last_recorded.borrow();
            if last.0 == *address && last.1.as_str() == module_name.as_str() {
                return;
            }
        }
        let key = StateKey::module(address, module_name);
        self.module_reads.borrow_mut().insert(key);
        let mut last = self.last_recorded.borrow_mut();
        last.0 = *address;
        last.1.clear();
        last.1.push_str(module_name.as_str());
    }
```
