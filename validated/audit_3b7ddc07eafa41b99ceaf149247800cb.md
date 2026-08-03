No vulnerability found for this question.

**Reasoning:** The reviewed code in `state_kv_pruner_manager.rs` governs internal RocksDB pruning bookkeeping (`min_readable_version`, `pruner_worker` target version) for the state-KV shard of `aptosdb`. It has no relationship to account/object ownership fields, resource-account authority, or any custody-relevant state transition.

Key points:
1. **No unprivileged entrypoint exists.** The scenario requires "attacker-induced faults" causing node restarts and precise timing control over when `set_pruner_target_db_version` runs versus when `save_min_readable_version` persists to disk. This is node-operator/infrastructure-level control, not a transaction, package, view, authenticator, API, bytecode, or proof input as required by the Review Bounds. Malicious peer/node behavior and generic fault-induced restarts are explicitly excluded from scope.
2. **`min_readable_version` is not an ownership or authority field.** It only bounds which historical state-KV versions are guaranteed retained on disk for pruning purposes: [1](#0-0)  It never gates who can execute a transaction, sign for a resource account, or move/mint/burn/freeze any asset. Ledger execution and authentication go through the VM/executor and account authentication key checks, not through this pruner-progress recovery value.
3. **No mechanism connects a wider "readable window" to resurrecting a stale owner as authoritative.** Even if `min_readable_version` were recovered inconsistently with the last in-memory target (which would at most affect how far back the state-KV pruner physically prunes stale index entries), the current authoritative state of any resource account is determined by the latest committed state tree/state-KV values, not by the pruner's watermark. Resource-account ownership/authentication-key reassignment is enforced in `resource_account`/`account` Move modules and validated at signature-verification and VM execution time, both of which are entirely independent of this struct.
4. There is no code shown, in this file or elsewhere in `aptosdb`, that reads `min_readable_version` (or the recovered pruner progress) to determine which state values are "authoritative" for transaction execution or authentication — it is used solely to decide the next pruning batch: [2](#0-1)  and to persist pruning progress: [3](#0-2) .

The submission does not identify any unprivileged transaction/input path that reaches this code, and does not demonstrate how a pruner-progress recovery inconsistency could change who owns, moves, mints, burns, freezes, or recovers value. It fails the Decision Standard and Review Path (no real custody boundary crossed, no wrong balance/owner/authority named with supporting code).

### Citations

**File:** storage/aptosdb/src/pruner/state_kv_pruner/state_kv_pruner_manager.rs (L61-71)
```rust
    /// Sets pruner target version when necessary.
    fn maybe_set_pruner_target_db_version(&self, latest_version: Version) {
        let min_readable_version = self.get_min_readable_version();
        // Only wake up the state kv pruner if there are `ledger_pruner_pruning_batch_size` pending
        if self.is_pruner_enabled()
            && latest_version
                >= min_readable_version + self.pruning_batch_size as u64 + self.prune_window
        {
            self.set_pruner_target_db_version(latest_version);
        }
    }
```

**File:** storage/aptosdb/src/pruner/state_kv_pruner/state_kv_pruner_manager.rs (L73-85)
```rust
    fn save_min_readable_version(&self, min_readable_version: Version) -> Result<()> {
        self.min_readable_version
            .store(min_readable_version, Ordering::SeqCst);

        PRUNER_VERSIONS
            .with_label_values(&[S::name(), "min_readable"])
            .set(min_readable_version as i64);

        self.state_kv_db.metadata_db().put::<DbMetadataSchema>(
            &S::pruner_progress_key(),
            &DbMetadataValue::Version(min_readable_version),
        )
    }
```

**File:** storage/aptosdb/src/pruner/state_kv_pruner/state_kv_pruner_manager.rs (L119-124)
```rust
        let min_readable_version =
            pruner_utils::get_state_kv_pruner_progress::<S>(&state_kv_db).expect("Must succeed.");

        PRUNER_VERSIONS
            .with_label_values(&[S::name(), "min_readable"])
            .set(min_readable_version as i64);
```
