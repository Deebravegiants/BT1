Looking at the actual code, I need to trace the exact path described.

**`clear_pending_roots` RPC handler** — no status guard: [1](#0-0) 

The handler calls `data_store.clear_pending_roots()` directly with zero check on whether the pending root is `PENDING` (submitted) vs `PENDING_BATCH`. Any caller with RPC access can invoke this for any store.

**`_update_confirmation_status` recovery path** — requires the pending root to exist: [2](#0-1) 

The only path that advances the local committed root (when `generation_shift == 0`) is the `else` branch that fetches `get_pending_root` and checks `pending_root is not None`. If the pending root was deleted by the RPC call, this condition is `False`, `change_root_status` is never called, and the function exits after a no-op `clear_pending_roots`.

**`batch_update` → PENDING root creation:** [3](#0-2) 

When `submit_on_chain=True`, a root with `Status.PENDING` is created and the tx is submitted to the mempool.

**The exact divergence path:**

1. `batch_update` → pending root created at generation N+1, hash H_new, `Status.PENDING`; tx in mempool
2. RPC caller calls `clear_pending_roots(store_id)` → pending root deleted
3. Tx confirms on-chain → singleton at generation N+1, root H_new
4. `_update_confirmation_status` runs:
   - committed root: generation N, hash H_old
   - `new_hashes = [H_new]`, `root_hash = H_old`
   - `H_new ≠ H_old` → `generation_shift = 0`
   - `pending_root = None` → condition at line 597 is `False`
   - No `change_root_status` call
   - Local store permanently stuck at generation N [4](#0-3) 

There is no fallback recovery path. Subsequent calls to `_update_confirmation_status` repeat the same logic with the same result. The `fetch_and_validate` path (for subscriptions) could theoretically re-download data from a server, but for an owned store with no configured download server this is unavailable.

**The missing guard** — compare with `submit_pending_root`, which correctly rejects calls on already-submitted roots: [5](#0-4) 

`submit_pending_root` checks `pending_root.status == Status.PENDING` and raises. `clear_pending_roots` has no equivalent check.

---

### Title
Unguarded `clear_pending_roots` RPC Allows Permanent Data Layer Store Sync Divergence — (`chia/data_layer/data_layer_rpc_api.py`, `chia/data_layer/data_layer.py`)

### Summary
The `/clear_pending_roots` RPC endpoint deletes the pending root for a store without checking whether that root has `Status.PENDING` (i.e., its corresponding transaction has already been submitted to the mempool). After deletion, `_update_confirmation_status` has no recovery path and the local store is permanently stuck at the pre-update generation while the on-chain singleton has advanced.

### Finding Description
`DataLayerRpcApi.clear_pending_roots` (line 553–556 of `data_layer_rpc_api.py`) calls `data_store.clear_pending_roots()` unconditionally. No check is made on the status of the pending root. If the root is `Status.PENDING` (meaning a transaction encoding the new root hash has already been broadcast), deleting it breaks the invariant that `_update_confirmation_status` relies on to advance the local committed root.

In `_update_confirmation_status` (lines 594–604 of `data_layer.py`), the only mechanism to commit a new root when `generation_shift == 0` is to find a matching pending root via `get_pending_root` and call `change_root_status`. With the pending root deleted, this branch is never taken, and every future invocation of `_update_confirmation_status` produces the same no-op result.

### Impact Explanation
The local Data Layer store is permanently stuck at generation N while the on-chain singleton is at generation N+1. Consequences:
- All subsequent `batch_update` calls operate on a store whose committed root is stale, producing incorrect generation numbers and potentially conflicting on-chain updates.
- `get_local_root` returns the wrong hash, breaking any application relying on local root integrity.
- Offer settlement and proof generation using this store produce proofs against a stale root, which will fail on-chain verification.

### Likelihood Explanation
The RPC is accessible to any local process holding the Data Layer SSL certificate (standard Chia RPC authentication). No elevated privilege beyond normal RPC access is required. The window between `batch_update` submission and block confirmation (typically 30–60 seconds) is ample for a racing call.

### Recommendation
In `DataLayerRpcApi.clear_pending_roots` (or in `DataLayer.clear_pending_roots` if a service-layer wrapper is added), fetch the pending root first and reject the call if `pending_root.status == Status.PENDING`:

```python
async def clear_pending_roots(self, request: ClearPendingRootsRequest) -> ClearPendingRootsResponse:
    pending = await self.service.data_store.get_pending_root(store_id=request.store_id)
    if pending is not None and pending.status == Status.PENDING:
        raise ValueError("Cannot clear a pending root that has already been submitted on-chain.")
    root = await self.service.data_store.clear_pending_roots(store_id=request.store_id)
    return ClearPendingRootsResponse(success=root is not None, root=root)
```

### Proof of Concept
1. Create a store and call `batch_update` with `submit_on_chain=True`. Record the tx id.
2. Before farming a block, call `clear_pending_roots(store_id)` via RPC. Observe `success=True`.
3. Farm a block to confirm the transaction.
4. Call `get_local_root(store_id)` — it returns H_old (generation N hash).
5. Call `get_root(store_id)` (on-chain) — it returns H_new (generation N+1 hash).
6. Assert `local_root != on_chain_root` — divergence is permanent; repeated calls to any RPC that triggers `_update_confirmation_status` do not resolve it.

### Citations

**File:** chia/data_layer/data_layer_rpc_api.py (L552-556)
```python
    @marshal()  # type: ignore[arg-type]
    async def clear_pending_roots(self, request: ClearPendingRootsRequest) -> ClearPendingRootsResponse:
        root = await self.service.data_store.clear_pending_roots(store_id=request.store_id)

        return ClearPendingRootsResponse(success=root is not None, root=root)
```

**File:** chia/data_layer/data_layer.py (L302-315)
```python
    async def batch_update(
        self,
        store_id: bytes32,
        changelist: list[dict[str, Any]],
        fee: uint64,
        submit_on_chain: bool = True,
    ) -> TransactionRecord | None:
        status = Status.PENDING if submit_on_chain else Status.PENDING_BATCH
        await self.batch_insert(store_id=store_id, changelist=changelist, status=status)

        if submit_on_chain:
            return await self.publish_update(store_id=store_id, fee=fee)
        else:
            return None
```

**File:** chia/data_layer/data_layer.py (L358-372)
```python
    async def submit_pending_root(
        self,
        store_id: bytes32,
        fee: uint64,
    ) -> TransactionRecord:
        await self._update_confirmation_status(store_id=store_id)

        pending_root: Root | None = await self.data_store.get_pending_root(store_id=store_id)
        if pending_root is None:
            raise Exception("Latest root is already confirmed.")
        if pending_root.status == Status.PENDING:
            raise Exception("Pending root is already submitted.")

        await self.data_store.change_root_status(pending_root, Status.PENDING)
        return await self.publish_update(store_id, fee)
```

**File:** chia/data_layer/data_layer.py (L585-604)
```python
            new_hashes = [record.root for record in reversed(wallet_history)]
            root_hash = self.none_bytes if root.node_hash is None else root.node_hash
            generation_shift = 0
            while len(new_hashes) > 0 and new_hashes[0] == root_hash:
                generation_shift += 1
                new_hashes.pop(0)
            if generation_shift > 0:
                await self.data_store.clear_pending_roots(store_id=store_id)
                await self.data_store.shift_root_generations(store_id=store_id, shift_size=generation_shift)
            else:
                expected_root_hash = None if new_hashes[0] == self.none_bytes else new_hashes[0]
                pending_root = await self.data_store.get_pending_root(store_id=store_id)
                if (
                    pending_root is not None
                    and pending_root.generation == root.generation + 1
                    and pending_root.node_hash == expected_root_hash
                    and pending_root.status == Status.PENDING
                ):
                    await self.data_store.change_root_status(pending_root, Status.COMMITTED)
            await self.data_store.clear_pending_roots(store_id=store_id)
```
