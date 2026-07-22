### Title
`starknet_estimateFee` / `starknet_simulateTransactions` omit `l2_gas_consumed` from `FeeEstimation`, returning an authoritative-looking wrong fee breakdown for V3 transactions — (File: `crates/apollo_rpc_execution/src/objects.rs`)

---

### Summary

The `FeeEstimation` struct returned by `starknet_estimateFee` and `starknet_simulateTransactions` is missing the `l2_gas_consumed` field. For V3 transactions that consume L2 gas, `overall_fee` is taken from `receipt.fee` (which correctly includes L2 gas costs), but the breakdown fields `gas_consumed` and `data_gas_consumed` only reflect L1 gas and L1 data gas respectively. The documented formula `overall_fee = gas_consumed * gas_price + data_gas_consumed * data_gas_price` is therefore wrong for any V3 transaction, and callers have no way to derive the L2 gas consumed from the response.

---

### Finding Description

In `tx_execution_output_to_fee_estimation` the struct is built as:

```rust
Ok(FeeEstimation {
    gas_consumed:      gas_vector.l1_gas.0.into(),      // L1 gas only
    l1_gas_price,
    data_gas_consumed: gas_vector.l1_data_gas.0.into(), // L1 data gas only
    l1_data_gas_price,
    l2_gas_price,                                        // price present …
    overall_fee: tx_execution_output.execution_info.receipt.fee, // includes L2 gas cost
    unit: tx_execution_output.price_unit,
})
```

`gas_vector.l2_gas` is never exposed. The struct definition carries an explicit acknowledgement of the gap:

```rust
// TODO(Tzahi): Add l2_gas_consumed. Verify overall_fee estimation of l1_gas_price only is
// close enough (as there are roundings) to the fee of both l1_gas_price and l2_gas_price.
```

`receipt.fee` is computed by `get_fee_by_gas_vector`, which calls `gas_vector.cost(gas_price_vector, tip)` — a sum over all three gas dimensions including `l2_gas * l2_gas_price`. So `overall_fee` is the true total, but the breakdown fields are incomplete.

The OpenRPC schema reinforces the wrong formula:

```json
"overall_fee": {
    "description": "The estimated fee … equals to gas_consumed*gas_price + data_gas_consumed*data_gas_price"
}
```

This description omits the L2 gas term entirely.

---

### Impact Explanation

**Impact: High — RPC fee estimation returns an authoritative-looking wrong value.**

For any V3 transaction (`AllResourceBounds`) that consumes L2 gas:

1. A caller computing `gas_consumed * l1_gas_price + data_gas_consumed * l1_data_gas_price` obtains a value **lower** than `overall_fee` by exactly `l2_gas_consumed * l2_gas_price`. This is the direct analog of the external bug: the estimate is lower than the actual fee because a variable is missing from the formula.

2. A caller that needs to set the `l2_gas` resource bound for a follow-up V3 transaction has no way to read `l2_gas_consumed` from the response. They must either guess or over-provision, and an under-provisioned bound causes the transaction to revert with `MaxGasAmountExceeded`.

3. The `l2_gas_price` field is present in the response, making the omission of `l2_gas_consumed` look like an oversight rather than an intentional design, so callers reasonably trust the formula in the spec.

---

### Likelihood Explanation

Every V3 transaction (the current standard for Starknet) that executes Cairo code consumes L2 gas. The issue is therefore triggered by the normal use of `starknet_estimateFee` or `starknet_simulateTransactions` for any modern transaction type.

---

### Recommendation

Add `l2_gas_consumed` to `FeeEstimation` and populate it in `tx_execution_output_to_fee_estimation`:

```rust
pub struct FeeEstimation {
    pub gas_consumed: Felt,
    pub l1_gas_price: GasPrice,
    pub data_gas_consumed: Felt,
    pub l1_data_gas_price: GasPrice,
    pub l2_gas_consumed: Felt,   // add this
    pub l2_gas_price: GasPrice,
    pub overall_fee: Fee,
    pub unit: PriceUnit,
}

// in tx_execution_output_to_fee_estimation:
Ok(FeeEstimation {
    gas_consumed:      gas_vector.l1_gas.0.into(),
    l1_gas_price,
    data_gas_consumed: gas_vector.l1_data_gas.0.into(),
    l1_data_gas_price,
    l2_gas_consumed:   gas_vector.l2_gas.0.into(),   // add this
    l2_gas_price,
    overall_fee: tx_execution_output.execution_info.receipt.fee,
    unit: tx_execution_output.price_unit,
})
```

