The code confirms this is a real bug. Let me trace the full path precisely.

**Call chain:**

`commit_block` (line 312) drops `rejected_txs` entirely when routing to catch-up: [1](#0-0) 

`accept_commit_while_catching_up` `Equal` branch passes `Default::default()` (empty set) as `rejected_txs`: [2](#0-1) 

`apply_commit_block` partitions `consumed_txs` against the (empty) `rejected_txs`, so ALL consumed txs land in the committed bucket: [3](#0-2) 

`mark_committed()` sets `self.committed = true` and `state = Committed`: [4](#0-3) 

**Why `Rejected` ≠ `Committed` in practice:**

`is_validatable()` explicitly includes `Rejected` as a validatable state (the docstring says "this includes states like: a rejected transaction"): [5](#0-4) 

`is_proposable()` only allows `Pending`, so rejected txs are not re-proposed by the proposer — but they remain validatable for validators. A tx incorrectly marked `Committed` is neither proposable nor validatable, permanently excluding it.

**Secondary breakage — future panic:**

`mark_rejected()` asserts `!self.committed`. If the same tx appears in a future block's rejected set, the node panics: [6](#0-5) 

**The backlog drain has the same bug:**

`CommitBlockBacklog` never stores `rejected_txs`, and the drain loop also passes `Default::default()`: [7](#0-6) [8](#0-7) 

**The developers acknowledged this gap with a TODO:** [2](#0-1) 

---

### Title
Rejected L1 Handler Txs Silently Marked `Committed` During Catch-Up, Permanently Losing L1→L2 Messages — (`crates/apollo_l1_events/src/l1_events_provider.rs`)

### Summary
When the `L1EventsProvider` is in `CatchingUp` state and the batcher calls `commit_block` at exactly the catch-up target height (the `Equal` branch), the `rejected_txs` parameter is silently dropped. `apply_commit_block` is called with an empty rejected set, causing every rejected L1 handler tx in that block to be recorded as `Committed` instead of `Rejected`. The same defect applies to every entry drained from the backlog. The result is permanent, unrecoverable loss of those L1→L2 messages from the provider's perspective.

### Finding Description
`commit_block` accepts both `committed_txs` and `rejected_txs`. When the provider is catching up, it routes to `accept_commit_while_catching_up(committed_txs, height)` — `rejected_txs` is never forwarded. Inside that function, the `Equal` branch calls `apply_commit_block(committed_txs, Default::default())`. `apply_commit_block` partitions `consumed_txs` against the (now-empty) `rejected_txs` set; every tx ends up in the committed partition and `mark_committed()` is called on all of them, setting `state = Committed` and `committed = true`.

`CommitBlockBacklog` only stores `committed_txs`, so the backlog drain loop (`for committed_block in backlog { self.apply_commit_block(committed_block.committed_txs, Default::default()); }`) has the identical defect for every block buffered while catching up.

### Impact Explanation
- A rejected L1 handler tx is validatable (`is_validatable()` returns `true` for `Rejected`) and can be re-included in a future block. Once incorrectly marked `Committed`, `is_validatable()` returns `false` and the tx is permanently excluded — the L1→L2 message is lost.
- `mark_committed()` sets the `committed` boolean flag. If the same tx hash later appears in a `rejected_txs` list, `mark_rejected()` asserts `!self.committed` and **panics**, crashing the node.
- The provider's internal state diverges from the actual block execution result, corrupting the authoritative record of which L1 handler messages have been delivered.

### Likelihood Explanation
The catch-up path is exercised on every node startup and after every crash. Rejected L1 handler txs occur whenever an L1→L2 message's target contract reverts. The `Equal` branch is hit whenever the batcher commits a block at exactly the sync target height — a normal operational event. No adversarial action is required; any L1 user whose message is rejected in that block is affected.

### Recommendation
Forward `rejected_txs` through the entire catch-up path:
1. Add `rejected_txs: IndexSet<TransactionHash>` to `CommitBlockBacklog`.
2. Pass `rejected_txs` from `commit_block` into `accept_commit_while_catching_up`.
3. In the `Equal` branch, call `apply_commit_block(committed_txs, rejected_txs)`.
4. In the backlog drain loop, call `apply_commit_block(committed_block.committed_txs, committed_block.rejected_txs)`.

### Proof of Concept
```
1. Initialize provider; set current_height = H, state = CatchingUp, target_height = H.
2. Add tx_A to the provider records (Pending state).
3. Call commit_block(committed_txs={tx_A}, rejected_txs={tx_A}, height=H).
   → Routes to accept_commit_while_catching_up({tx_A}, H).
   → new_height == current_height → Equal branch.
   → apply_commit_block({tx_A}, Default::default()).
   → partition: rejected_and_consumed=[], committed=[tx_A].
   → commit_txs([tx_A], []).
   → mark_committed() called on tx_A.
4. Assert records[tx_A].state == Committed.   ← BUG: should be Rejected.
5. Call validate(tx_A, H+1).
   → is_validatable() returns false (Committed).
   → Returns AlreadyIncludedOnL2.             ← BUG: should be Validated.
```

### Citations

**File:** crates/apollo_l1_events/src/l1_events_provider.rs (L310-313)
```rust
        if self.state.is_catching_up() {
            // Once catchup completes it will transition to Pending state by itself.
            return self.accept_commit_while_catching_up(committed_txs, height);
        }
```

**File:** crates/apollo_l1_events/src/l1_events_provider.rs (L378-381)
```rust
        let (rejected_and_consumed, committed_txs): (Vec<_>, Vec<_>) =
            consumed_txs.iter().copied().partition(|tx| rejected_txs.contains(tx));
        self.tx_manager.commit_txs(&committed_txs, &rejected_and_consumed);

```

**File:** crates/apollo_l1_events/src/l1_events_provider.rs (L433-434)
```rust
            // TODO(guyn): check what about rejected txs here and in the backlog?
            Equal => self.apply_commit_block(committed_txs, Default::default()),
```

**File:** crates/apollo_l1_events/src/l1_events_provider.rs (L476-478)
```rust
            for committed_block in backlog {
                self.apply_commit_block(committed_block.committed_txs, Default::default());
            }
```

**File:** crates/apollo_l1_events/src/transaction_record.rs (L50-60)
```rust
    pub fn mark_committed(&mut self) {
        // Can't return error because committing only part of a block leaves the provider in an
        // undetermined state.
        assert!(
            !self.committed,
            "L1 handler transaction {} committed twice, this may lead to l2 reorgs,",
            self.tx.tx_hash()
        );
        self.state = TransactionState::Committed;
        self.committed = true;
    }
```

**File:** crates/apollo_l1_events/src/transaction_record.rs (L63-72)
```rust
    pub fn mark_rejected(&mut self) {
        // Pedantic, this is unlikely to happen.
        assert!(
            !self.committed,
            "Attempted to reject a committed transaction {}",
            self.tx.tx_hash()
        );
        self.state = TransactionState::Rejected;
        self.rejected = true;
    }
```

**File:** crates/apollo_l1_events/src/transaction_record.rs (L179-181)
```rust
    pub fn is_validatable(&self) -> bool {
        !self.is_committed() && !self.is_cancelled() && !self.is_consumed()
    }
```

**File:** crates/apollo_l1_events/src/catchupper.rs (L249-253)
```rust
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct CommitBlockBacklog {
    pub height: BlockNumber,
    pub committed_txs: IndexSet<TransactionHash>,
}
```
