The code confirms the bug. Let me verify the `get_starknet_version` guard and the pending data flow precisely.

### Title
Pending-block `starknet_estimateFee` / `starknet_simulateTransactions` always uses `StarknetVersion::LATEST` versioned constants instead of the actual network version — (`crates/apollo_rpc_execution/src/lib.rs`)

---

### Summary

`create_block_context` unconditionally queries `get_starknet_version` with the **pending** block number (`block_context_number + 1`). That block does not yet exist in storage, so the storage guard returns `None`, and the code falls back to `StarknetVersion::LATEST`. Any unprivileged RPC client that calls `starknet_estimateFee` or `starknet_simulateTransactions` with `block_id = Pending` therefore receives fee estimates computed with the wrong `VersionedConstants`.

---

### Finding Description

**Step 1 — pending `block_number` is set to `block_context_number + 1`**

When `maybe_pending_data` is `Some`, the destructuring at line 342 sets:

```
block_number = block_context_number.unchecked_next()   // N + 1
``` [1](#0-0) 

**Step 2 — `get_starknet_version` is called with that pending block number**

```rust
let starknet_version = storage_reader
    .begin_ro_txn()?
    .get_starknet_version(block_number)?   // block_number = N+1
    .unwrap_or(StarknetVersion::LATEST);
``` [2](#0-1) 

**Step 3 — the storage guard always returns `None` for the pending block number**

`get_starknet_version` opens with:

```rust
if block_number >= self.get_header_marker()? {
    return Ok(None);
}
```

`header_marker` equals the next block number to be written, which is exactly `N + 1`. Therefore `N+1 >= N+1` is always true, and the function returns `Ok(None)` before ever touching the cursor. [3](#0-2) 

**Step 4 — fallback to `LATEST` and wrong `VersionedConstants`**

The `unwrap_or(StarknetVersion::LATEST)` at line 373 fires on every pending-block call, and line 408 then selects execution constants for `LATEST`:

```rust
let versioned_constants = VersionedConstants::get(&starknet_version)?;
``` [4](#0-3) 

---

### Impact Explanation

`VersionedConstants` controls step costs, builtin costs, L1/L2 gas multipliers, and other fee-relevant parameters. When the live network runs on a version older than `LATEST` (e.g., `V0_13_0`), every `starknet_estimateFee` / `starknet_simulateTransactions` call with `block_id=Pending` returns a fee computed with the wrong constant table. Depending on the direction of the difference, users either:

- **under-estimate** fees → submit transactions that the sequencer rejects for insufficient resources, or
- **over-estimate** fees → overpay, with economic impact.

This matches the allowed impact: **"High. RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value."**

---

### Likelihood Explanation

- Triggered by any unauthenticated RPC call with `block_id=Pending`.
- `Pending` is the most common tag used by wallets and dApps for fee estimation.
- The bug fires on **every** such call without exception; there is no code path that avoids it.
- No special privileges, keys, or network position are required.

---

### Recommendation

Replace the `block_number` argument to `get_starknet_version` with `block_context_number` (the latest stored block) when pending data is present, so the lookup falls within the stored range:

```rust
// Use block_context_number (the last finalized block) for version lookup,
// regardless of whether we are building a pending or non-pending context.
let starknet_version = storage_reader
    .begin_ro_txn()?
    .get_starknet_version(block_context_number)?
    .unwrap_or(StarknetVersion::LATEST);
```

Alternatively, propagate the `starknet_version` field already present in `PendingBlockOrDeprecated` through `PendingData` and use it directly when `maybe_pending_data` is `Some`. [2](#0-1) 

---

### Proof of Concept

```rust
// Pseudocode for a Rust unit test
// 1. Write block N with StarknetVersion::V0_13_0 into storage.
// 2. Construct PendingData (parent = block N's hash).
// 3. Call exec_estimate_fee / execute_transactions with
//    block_context_block_number = N, maybe_pending_data = Some(pending).
// 4. Capture the BlockContext returned.
// 5. Assert:
//    block_context.block_info().starknet_version == StarknetVersion::LATEST
//    // (not V0_13_0 — proving the wrong constants were used)
```

The assertion at step 5 will pass because `get_starknet_version(N+1)` hits the `block_number >= header_marker` guard and returns `None`, forcing the fallback to `LATEST`. [5](#0-4)

### Citations

**File:** crates/apollo_rpc_execution/src/lib.rs (L340-342)
```rust
    ) = match maybe_pending_data {
        Some(pending_data) => (
            block_context_number.unchecked_next(),
```

**File:** crates/apollo_rpc_execution/src/lib.rs (L370-373)
```rust
    let starknet_version = storage_reader
        .begin_ro_txn()?
        .get_starknet_version(block_number)?
        .unwrap_or(StarknetVersion::LATEST);
```

**File:** crates/apollo_rpc_execution/src/lib.rs (L408-408)
```rust
    let versioned_constants = VersionedConstants::get(&starknet_version)?;
```

**File:** crates/apollo_storage/src/header.rs (L252-258)
```rust
    fn get_starknet_version(
        &self,
        block_number: BlockNumber,
    ) -> StorageResult<Option<StarknetVersion>> {
        if block_number >= self.get_header_marker()? {
            return Ok(None);
        }
```
