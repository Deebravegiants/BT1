### Title
`get_uncertified_validator_proposals` Returns Duplicate Account Proposals Without Deduplication, Causing Wrong Stake at Epoch Boundary - (`chain/chain/src/spice/core.rs`)

### Summary

In the SPICE execution path, `get_uncertified_validator_proposals` can return a `Vec<ValidatorStake>` containing multiple entries for the same `AccountId` (one per uncertified chunk height). Its caller `prev_validator_proposals` returns this list raw, without deduplication. These duplicates propagate into `BlockInfo.proposals`, where `EpochInfoAggregator::update_tail` processes them with `or_insert` (first-wins semantics), silently discarding the more-recent, authoritative proposal. The function's own doc comment acknowledges the problem but delegates deduplication to the caller, which never performs it.

### Finding Description

`get_uncertified_validator_proposals` collects validator proposals from all uncertified chunks for a given shard, sorts them by block height, and returns them as a flat `Vec`: [1](#0-0) 

The doc comment explicitly states: *"If multiple uncertified chunks contain proposals for the same account, the most recent one (last in iteration order) should be kept by the caller's fold/insert logic."* The test `test_uncertified_validator_proposals_multiple_heights_same_account` confirms this returns two entries for the same account: [2](#0-1) 

The direct caller `prev_validator_proposals` returns the raw result with no deduplication: [3](#0-2) 

These proposals flow into `BlockInfo.proposals` and are processed by `EpochInfoAggregator::update_tail` using `or_insert`, which keeps the **first** (oldest, lower-stake) proposal and silently drops the later one: [4](#0-3) 

The aggregator's `all_proposals` (a `BTreeMap`) is then passed to `proposals_to_epoch_info`, which only has a `debug_assert!` (not enforced in release builds) that proposals contain no duplicates: [5](#0-4) 

### Impact Explanation

At an epoch boundary in SPICE mode, if a validator submits staking transactions that land in two different uncertified chunks (e.g., first an unstake, then a re-stake), the epoch manager uses the wrong (earlier) stake amount for validator selection. Concretely:

- A validator who re-staked at a higher amount is selected with the lower, stale stake.
- A validator who unstaked and then re-staked may be incorrectly kicked out because the zero-stake proposal is kept instead of the re-stake.
- The `last_proposals` used in `update_validator_accounts` to compute stake returns is wrong, causing incorrect locked-balance accounting. [6](#0-5) 

### Likelihood Explanation

Any unprivileged user can submit two staking transactions from the same account. In SPICE mode with an endorsement delay (as used in integration tests), it is realistic for both transactions to land in separate uncertified chunks near an epoch boundary. The test `test_spice_uncertified_restake_prevents_stake_return` demonstrates exactly this scenario: [7](#0-6) 

The SPICE feature is currently gated by `protocol_feature_spice`, so this is not yet active on mainnet, but the root cause exists in production code paths.

### Recommendation

Deduplicate proposals by account ID inside `prev_validator_proposals` (or inside `get_uncertified_validator_proposals`) before returning, keeping the last (highest-height) proposal per account. For example, fold the sorted `height_proposals` into a `HashMap<AccountId, ValidatorStake>` using `insert` (last-wins), then collect the values. This matches the semantics described in the doc comment and mirrors how `apply_epoch_update_to_proposals` handles duplicates via `proposals_by_account.insert`: [8](#0-7) 

### Proof of Concept

1. Enable `protocol_feature_spice` and set `endorsement_delay = 4` (as in existing tests).
2. Submit `StakeAction { stake: 0 }` (unstake) for account `test0` — lands in uncertified chunk at height H.
3. Submit `StakeAction { stake: INIT_STAKE }` (re-stake) for `test0` — lands in uncertified chunk at height H+1.
4. At the epoch boundary, `get_uncertified_validator_proposals` returns `[test0@0, test0@INIT_STAKE]`.
5. `prev_validator_proposals` returns this list unchanged.
6. `EpochInfoAggregator::update_tail` processes `test0@0` first via `or_insert`; `test0@INIT_STAKE` is silently dropped.
7. `proposals_to_epoch_info` receives `test0@0`, treating `test0` as having unstaked, and kicks them out of the validator set — even though they re-staked. [9](#0-8)

### Citations

**File:** chain/chain/src/spice/core.rs (L137-162)
```rust
    pub fn get_uncertified_validator_proposals(
        &self,
        block_hash: &CryptoHash,
        shard_id: ShardId,
    ) -> Result<Vec<ValidatorStake>, Error> {
        let uncertified_chunks = self.get_uncertified_chunks(block_hash)?;
        let shard_uncertified_chunks: Vec<_> = uncertified_chunks
            .into_iter()
            .filter(|info| info.chunk_id.shard_id == shard_id)
            .collect();
        let mut height_proposals: Vec<(BlockHeight, Vec<ValidatorStake>)> = Vec::new();
        for info in &shard_uncertified_chunks {
            let chunk_extra = self.get_trusted_chunk_extra(&info.chunk_id)?;
            let proposals: Vec<ValidatorStake> = chunk_extra.validator_proposals().collect();
            if !proposals.is_empty() {
                let height = self.chain_store.get_block_height(&info.chunk_id.block_hash)?;
                height_proposals.push((height, proposals));
            }
        }
        height_proposals.sort_by_key(|(h, _)| *h);
        debug_assert!(
            height_proposals.windows(2).all(|w| w[0].0 != w[1].0),
            "multiple uncertified chunks at the same height for shard {shard_id}"
        );
        Ok(height_proposals.into_iter().flat_map(|(_, proposals)| proposals).collect())
    }
```

**File:** chain/chain/src/spice/core.rs (L167-177)
```rust
    pub fn prev_validator_proposals(
        &self,
        prev_block_hash: &CryptoHash,
        shard_id: ShardId,
    ) -> Result<Vec<ValidatorStake>, Error> {
        if self.epoch_manager.is_next_block_epoch_start(prev_block_hash)? {
            self.get_uncertified_validator_proposals(prev_block_hash, shard_id)
        } else {
            Ok(vec![])
        }
    }
```

**File:** chain/chain/src/spice/tests/core.rs (L1864-1896)
```rust
fn test_uncertified_validator_proposals_multiple_heights_same_account() {
    let (mut chain, core_reader) = setup();
    let genesis = chain.genesis_block();

    let block1 = build_block(&mut chain, &genesis, vec![]);
    process_block(&mut chain, block1.clone());

    let block2 = build_block(&mut chain, &block1, vec![]);
    process_block(&mut chain, block2.clone());

    let shard_id = ShardId::new(0);
    save_chunk_extra_for_block(
        &mut chain,
        &block1,
        shard_id,
        make_chunk_extra_with_proposals(vec![test_proposal("test0", 100)]),
    );
    save_chunk_extra_for_block(
        &mut chain,
        &block2,
        shard_id,
        make_chunk_extra_with_proposals(vec![test_proposal("test0", 200)]),
    );

    let result = core_reader.get_uncertified_validator_proposals(block2.hash(), shard_id).unwrap();
    // Both proposals returned in height order. The caller's fold/insert keeps
    // the last one (height of block2, stake=200) for "test0".
    assert_eq!(result.len(), 2);
    assert_eq!(result[0].account_id().as_str(), "test0");
    assert_eq!(result[0].stake(), Balance::from_near(100));
    assert_eq!(result[1].account_id().as_str(), "test0");
    assert_eq!(result[1].stake(), Balance::from_near(200));
}
```

**File:** chain/epoch-manager/src/epoch_info_aggregator.rs (L200-203)
```rust
        // Step 4: update proposals
        for proposal in block_info.proposals_iter() {
            self.all_proposals.entry(proposal.account_id().clone()).or_insert(proposal);
        }
```

**File:** chain/epoch-manager/src/validator_selection.rs (L179-183)
```rust
    debug_assert!(
        proposals.iter().map(|stake| stake.account_id()).collect::<HashSet<_>>().len()
            == proposals.len(),
        "Proposals should not have duplicates"
    );
```

**File:** chain/epoch-manager/src/validator_selection.rs (L297-312)
```rust
    let mut proposals_by_account = HashMap::new();
    for p in proposals {
        let account_id = p.account_id();
        if validator_kickout.contains_key(account_id) {
            let account_id = p.take_account_id();
            stake_change.insert(account_id, Balance::ZERO);
        } else if let Some(ValidatorKickoutReason::ProtocolVersionTooOld { .. }) =
            prev_epoch_info.validator_kickout().get(account_id)
        {
            // If the validator was kicked out because of an old protocol version in T-1,
            // it is not allowed back in T.
            continue;
        } else {
            stake_change.insert(account_id.clone(), p.stake());
            proposals_by_account.insert(account_id.clone(), p);
        }
```

**File:** runtime/runtime/src/lib.rs (L1609-1616)
```rust
                let last_proposal = *validator_accounts_update
                    .last_proposals
                    .get(account_id)
                    .unwrap_or(&Balance::ZERO);
                let return_stake = account
                    .locked()
                    .checked_sub(max(*max_of_stakes, last_proposal))
                    .ok_or_else(|| {
```

**File:** test-loop-tests/src/tests/stake_nodes.rs (L413-505)
```rust
/// Verifies that a validator who unstakes and then re-stakes in an uncertified chunk
/// near the epoch boundary does NOT have their stake returned. The re-stake proposal
/// from the uncertified chunk should be picked up by get_uncertified_validator_proposals.
#[test]
#[cfg_attr(not(feature = "protocol_feature_spice"), ignore)]
fn test_spice_uncertified_restake_prevents_stake_return() {
    init_test_logger();

    let epoch_length: u64 = 10;
    let endorsement_delay: u64 = 4;
    let unstaker_idx = 0;
    let validators_spec = create_validators_spec(4, 1);
    let accounts = validators_spec_clients(&validators_spec);
    let unstaker = accounts[unstaker_idx].clone();
    let unstaker_key = create_test_signer(unstaker.as_str()).public_key();

    let mut env = TestLoopBuilder::new()
        .validators_spec(validators_spec)
        .epoch_length(epoch_length)
        .add_user_accounts(&accounts, TESTING_INIT_BALANCE)
        .max_inflation_rate(Rational32::new(0, 1))
        .config_modifier(move |config, idx| {
            // TODO(spice): Here, we force unstaker to retain memtrie for the
            // unloaded shard. Memtrie retention needs to be fixed for spice to
            // wait until certification of the last block of the prior epoch.
            if idx == unstaker_idx {
                config.tracked_shards_config = TrackedShardsConfig::AllShards;
            }
        })
        .delay_warmup()
        .build();
    env.delay_endorsements_propagation(endorsement_delay);
    let mut env = env.warmup();

    let genesis_height = env.node(unstaker_idx).client().chain.genesis().height();
    let initial_stake = env.node(unstaker_idx).view_account_query(&unstaker).unwrap().locked;

    // Submit unstake (stake = 0) in the first epoch.
    let unstake_tx = env.node(unstaker_idx).tx_from_actions(
        &unstaker,
        &unstaker,
        vec![Action::Stake(Box::new(StakeAction {
            stake: Balance::ZERO,
            public_key: unstaker_key.clone(),
        }))],
    );
    env.node_runner(unstaker_idx).run_tx(unstake_tx, Duration::seconds(30));

    // Advance to a few blocks before the E4->E5 boundary where stake return would
    // happen. Unstake in E0 -> active in E0,E1 -> inactive from E2 -> 3-epoch window
    // covers E2,E3,E4 with 0 stake -> return at E4->E5 boundary.
    let epoch_boundary = genesis_height + 5 * epoch_length;
    let restake_submit_height = epoch_boundary - 3;
    // The restake must land within endorsement_delay of the epoch boundary
    // to make sure the premise of the test holds.
    assert!(restake_submit_height + endorsement_delay > epoch_boundary);
    env.node_runner(unstaker_idx).run_until_head_height(restake_submit_height);

    // Submit re-stake near the end of E4. With endorsement delay, this tx will
    // land in an uncertified chunk, and its stake proposal should be picked up
    // by get_uncertified_validator_proposals at the epoch boundary.
    let restake_tx = env.node(unstaker_idx).tx_from_actions(
        &unstaker,
        &unstaker,
        vec![Action::Stake(Box::new(StakeAction {
            stake: initial_stake,
            public_key: unstaker_key,
        }))],
    );
    env.node(unstaker_idx).submit_tx(restake_tx);

    // Run past the epoch boundary, plus extra blocks for execution to certify.
    env.node_runner(unstaker_idx).run_until_head_height(epoch_boundary + endorsement_delay + 2);

    // Verify the re-stake proposal landed in an uncertified chunk at the epoch boundary.
    let client = env.node(unstaker_idx).client();
    let last_block_hash =
        client.chain.chain_store.get_block_hash_by_height(epoch_boundary - 1).unwrap();
    let uncertified_proposals = client
        .chain
        .spice_core_reader
        .get_uncertified_validator_proposals(&last_block_hash, ShardId::new(0))
        .unwrap();
    assert!(
        uncertified_proposals.iter().any(|p| p.account_id() == &unstaker),
        "re-stake proposal should be in uncertified chunks, got: {:?}",
        uncertified_proposals
    );

    // Verify that the unstaker's locked balance was NOT returned.
    let account = env.node(unstaker_idx).view_account_query(&unstaker).unwrap();
    assert_eq!(account.locked, initial_stake, "stake should NOT have been returned");
}
```
