No vulnerability found for this question.

The premise conflates two unrelated mechanisms. Client-side QUIC congestion signals (`congestion_events`, `data_blocked`) tracked in `ClientStats`/`ConnectionCacheStats` only affect *when* packets arrive at the streamer — they have no bearing on how the leader's cost tracker admits transactions [1](#0-0) .

On the leader side, `CostTracker::would_fit` is invoked synchronously for each transaction at admission time and checks the transaction's cost against the current `block_cost` accumulator and per-account limits before it is ever added [2](#0-1) . This check is purely a function of already-admitted costs plus the new transaction's cost — it has no dependency on arrival timing, batching, or how many packets arrived "in the same window." Whether transactions arrive spread out over the slot or bunched together due to network congestion, each one is checked against the live `block_cost` state at the moment it is processed, and the ceiling (`MAX_BLOCK_UNITS` et al., defined per slot-time regime in `SlotParams`) can never be exceeded because `would_fit` rejects any transaction that would push the cumulative cost over the limit [3](#0-2) .

There is no "declared compute units must upper-bound real work performed based on arrival timing" invariant in the code — the invariant actually enforced is purely additive/synchronous per-transaction admission, which is timing-independent by construction. The `test_check_block_cost_limit` test demonstrates this: a second transaction identical to one already admitted is rejected once the cumulative cost would exceed `block_cost`, regardless of when it arrives [4](#0-3) . Client-side congestion cannot cause the tracker to admit more aggregate cost than its configured ceiling; it can at most delay when transactions get processed or dropped, which is an availability/latency concern already acknowledged as out of scope (RPC/network DoS) rather than a cost-model correctness violation.

### Citations

**File:** quic-client/src/nonblocking/quic_client.rs (L362-388)
```rust
            let new_stats = connection.stats();

            connection_stats
                .total_client_stats
                .congestion_events
                .update_stat(
                    &self.stats.congestion_events,
                    new_stats.path.congestion_events,
                );

            connection_stats
                .total_client_stats
                .streams_blocked_uni
                .update_stat(
                    &self.stats.streams_blocked_uni,
                    new_stats.frame_tx.streams_blocked_uni,
                );

            connection_stats
                .total_client_stats
                .data_blocked
                .update_stat(&self.stats.data_blocked, new_stats.frame_tx.data_blocked);

            connection_stats
                .total_client_stats
                .acks
                .update_stat(&self.stats.acks, new_stats.frame_tx.acks);
```

**File:** cost-model/src/cost_tracker.rs (L272-310)
```rust
    fn would_fit(
        &self,
        tx_cost: &TransactionCost<impl TransactionWithMeta>,
    ) -> Result<(), CostTrackerError> {
        let cost: u64 = tx_cost.sum();

        if self.block_cost().saturating_add(cost) > self.limits.block_cost {
            // check against the total package cost
            return Err(CostTrackerError::WouldExceedBlockMaxLimit);
        }

        // check if the transaction itself is more costly than the account_cost_limit
        if cost > self.limits.account_cost {
            return Err(CostTrackerError::WouldExceedAccountMaxLimit);
        }

        let allocated_accounts_data_size =
            self.allocated_accounts_data_size + Saturating(tx_cost.allocated_accounts_data_size());

        if allocated_accounts_data_size.0 > self.limits.allocated_data_size {
            return Err(CostTrackerError::WouldExceedAccountDataBlockLimit);
        }

        // check each account against account_cost_limit,
        for account_key in tx_cost.writable_accounts() {
            match self.cost_by_writable_accounts.get(account_key) {
                Some(chained_cost) => {
                    if chained_cost.saturating_add(cost) > self.limits.account_cost {
                        return Err(CostTrackerError::WouldExceedAccountMaxLimit);
                    } else {
                        continue;
                    }
                }
                None => continue,
            }
        }

        Ok(())
    }
```

**File:** runtime/src/slot_params.rs (L123-133)
```rust
pub(crate) const LEGACY_SLOT_PARAMS: SlotParams = SlotParams {
    ns_per_slot: 400_000_000,
    slots_per_year: 78_892_314.984,
    hashes_per_tick: Some(LEGACY_HASHES_PER_TICK),
    cost_tracker_limits: CostTrackerLimits::new(24_000_000, 60_000_000, 100_000_000),
    max_data_shreds_per_slot: 32_768,
    max_code_shreds_per_slot: 32_768,
    max_entry_bytes_per_slot: 20 * 1024 * 1024,
    partitioned_epoch_rewards_stake_account_stores_per_block: 4096,
    vat_to_burn_per_epoch: 1_600_000_000,
};
```

**File:** runtime/src/transaction_execution.rs (L310-349)
```rust
    #[test]
    fn test_check_block_cost_limit() {
        let dummy_leader_pubkey = solana_pubkey::new_rand();
        let GenesisConfigInfo {
            genesis_config,
            mint_keypair,
            ..
        } = create_genesis_config_with_leader(500, &dummy_leader_pubkey, 100);
        let bank = Bank::new_for_tests(&genesis_config);

        let tx =
            RuntimeTransaction::from_transaction_for_tests(solana_system_transaction::transfer(
                &mint_keypair,
                &Pubkey::new_unique(),
                1,
                genesis_config.hash(),
            ));
        let mut tx_cost = CostModel::calculate_cost(&tx, &bank.feature_set);
        let actual_execution_cu = 1;
        let actual_loaded_accounts_data_size = 64 * 1024;
        tx_cost.programs_execution_cost = actual_execution_cu;
        tx_cost.loaded_accounts_data_size_cost =
            CostModel::calculate_loaded_accounts_data_size_cost(
                actual_loaded_accounts_data_size,
                &bank.feature_set,
            );
        // set block-limit to be able to just have one transaction
        let block_limit = tx_cost.sum();
        bank.write_cost_tracker()
            .unwrap()
            .set_limits(CostTrackerLimits::new(u64::MAX, block_limit, u64::MAX));

        let tx_costs = vec![None, Some(tx_cost), None];
        // The transaction will fit when added the first time
        assert!(check_block_cost_limits(&bank, &tx_costs).is_ok());
        // But adding a second time will exceed the block limit
        assert_eq!(
            Err(TransactionError::WouldExceedMaxBlockCostLimit),
            check_block_cost_limits(&bank, &tx_costs)
        );
```
