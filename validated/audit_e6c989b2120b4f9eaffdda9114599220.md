### Title
Byzantine Participant Can Inflate `maximum_height` via Crafted `IndexerHeightMessage`, Causing Premature Request Expiry — (`crates/node/src/network/indexer_heights.rs`, `crates/node/src/requests/queue.rs`)

---

### Summary

A single Byzantine participant (below the signing threshold) can send `IndexerHeightMessage`s with an arbitrarily inflated height. Because `set_height` only ratchets upward and `eligible_leaders_and_maximum_height` derives `maximum_height` from alive participants without bounding it against the actual chain, `cutoff_block` advances past the real chain height. Every signing request submitted at the real chain height is then classified as expired and dropped from all honest nodes' queues, while the contract still holds those requests as pending.

---

### Finding Description

**Step 1 — Ratchet in `set_height`** [1](#0-0) 

Heights are stored unconditionally if `height > current`. There is no upper-bound validation against the actual NEAR chain height. A Byzantine participant can call this with any value.

**Step 2 — `maximum_height` derived from alive participants only** [2](#0-1) 

`maximum_height` is the `max` of heights across `alive_participants`. A Byzantine participant that is connected (alive) and has reported height `H_actual + 300` will dominate this max.

**Step 3 — `cutoff_block` computed from `maximum_height`** [3](#0-2) 

With `REQUEST_EXPIRATION_BLOCKS = 200`, if `maximum_height = H_actual + 300`, then `cutoff_block = H_actual + 101`.

**Step 4 — `is_older_than` drops the request** [4](#0-3) 

A request submitted at `H_actual` has `block_height = H_actual`. The check `cutoff_block > self.block_height` → `H_actual + 101 > H_actual` → **true**. The request is dropped with `DropReason::RequestTimedOut`. [5](#0-4) 

**Step 5 — Side-effect: honest participants also lose leader eligibility** [6](#0-5) 

With `STALE_PARTICIPANT_THRESHOLD = 10`, honest participants at `H_actual` are filtered out as eligible leaders when `maximum_height = H_actual + 300`. Only the Byzantine participant remains eligible — but it will never actually process the request. However, the `is_older_than` check fires *before* the leader check, so the request is dropped regardless.

**Step 6 — The codebase itself acknowledges this risk**

The test comment at line 1166–1168 explicitly notes: *"We let indexer 0 have a higher height than normal. This is to test a pathological case, in case some node reports an incorrectly high height and we want to allow shutting down that node to be a mitigation."* [7](#0-6) 

The mitigation described is *operator intervention* (bringing the node offline). There is no automated protocol-level guard.

---

### Impact Explanation

- All honest nodes independently receive the Byzantine height message and each independently computes the inflated `maximum_height`. Every honest node drops the same requests.
- The contract still holds the requests as pending (yield-resume state). No node will ever respond.
- The attacker can continuously ratchet the height upward (since `set_height` never decreases), so every new signing request submitted at the real chain height is also immediately dropped.
- This is a sustained, complete denial of signing service for as long as the Byzantine participant remains connected.
- Funds submitted to the chain-signature contract are locked until the on-chain yield-resume timeout (200 blocks) expires. If the contract does not automatically refund on timeout, funds are permanently frozen.

---

### Likelihood Explanation

- Requires only **one** Byzantine participant below the signing threshold — no collusion needed.
- The participant must be connected (in `alive_participants`), which is the normal operating state.
- The attack message is a single `IndexerHeightMessage` with an inflated `height` field. No cryptographic material is needed.
- The ratchet is permanent per-node-restart: once the height is stored, it cannot decrease.

---

### Recommendation

1. **Bound `maximum_height` to the node's own observed chain height.** The local node's own indexer height (updated via `update_indexer_height` from actual block events) should serve as a ceiling for `maximum_height`. Peer-reported heights should only be trusted within a reasonable delta of the local height.
2. **Validate peer-reported heights against the local chain height** before calling `set_height`. Reject any height that exceeds `local_height + SOME_TOLERANCE`.
3. **Use the local node's own indexer height as the primary source for `cutoff_block`**, with peer heights used only for leader-eligibility staleness filtering — not for expiry computation.

---

### Proof of Concept

```
// Deterministic simulation:
// 4 participants; participant[0] is Byzantine; participant[1] is "us" (MY_INDEX).
// Actual chain height: 100.

setup.network_api.set_height(participants[0], 400); // Byzantine: actual + 300
setup.network_api.set_height(participants[1], 100); // honest
setup.network_api.set_height(participants[2], 100); // honest
setup.network_api.set_height(participants[3], 100); // honest

// Submit a signing request at actual chain height 101
let req = setup.add_request_leader();
setup.update(&mut pending_requests); // block_height = 101

// maximum_height = 400 (from Byzantine participant[0])
// cutoff_block = (400 - 200 + 1) = 201
// req.block_height = 101
// is_older_than(201) = 201 > 101 = true → DROPPED

let to_attempt = pending_requests.get_requests_to_attempt();
assert_eq!(to_attempt.len(), 0); // request dropped despite being only 1 block old
assert!(!pending_requests.requests.contains_key(&req.id)); // removed from queue
// Contract still holds the request as pending → divergence
```

### Citations

**File:** crates/node/src/network/indexer_heights.rs (L21-26)
```rust
    pub fn set_height(&self, participant: ParticipantId, height: u64) {
        let atomic = self.heights.get(&participant).unwrap();
        let current = atomic.load(std::sync::atomic::Ordering::Relaxed);
        if height > current {
            atomic.store(height, std::sync::atomic::Ordering::Relaxed);
        }
```

**File:** crates/node/src/requests/queue.rs (L332-334)
```rust
    fn is_older_than(&self, cutoff_block: BlockHeight) -> bool {
        cutoff_block > self.block_height
    }
```

**File:** crates/node/src/requests/queue.rs (L377-381)
```rust
        // check it against the network height
        if self.is_older_than(cutoff_block) {
            // This request is definitely not useful anymore, so discard it.
            return RequestStatus::Drop(DropReason::RequestTimedOut);
        }
```

**File:** crates/node/src/requests/queue.rs (L532-538)
```rust
        let indexer_heights = self.network_api.indexer_heights();
        let alive_participants = self.network_api.alive_participants();
        let maximum_height = alive_participants
            .iter()
            .map(|p| indexer_heights.get(p).copied().unwrap_or(0))
            .max()
            .unwrap_or(0);
```

**File:** crates/node/src/requests/queue.rs (L539-548)
```rust
        let eligible_leaders = self
            .all_participants
            .iter()
            .filter(|p| {
                alive_participants.contains(p)
                    && indexer_heights.get(p).copied().unwrap_or(0) + STALE_PARTICIPANT_THRESHOLD
                        >= maximum_height
            })
            .copied()
            .collect::<HashSet<_>>();
```

**File:** crates/node/src/requests/queue.rs (L604-606)
```rust
        // any request strictly older than `cutoff_block` will be considered expired
        let cutoff_block: BlockHeight =
            (maximum_height.saturating_sub(REQUEST_EXPIRATION_BLOCKS) + 1).into();
```

**File:** crates/node/src/requests/queue.rs (L1166-1170)
```rust
        // Indexer 0 is offline; indexer 2 is stale. We let indexer 0 have a higher height than
        // normal. This is to test a pathological case, in case some node reports an incorrectly high
        // height and we want to allow shutting down that node to be a mitigation.
        setup.network_api.bring_down(setup.participant_ids[0]);
        setup.network_api.set_height(setup.participant_ids[0], 120); // ignored because offline
```
