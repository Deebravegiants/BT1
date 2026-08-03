[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L119-122)
```rust
/// After a transaction's execution attempt is processed by the scheduler, the [AbortManager] instance
/// is transferred by value (moving ownership) to the [SchedulerV2::finish_execution] function.
/// This transfer enforces a clear ownership model and ensures that the [AbortManager]'s state
/// is correctly consumed and finalized.
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L123-131)
```rust
pub(crate) struct AbortManager<'a> {
    owner_txn_idx: TxnIndex,
    owner_incarnation: Incarnation,
    scheduler: &'a SchedulerV2,
    // Transaction index in the map implies a write by (owner_txn_idx, owner_incarnation)
    // invalidated a read by the said transaction. If the incarnation is stored in the
    // entry, then start_abort call was successful, implying a promise to call finish_abort.
    invalidated_dependencies: BTreeMap<TxnIndex, Option<Incarnation>>,
}
```

**File:** aptos-move/block-executor/src/scheduler_v2.rs (L246-260)
```rust
    // For invalidated dependencies that are mapped to an incarnation, [SchedulerV2::start_abort]
    // was successful, and the [SchedulerV2::finish_abort] still needs to be performed.
    fn take(
        self,
    ) -> (
        TxnIndex,
        Incarnation,
        BTreeMap<TxnIndex, Option<Incarnation>>,
    ) {
        (
            self.owner_txn_idx,
            self.owner_incarnation,
            self.invalidated_dependencies,
        )
    }
```
