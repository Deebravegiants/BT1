No vulnerability found for this question.

**Analysis:** The call chain confirms there's no race of the type described. `maybe_set_pruner_target_db_version` is invoked from `post_commit`, which itself is called only after `commit_ledger` has already written and durably persisted the ledger metadata batch (`self.ledger_db.metadata_db().write_schemas(ledger_batch)?`) [1](#0-0) . The pruner target is set using the version that was just durably committed, not a version whose writes are still in flight [2](#0-1) .

The actual data commit path (`calculate_and_commit_ledger_and_state_kv`, which writes write-sets, transactions, state KV, etc.) happens synchronously and completes before `post_commit` (and thus before any pruner target update) is reached, whether via `pre_commit_ledger`/`commit_ledger` [3](#0-2)  or via the internal `calculate_and_commit_ledger_and_state_kv` scope that blocks until all spawned commit tasks finish [4](#0-3) . There is no code path where `set_target_version` is driven with a version whose write-sets have not yet been flushed — the ordering is structurally enforced by the synchronous nature of `post_commit` being called strictly after the flush.

Additionally, `DBPruner::is_pruning_pending`/`prune()` only act on already-committed, durable data [5](#0-4) , and this is purely an internal storage/pruner mechanism, not a custody-boundary surface reachable by crafting transaction content (e.g., via `create_object`/`create_named_object`). No unprivileged input can alter this ordering or influence which version is passed to the pruner target ahead of its flush completion. This does not meet the Custody Impact Gate — no owner, authority, or balance corruption path is present, only a hypothetical internal storage race that the actual commit/post_commit sequencing rules out.

### Citations

**File:** storage/aptosdb/src/db/aptosdb_writer.rs (L50-119)
```rust
    fn pre_commit_ledger(&self, chunk: ChunkToCommit, sync_commit: bool) -> Result<()> {
        gauged_api("pre_commit_ledger", || {
            // Pre-committing and committing in concurrency is allowed but not pre-committing at the
            // same time from multiple threads, the same for committing.
            // Consensus and state sync must hand over to each other after all pending execution and
            // committing complete.
            let _lock = self
                .pre_commit_lock
                .try_lock()
                .expect("Concurrent committing detected.");
            let _timer = OTHER_TIMERS_SECONDS.timer_with(&["pre_commit_ledger"]);

            chunk
                .state_summary
                .latest()
                .global_state_summary
                .log_generation("db_save");

            self.pre_commit_validation(&chunk)?;
            let _new_root_hash =
                self.calculate_and_commit_ledger_and_state_kv(&chunk, sync_commit)?;

            let _timer = OTHER_TIMERS_SECONDS.timer_with(&["save_transactions__others"]);

            self.state_store.buffered_state().lock().update(
                chunk.result_ledger_state_with_summary(),
                chunk.hot_state_updates.clone(),
                chunk.estimated_total_state_updates(),
                sync_commit || chunk.is_reconfig,
            )?;

            Ok(())
        })
    }

    fn commit_ledger(
        &self,
        version: Version,
        ledger_info_with_sigs: Option<&LedgerInfoWithSignatures>,
        chunk_opt: Option<ChunkToCommit>,
    ) -> Result<()> {
        gauged_api("commit_ledger", || {
            // Pre-committing and committing in concurrency is allowed but not pre-committing at the
            // same time from multiple threads, the same for committing.
            // Consensus and state sync must hand over to each other after all pending execution and
            // committing complete.
            let _lock = self
                .commit_lock
                .try_lock()
                .expect("Concurrent committing detected.");
            let _timer = OTHER_TIMERS_SECONDS.timer_with(&["commit_ledger"]);

            let old_committed_ver = self.get_and_check_commit_range(version)?;

            let mut ledger_batch = SchemaBatch::new();
            // Write down LedgerInfo if provided.
            if let Some(li) = ledger_info_with_sigs {
                self.check_and_put_ledger_info(version, li, &mut ledger_batch)?;
            }
            // Write down commit progress
            ledger_batch.put::<DbMetadataSchema>(
                &DbMetadataKey::OverallCommitProgress,
                &DbMetadataValue::Version(version),
            )?;
            self.ledger_db.metadata_db().write_schemas(ledger_batch)?;

            // Notify the pruners, invoke the indexer, and update in-memory ledger info.
            self.post_commit(old_committed_ver, version, ledger_info_with_sigs, chunk_opt)
        })
    }
```

**File:** storage/aptosdb/src/db/aptosdb_writer.rs (L286-341)
```rust
    fn calculate_and_commit_ledger_and_state_kv(
        &self,
        chunk: &ChunkToCommit,
        sync_commit: bool,
    ) -> Result<HashValue> {
        let _timer = OTHER_TIMERS_SECONDS.timer_with(&["save_transactions__work"]);

        let mut new_root_hash = HashValue::zero();
        THREAD_MANAGER.get_non_exe_cpu_pool().scope(|s| {
            // TODO(grao): Write progress for each of the following databases, and handle the
            // inconsistency at the startup time.
            //
            // TODO(grao): Consider propagating the error instead of panic, if necessary.
            s.spawn(|_| {
                self.commit_events(chunk.first_version, chunk.transaction_outputs)
                    .unwrap()
            });
            s.spawn(|_| {
                self.ledger_db
                    .write_set_db()
                    .commit_write_sets(chunk.first_version, chunk.transaction_outputs)
                    .unwrap()
            });
            s.spawn(|_| {
                self.ledger_db
                    .transaction_db()
                    .commit_transactions(
                        chunk.first_version,
                        chunk.transactions,
                        true, /* skip_index */
                    )
                    .unwrap()
            });
            s.spawn(|_| {
                self.ledger_db
                    .persisted_auxiliary_info_db()
                    .commit_auxiliary_info(chunk.first_version, chunk.persisted_auxiliary_infos)
                    .unwrap()
            });
            s.spawn(|_| self.commit_state_kv_and_ledger_metadata(chunk).unwrap());
            s.spawn(|_| {
                self.commit_transaction_infos(chunk.first_version, chunk.transaction_infos)
                    .unwrap()
            });
            s.spawn(|_| {
                new_root_hash = self
                    .commit_transaction_accumulator(chunk.first_version, chunk.transaction_infos)
                    .unwrap()
            });
            if self.position.is_some() {
                s.spawn(|_| self.commit_native_position(chunk, sync_commit).unwrap());
            }
        });

        Ok(new_root_hash)
    }
```

**File:** storage/aptosdb/src/db/aptosdb_writer.rs (L791-812)
```rust
            self.ledger_pruner
                .maybe_set_pruner_target_db_version(version);
            self.state_store
                .state_pruner
                .state_kv_pruner
                .maybe_set_pruner_target_db_version(version);
            self.state_store
                .state_pruner
                .hot_state_kv_pruner
                .maybe_set_pruner_target_db_version(version);
            // Activate the native-position value pruner here too, after
            // the commit is durable — same point as `state_kv_pruner`.
            // (The merkle pruners are driven when snapshots persist.)
            if let Some(position_pruner) = self
                .position
                .as_ref()
                .and_then(|bundle| bundle.position_pruner.as_ref())
            {
                position_pruner
                    .value_pruner
                    .maybe_set_pruner_target_db_version(version);
            }
```

**File:** storage/aptosdb/src/pruner/db_pruner.rs (L14-39)
```rust
    fn prune(&self, batch_size: usize) -> Result<Version>;

    /// Returns the progress of the pruner.
    fn progress(&self) -> Version;

    /// Sets the target version for the pruner
    fn set_target_version(&self, target_version: Version);

    /// Returns the target version for the DB pruner
    fn target_version(&self) -> Version;

    /// Returns the target version for the current pruning round - this might be different from the
    /// target_version() because we need to keep max_version in account.
    #[allow(unused)]
    fn get_current_batch_target(&self, max_versions: Version) -> Version {
        // Current target version  might be less than the target version to ensure we don't prune
        // more than max_version in one go.
        min(self.progress() + max_versions, self.target_version())
    }
    /// Records the current progress of the pruner by updating the least readable version
    fn record_progress(&self, min_readable_version: Version);

    /// True if there is pruning work pending to be done
    fn is_pruning_pending(&self) -> bool {
        self.target_version() > self.progress()
    }
```