Update the OpenRPC schema description of `overall_fee` to include the L2 gas term.

---

### Proof of Concept

1. Submit a V3 `INVOKE` transaction to `starknet_estimateFee` on a node running Starknet ≥ 0.13.2 (L2 gas active).
2. Receive a `FeeEstimation` response. Observe `l2_gas_price` is non-zero and `overall_fee` is non-zero, but `l2_gas_consumed` is absent.
3. Compute `reconstructed = gas_consumed * l1_gas_price + data_gas_consumed * l1_data_gas_price`.
4. Observe `reconstructed < overall_fee`. The gap equals `l2_gas_consumed * l2_gas_price`.
5. Attempt to submit the same transaction with `l2_gas.max_amount` set to `0` (the only value derivable from the response without guessing): the transaction reverts with `MaxGasAmountExceeded`.

---

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** crates/apollo_rpc_execution/src/objects.rs (L94-113)
```rust
#[derive(Debug, Serialize, Deserialize, PartialEq, Eq, Clone)]
pub struct FeeEstimation {
    /// Gas consumed by this transaction. This includes gas for DA in calldata mode.
    pub gas_consumed: Felt,
    /// The gas price for execution and calldata DA.
    pub l1_gas_price: GasPrice,
    /// Gas consumed by DA in blob mode.
    pub data_gas_consumed: Felt,
    /// The gas price for DA blob.
    pub l1_data_gas_price: GasPrice,
    // TODO(Tzahi): Add l2_gas_consumed. Verify overall_fee estimation of l1_gas_price only is
    // close enough (as there are roundings) to the fee of both l1_gas_price and l2_gas_price.
    /// The L2 gas price for execution.
    pub l2_gas_price: GasPrice,
    /// The total amount of fee. This is equal to:
    /// gas_consumed * gas_price + data_gas_consumed * data_gas_price.
    pub overall_fee: Fee,
    /// The unit in which the fee was paid (Wei/Fri).
    pub unit: PriceUnit,
}
```

**File:** crates/apollo_rpc_execution/src/objects.rs (L161-183)
```rust
pub(crate) fn tx_execution_output_to_fee_estimation(
    tx_execution_output: &TransactionExecutionOutput,
    block_context: &BlockContext,
) -> ExecutionResult<FeeEstimation> {
    let gas_prices = &block_context.block_info().gas_prices;
    let (l1_gas_price, l1_data_gas_price, l2_gas_price) = (
        gas_prices.l1_gas_price(&tx_execution_output.price_unit.into()).get(),
        gas_prices.l1_data_gas_price(&tx_execution_output.price_unit.into()).get(),
        gas_prices.l2_gas_price(&tx_execution_output.price_unit.into()).get(),
    );

    let gas_vector = tx_execution_output.execution_info.receipt.gas;

    Ok(FeeEstimation {
        gas_consumed: gas_vector.l1_gas.0.into(),
        l1_gas_price,
        data_gas_consumed: gas_vector.l1_data_gas.0.into(),
        l1_data_gas_price,
        l2_gas_price,
        overall_fee: tx_execution_output.execution_info.receipt.fee,
        unit: tx_execution_output.price_unit,
    })
}
```

**File:** crates/apollo_rpc/resources/V0_8/starknet_api_openrpc.json (L3648-3666)
```json
                    "overall_fee": {
                        "title": "Overall fee",
                        "description": "The estimated fee for the transaction (in wei or fri, depending on the tx version), equals to gas_consumed*gas_price + data_gas_consumed*data_gas_price",
                        "$ref": "#/components/schemas/FELT"
                    },
                    "unit": {
                        "title": "Fee unit",
                        "description": "units in which the fee is given",
                        "$ref": "#/components/schemas/PRICE_UNIT"
                    }
                },
                "required": [
                    "gas_consumed",
                    "l1_gas_price",
                    "data_gas_consumed",
                    "l1_data_gas_price",
                    "overall_fee",
                    "unit"
                ]
```
