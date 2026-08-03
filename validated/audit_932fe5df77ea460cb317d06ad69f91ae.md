No vulnerability found for this question.

**Analysis:**

The premise conflates two unrelated mechanisms:

1. `TOTAL_SUPPLY_STATE_KEY` in [1](#0-0)  is a single, fixed, well-known state key corresponding to the legacy `aptos_framework::coin::CoinInfo<AptosCoin>` supply aggregator table item — not a per-FA-store or per-metadata-object supply value. `WriteSet::get_total_supply()` only reads/decodes this one specific key [2](#0-1) .

2. `aggregate_and_update_total_supply` in the sharded block executor uses this to reconcile deltas of the *single global legacy AptosCoin aggregator* across shards after parallel execution, because each shard executes with an overridden base value for that one aggregator (`TOTAL_SUPPLY_AGGR_BASE_VAL`) [3](#0-2) . It is purely an internal, in-place patch of that one write-set entry via `TransactionOutput::update_total_supply` [4](#0-3) , and does not touch, read, or invalidate any other resource writes in the transaction's write set, including `FungibleStore`/`ConcurrentSupply`/`Metadata` resources belonging to a fungible-asset store held by a resource account.

A transaction that mutates a resource-account-held FA store (transfer/mint/burn on a custom fungible asset) writes to state keys under that FA metadata object's address (`ConcurrentSupply`/`Supply`/`FungibleStore` resources, per `aptos-move/framework/aptos-framework/sources/fungible_asset.move` `increase_supply`/`decrease_supply` at lines 1321-1363) [5](#0-4)  — this is a completely different, independent write to a completely different state key, unrelated to `TOTAL_SUPPLY_STATE_KEY`. Whether `get_total_supply()` returns `Some` or `None` for that txn has zero bearing on whether the FA store's own balance/supply write op is present, correct, or committed; that write is applied to the DB unmodified through the normal state-commit path regardless of this aggregator-reconciliation hack.

Consequently:
- There is no "stale total_supply" exposed for an FA store — FA stores don't have their supply represented via `TOTAL_SUPPLY_STATE_KEY` at all.
- The reconciliation logic in `aggregate_and_update_total_supply` only ever affects the legacy AptosCoin global supply aggregator entry, and only within the internal sharded-execution reconciliation path, which is validator-internal execution infrastructure, not something directly influenced by unprivileged transaction/API/bytecode input in a way that breaks custody of any asset.
- No controller, holder, freeze, or transfer-authority state changes as a result of this code; it is a bookkeeping value only, and even a mismatch here would be, at most, a cosmetic reporting discrepancy on the legacy coin aggregator value — explicitly excluded by the decision standard ("Reject anything that... only produces cosmetic or event-level mismatch").

This does not cross a custody boundary and does not match any of the required custody pivots (ownership, transfer authority, freeze, upgrade, or recovery rights).

### Citations

**File:** types/src/write_set.rs (L27-37)
```rust
pub static TOTAL_SUPPLY_STATE_KEY: Lazy<StateKey> = Lazy::new(|| {
    StateKey::table_item(
        &"1b854694ae746cdbd8d44186ca4929b2b337df21d1c74633be19b2710552fdca"
            .parse()
            .unwrap(),
        &[
            6, 25, 220, 41, 160, 170, 200, 250, 20, 103, 20, 5, 142, 141, 214, 210, 208, 243, 189,
            245, 246, 51, 25, 7, 191, 145, 243, 172, 216, 30, 105, 53,
        ],
    )
});
```

**File:** types/src/write_set.rs (L696-703)
```rust
    pub fn get_total_supply(&self) -> Option<u128> {
        let value = self
            .value_writes()
            .get(&TOTAL_SUPPLY_STATE_KEY)
            .and_then(|op| op.bytes())
            .map(|bytes| bcs::from_bytes::<u128>(bytes));
        value.transpose().map_err(anyhow::Error::msg).unwrap()
    }
```

**File:** aptos-move/aptos-vm/src/sharded_block_executor/sharded_aggregator_service.rs (L168-213)
```rust
pub fn aggregate_and_update_total_supply<S: StateView>(
    sharded_output: &mut Vec<Vec<Vec<TransactionOutput>>>,
    global_output: &mut [TransactionOutput],
    state_view: &S,
    executor_thread_pool: Arc<rayon::ThreadPool>,
) {
    let num_shards = sharded_output.len();
    let num_rounds = sharded_output[0].len();

    // The first element is 0, which is the delta for shard 0 in round 0. +1 element will contain
    // the delta for the global shard
    let mut aggr_total_supply_delta = vec![DeltaU128::default(); num_shards * num_rounds + 1];

    // No need to parallelize this as the runtime is O(num_shards * num_rounds)
    // TODO: Get this from the individual shards while getting 'sharded_output'
    let mut aggr_ts_idx = 1;
    for round in 0..num_rounds {
        sharded_output.iter().for_each(|shard_output| {
            let mut curr_delta = DeltaU128::default();
            // Though we expect all the txn_outputs to have total_supply, there can be
            // exceptions like 'block meta' (first txn in the block) and 'chkpt info' (last txn
            // in the block) which may not have total supply. Hence we iterate till we find the
            // last txn with total supply.
            for txn in shard_output[round].iter().rev() {
                if let Some(last_txn_total_supply) = txn.write_set().get_total_supply() {
                    curr_delta =
                        DeltaU128::get_delta(last_txn_total_supply, TOTAL_SUPPLY_AGGR_BASE_VAL);
                    break;
                }
            }
            aggr_total_supply_delta[aggr_ts_idx] =
                curr_delta + aggr_total_supply_delta[aggr_ts_idx - 1];
            aggr_ts_idx += 1;
        });
    }

    // The txn_outputs contain 'txn_total_supply' with
    // 'CrossShardStateViewAggrOverride::total_supply_aggr_base_val' as the base value.
    // The actual 'total_supply_base_val' is in the state_view.
    // The 'delta' for the shard/round is in aggr_total_supply_delta[round * num_shards + shard_id + 1]
    // For every txn_output, we have to compute
    //      txn_total_supply = txn_total_supply - CrossShardStateViewAggrOverride::total_supply_aggr_base_val + total_supply_base_val + delta
    // While 'txn_total_supply' is u128, the intermediate computation can be negative. So we use
    // DeltaU128 to handle any intermediate underflow of u128.
    let total_supply_base_val: u128 = get_state_value(&TOTAL_SUPPLY_STATE_KEY, state_view).unwrap();
    let base_val_delta = DeltaU128::get_delta(total_supply_base_val, TOTAL_SUPPLY_AGGR_BASE_VAL);
```

**File:** types/src/transaction/mod.rs (L2095-2102)
```rust
    // This is a special function to update the total supply in the write set. 'TransactionOutput'
    // already has materialized write set, but in case of sharding support for total_supply, we
    // want to update the total supply in the write set by aggregating the total supply deltas from
    // each shard. However, is costly to materialize the entire write set again, hence we have this
    // inplace update hack.
    pub fn update_total_supply(&mut self, value: u128) {
        self.write_set.update_total_supply(value);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L1337-1363)
```text
    /// Decrease the supply of a fungible asset by burning.
    fun decrease_supply<T: key>(metadata: &Object<T>, amount: u64) acquires Supply, ConcurrentSupply {
        if (amount == 0) { return };
        let metadata_address = metadata.object_address();

        if (exists<ConcurrentSupply>(metadata_address)) {
            let supply = borrow_global_mut<ConcurrentSupply>(metadata_address);

            assert!(
                supply.current.try_sub(amount as u128),
                error::out_of_range(ESUPPLY_UNDERFLOW)
            );
        } else if (exists<Supply>(metadata_address)) {
            assert!(
                exists<Supply>(metadata_address),
                error::not_found(ESUPPLY_NOT_FOUND)
            );
            let supply = borrow_global_mut<Supply>(metadata_address);
            assert!(
                supply.current >= (amount as u128),
                error::invalid_state(ESUPPLY_UNDERFLOW)
            );
            supply.current -= (amount as u128);
        } else {
            assert!(false, error::not_found(ESUPPLY_NOT_FOUND));
        }
    }
```
