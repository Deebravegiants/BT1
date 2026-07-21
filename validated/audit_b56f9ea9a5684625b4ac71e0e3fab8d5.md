### Title
Pending-block `starknet_estimateFee` always silently uses `StarknetVersion::LATEST` constants instead of the actual pending block version — (`crates/apollo_rpc_execution/src/lib.rs`)

---

### Summary

`create_block_context` unconditionally queries storage for the Starknet version of the pending block number (`N+1`), which does not yet exist in storage. `get_starknet_version` returns `None` for any block number `>= header_marker`, so the code silently falls back to `StarknetVersion::LATEST`. The actual pending block version (available in `ClientPendingData`) is dropped during conversion to `ExecutionPendingData` and is never consulted. Any unprivileged RPC client calling `starknet_estimateFee` or `starknet_simulateTransactions` with `block_id=Tag::Pending` receives fee estimates computed against the wrong `VersionedConstants`.

---

### Finding Description

**Step 1 — `block_number` is set to the non-existent pending block number.**

In `create_block_context`, when `maybe_pending_data = Some(...)`, the local `block_number` is set to `block_context_number.unchecked_next()` (i.e., `N+1`): [1](#0-0) 

**Step 2 — `get_starknet_version(N+1)` always returns `None`.**

`get_starknet_version` has an explicit early-return guard: if `block_number >= header_marker`, it returns `Ok(None)`. Since the pending block (`N+1`) is exactly the header marker, this guard fires unconditionally: [2](#0-1) 

This is confirmed by the storage test, which asserts `get_starknet_version(BlockNumber(6))` is `None` when only blocks 0–5 are stored: [3](#0-2) 

**Step 3 — Silent fallback to `StarknetVersion::LATEST`.**

The `None` result is silently replaced with `StarknetVersion::LATEST`, which then selects `VersionedConstants` for the latest version the binary knows about: [4](#0-3) 

**Step 4 — The actual pending block version is available but dropped.**

`ClientPendingData` carries a `starknet_version` string on the pending block: [5](#0-4) 

However, `client_pending_data_to_execution_pending_data` explicitly omits it when constructing `ExecutionPendingData`: [6](#0-5) 

`ExecutionPendingData` has no `starknet_version` field, so `create_block_context` has no way to read the correct version even if it tried.

**Step 5 — Different versions have materially different constants.**

The test `test_get_versioned_constants` confirms that `invoke_tx_max_n_steps` changes from 3 M (V0_13_0) → 4 M (V0_13_1) → 10 M (V0_13_2), and the blockifier defines 14 distinct versioned-constants files: [7](#0-6) 

---

### Impact Explanation

Every call to `starknet_estimateFee`, `starknet_simulateTransactions`, or `starknet_call` with `block_id=Tag::Pending` uses `VersionedConstants` for `StarknetVersion::LATEST` rather than the actual pending block version. During any period where the binary's `LATEST` differs from the live network version (e.g., a node binary updated ahead of a protocol upgrade, or a node binary lagging behind), fee estimates are computed with the wrong step limits, syscall gas costs, and resource bounds. The returned fee is authoritative-looking and is used by wallets and dApps to set resource bounds on submitted transactions, causing systematic over- or under-estimation.

This satisfies: **High — RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value.**

---

### Likelihood Explanation

The bug fires on **every** pending-block fee estimation call — it is not conditional on any race or timing. The only question is whether `LATEST` matches the live network version. This mismatch is guaranteed during any protocol upgrade window and is also present whenever a node operator runs a binary that is ahead of or behind the network version. The attacker path requires only a standard unauthenticated `starknet_estimateFee` RPC call.

---

### Recommendation

1. Add a `starknet_version: Option<StarknetVersion>` field to `ExecutionPendingData` in `crates/apollo_rpc_execution/src/objects.rs`.
2. Populate it in `client_pending_data_to_execution_pending_data` by parsing `client_pending_data.block.starknet_version()`.
3. In `create_block_context`, when `maybe_pending_data` is `Some`, read `starknet_version` from `pending_data.starknet_version` first; fall back to `get_starknet_version(block_context_number)` (block `N`, not `N+1`) only if absent; use `LATEST` only as a last resort.

---

### Proof of Concept

```rust
// In crates/apollo_rpc_execution/src/execution_test.rs (integration style)
#[test]
fn pending_fee_estimation_uses_latest_not_actual_version() {
    // Store block N with version V0_13_2
    let ((reader, mut writer), _tmp) = get_test_storage();
    let header = BlockHeader {
        block_header_without_hash: BlockHeaderWithoutHash {
            block_number: BlockNumber(0),
            starknet_version: StarknetVersion::try_from("0.13.2".to_string()).unwrap(),
            ..Default::default()
        },
        ..Default::default()
    };
    writer.begin_rw_txn().unwrap()
        .append_header(BlockNumber(0), &header).unwrap()
        .commit().unwrap();

    // Simulate what create_block_context does for pending:
    // block_number = 0.unchecked_next() = 1
    let block_number = BlockNumber(0).unchecked_next(); // = BlockNumber(1)
    let version = reader.begin_ro_txn().unwrap()
        .get_starknet_version(block_number).unwrap();

    // This is None because block 1 >= header_marker(1)
    assert!(version.is_none());

    // The fallback is LATEST, not V0_13_2
    let effective = version.unwrap_or(StarknetVersion::LATEST);
    assert_ne!(
        effective,
        StarknetVersion::try_from("0.13.2".to_string()).unwrap(),
        "Bug: pending fee estimation uses LATEST, not the actual pending block version"
    );
}
```

### Citations

**File:** crates/apollo_rpc_execution/src/lib.rs (L340-349)
```rust
    ) = match maybe_pending_data {
        Some(pending_data) => (
            block_context_number.unchecked_next(),
            pending_data.timestamp,
            pending_data.l1_gas_price,
            pending_data.l1_data_gas_price,
            pending_data.l2_gas_price,
            pending_data.sequencer,
            pending_data.l1_da_mode,
        ),
```

**File:** crates/apollo_rpc_execution/src/lib.rs (L370-408)
```rust
    let starknet_version = storage_reader
        .begin_ro_txn()?
        .get_starknet_version(block_number)?
        .unwrap_or(StarknetVersion::LATEST);
    let block_info = BlockInfo {
        block_timestamp,
        sequencer_address: sequencer_address.0,
        use_kzg_da,
        block_number,
        // TODO(yair): What to do about blocks pre 0.13.1 where the data gas price were 0?
        gas_prices: GasPrices {
            eth_gas_prices: GasPriceVector {
                l1_gas_price: NonzeroGasPrice::new(l1_gas_price.price_in_wei)
                    .unwrap_or(NonzeroGasPrice::MIN),
                l1_data_gas_price: NonzeroGasPrice::new(l1_data_gas_price.price_in_wei)
                    .unwrap_or(NonzeroGasPrice::MIN),
                l2_gas_price: NonzeroGasPrice::new(l2_gas_price.price_in_wei)
                    .unwrap_or(NonzeroGasPrice::MIN),
            },
            strk_gas_prices: GasPriceVector {
                l1_gas_price: NonzeroGasPrice::new(l1_gas_price.price_in_fri)
                    .unwrap_or(NonzeroGasPrice::MIN),
                l1_data_gas_price: NonzeroGasPrice::new(l1_data_gas_price.price_in_fri)
                    .unwrap_or(NonzeroGasPrice::MIN),
                l2_gas_price: NonzeroGasPrice::new(l2_gas_price.price_in_fri)
                    .unwrap_or(NonzeroGasPrice::MIN),
            },
        },
        starknet_version,
    };
    let chain_info = ChainInfo {
        chain_id,
        fee_token_addresses: FeeTokenAddresses {
            strk_fee_token_address: execution_config.strk_fee_contract_address,
            eth_fee_token_address: execution_config.eth_fee_contract_address,
        },
        is_l3: false,
    };
    let versioned_constants = VersionedConstants::get(&starknet_version)?;
```

**File:** crates/apollo_storage/src/header.rs (L256-258)
```rust
        if block_number >= self.get_header_marker()? {
            return Ok(None);
        }
```

**File:** crates/apollo_storage/src/header_test.rs (L227-229)
```rust
    let block_6_starknet_version =
        reader.begin_ro_txn().unwrap().get_starknet_version(BlockNumber(6)).unwrap();
    assert!(block_6_starknet_version.is_none());
```

**File:** crates/apollo_starknet_client/src/reader/objects/pending_data.rs (L123-128)
```rust
    pub fn starknet_version(&self) -> String {
        match self {
            PendingBlockOrDeprecated::Deprecated(block) => block.starknet_version.clone(),
            PendingBlockOrDeprecated::Current(block) => block.starknet_version.clone(),
        }
    }
```

**File:** crates/apollo_rpc/src/pending.rs (L9-23)
```rust
    ExecutionPendingData {
        storage_diffs: client_pending_data.state_update.state_diff.storage_diffs,
        deployed_contracts: client_pending_data.state_update.state_diff.deployed_contracts,
        declared_classes: client_pending_data.state_update.state_diff.declared_classes,
        old_declared_contracts: client_pending_data.state_update.state_diff.old_declared_contracts,
        nonces: client_pending_data.state_update.state_diff.nonces,
        replaced_classes: client_pending_data.state_update.state_diff.replaced_classes,
        classes: pending_classes,
        timestamp: client_pending_data.block.timestamp(),
        l1_gas_price: client_pending_data.block.l1_gas_price(),
        l1_data_gas_price: client_pending_data.block.l1_data_gas_price(),
        l2_gas_price: client_pending_data.block.l2_gas_price(),
        l1_da_mode: client_pending_data.block.l1_da_mode(),
        sequencer: client_pending_data.block.sequencer_address(),
    }
```

**File:** crates/blockifier/src/blockifier_versioned_constants.rs (L40-60)
```rust
define_versioned_constants!(
    VersionedConstants,
    RawVersionedConstants,
    VersionedConstantsError,
    StarknetVersion::V0_13_0,
    "resources/versioned_constants_diff_regression",
    (V0_13_0, "../resources/blockifier_versioned_constants_0_13_0.json"),
    (V0_13_1, "../resources/blockifier_versioned_constants_0_13_1.json"),
    (V0_13_1_1, "../resources/blockifier_versioned_constants_0_13_1_1.json"),
    (V0_13_2, "../resources/blockifier_versioned_constants_0_13_2.json"),
    (V0_13_2_1, "../resources/blockifier_versioned_constants_0_13_2_1.json"),
    (V0_13_3, "../resources/blockifier_versioned_constants_0_13_3.json"),
    (V0_13_4, "../resources/blockifier_versioned_constants_0_13_4.json"),
    (V0_13_5, "../resources/blockifier_versioned_constants_0_13_5.json"),
    (V0_13_6, "../resources/blockifier_versioned_constants_0_13_6.json"),
    (V0_14_0, "../resources/blockifier_versioned_constants_0_14_0.json"),
    (V0_14_1, "../resources/blockifier_versioned_constants_0_14_1.json"),
    (V0_14_2, "../resources/blockifier_versioned_constants_0_14_2.json"),
    (V0_14_3, "../resources/blockifier_versioned_constants_0_14_3.json"),
    (V0_14_4, "../resources/blockifier_versioned_constants_0_14_4.json"),
);
```
