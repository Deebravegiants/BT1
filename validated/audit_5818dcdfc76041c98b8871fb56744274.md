No vulnerability found for this question.

**Reasoning:** `BufferedState::new_at_snapshot` is only invoked once per process, during `StateStore::new` at DB (re)open time, and the `last_snapshot` it receives is always derived from a single, synchronous read of the actual on-disk state merkle DB tip via `get_state_snapshot_version_before(Version::MAX)` in `create_buffered_state_from_latest_snapshot`, before any commit-pipeline thread is spawned [1](#0-0) .

Both `out_persisted_state.hack_reset(last_snapshot.clone())` and the `commit_thread` closure that captures `last_snapshot.clone()` are populated from the exact same `state.clone()` value at construction time [2](#0-1) , so there is no window in which the persisted-state view and the merkle-committer's base snapshot could diverge — they are set atomically from one source, single-threaded, prior to any commit being enqueued. `hack_reset` itself documents this constraint ("Can only be used when no on the fly commit is in the queue") [3](#0-2) , which matches how it's actually used in this codebase.

A "DB reopen with `last_snapshot` older than what the merkle committer already durably wrote" scenario would require calling `new_at_snapshot` a second time within the same live process while a prior commit pipeline's writes are still outstanding — but `StateStore::new` only calls it once at startup, and a real reopen means the whole process (and its commit thread) restarted, so `get_state_snapshot_version_before` at the new startup will read whatever was truly durably persisted, not something behind it. There is no unprivileged transaction, package, view, authenticator, API, or proof input that can trigger this hypothesized double-initialization with a stale `last_snapshot`, so this does not cross the review's required entrypoint gate, and no code path exists in this repository that produces the described divergence.

### Citations

**File:** storage/aptosdb/src/state_store/mod.rs (L763-828)
```rust

        let latest_snapshot_version = state_db
            .state_merkle_db
            .get_state_snapshot_version_before(Version::MAX)
            .expect("Failed to query latest node on initialization.");

        info!(
            num_transactions = num_transactions,
            latest_snapshot_version = latest_snapshot_version,
            "Initializing BufferedState."
        );
        let latest_snapshot_root_hash = if let Some(version) = latest_snapshot_version {
            state_db
                .state_merkle_db
                .get_root_hash(version)
                .expect("Failed to query latest checkpoint root hash on initialization.")
        } else {
            *SPARSE_MERKLE_PLACEHOLDER_HASH
        };
        let hot_state_root_hash = if !hot_state_config.delete_on_restart
            && let Some(version) = latest_snapshot_version
        {
            match state_db
                .hot_state_merkle_db
                .get_root_hash_option(version)
                .expect("Failed to query hot state root hash on initialization.")
            {
                Some(root_hash) => {
                    info!(
                        latest_snapshot_version = version,
                        hot_state_root_hash = root_hash,
                        "Loaded hot state root hash at latest snapshot version."
                    );
                    root_hash
                },
                None => {
                    // No hot state root at `version` yet (e.g. before the hot state has ever
                    // been committed) — fall back to the placeholder.
                    // TODO(HotState): revisit when we delete_on_restart is not true by default.
                    info!(
                        latest_snapshot_version = version,
                        "No hot state root hash found at latest snapshot version; falling back to placeholder hash."
                    );
                    *SPARSE_MERKLE_PLACEHOLDER_HASH
                },
            }
        } else {
            *SPARSE_MERKLE_PLACEHOLDER_HASH
        };
        let usage = state_db.get_state_storage_usage(latest_snapshot_version)?;

        let state = StateWithSummary::new_at_version_with_hot_state_metadata(
            latest_snapshot_version,
            hot_state_root_hash,
            latest_snapshot_root_hash,
            usage,
            hot_state_config,
            hot_state_metadata,
        );
        let mut buffered_state = BufferedState::new_at_snapshot(
            state_db,
            state.clone(),
            buffered_state_target_items,
            out_current_state.clone(),
            out_persisted_state.clone(),
        );
```

**File:** storage/aptosdb/src/state_store/buffered_state.rs (L107-127)
```rust
        let arc_state_db = Arc::clone(state_db);
        *out_current_state.lock() =
            LedgerStateWithSummary::new_at_checkpoint(last_snapshot.clone());
        out_persisted_state.hack_reset(last_snapshot.clone());

        let merklize_state_db = Arc::clone(&arc_state_db);
        let persisted_state_clone = out_persisted_state.clone();
        let commit_thread = spawn_commit_pipeline(
            "state-committer",
            ASYNC_COMMIT_CHANNEL_BUFFER_SIZE as usize,
            "state_batch_committer",
            STATE_BATCH_CHANNEL_SIZE,
            last_snapshot.clone(),
            move |batch_receiver| {
                StateMerkleBatchCommitter::new(arc_state_db, batch_receiver, persisted_state_clone)
                    .run();
            },
            move |last_snapshot, input| {
                merklize_main_state(&merklize_state_db, last_snapshot, input)
            },
        );
```

**File:** storage/aptosdb/src/state_store/persisted_state.rs (L77-82)
```rust
    // n.b. Can only be used when no on the fly commit is in the queue.
    pub fn hack_reset(&self, state_with_summary: StateWithSummary) {
        let (state, summary) = state_with_summary.into_inner();
        *self.summary.lock() = summary;
        self.hot_state.hack_reset(state);
    }
```
