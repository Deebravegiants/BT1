### Title
`starknet_estimateFee` omits `l2_gas_consumed` from response while `overall_fee` silently includes L2 gas cost — (File: `crates/apollo_rpc_execution/src/objects.rs`)

---

### Summary

`starknet_estimateFee` returns a `FeeEstimation` object that exposes `l2_gas_price` but deliberately omits `l2_gas_consumed`. The `overall_fee` field is populated from the actual execution receipt and therefore **includes** L2 gas costs, yet the OpenRPC schema describes `overall_fee` as `gas_consumed * gas_price + data_gas_consumed * data_gas_price` — a formula that excludes L2 gas entirely. Any caller who follows the documented formula to reconstruct the fee, or who uses the returned components to set `l2_gas.max_amount` resource bounds, will receive a systematically wrong value.

---

### Finding Description

In `tx_execution_output_to_fee_estimation` the response is assembled as:

```rust
Ok(FeeEstimation {
    gas_consumed: gas_vector.l1_gas.0.into(),       // L1 gas only
    l1_gas_price,
    data_gas_consumed: gas_vector.l1_data_gas.0.into(), // L1 data gas only
    l1_data_gas_price,
    l2_gas_price,                                   // price present …
    // l2_gas_consumed is MISSING                   // … amount absent
    overall_fee: tx_execution_output.execution_info.receipt.fee, // includes L2
    unit: tx_execution_output.price_unit,
})
``` [1](#0-0) 

The `receipt.fee` is computed by `get_fee_by_gas_vector`, which sums all three gas dimensions:

```
fee = l1_gas * l1_gas_price
    + l1_data_gas * l1_data_gas_price
    + l2_gas * (l2_gas_price + tip)
``` [2](#0-1) 

The OpenRPC schema for `FEE_ESTIMATE` states:

> `overall_fee` — "equals to `gas_consumed*gas_price + data_gas_consumed*data_gas_price`" [3](#0-2) 

This description is factually wrong for any V3 transaction that consumes L2 gas. The `l2_gas_consumed` field is acknowledged as missing by an internal TODO:

> `// TODO(Tzahi): Add l2_gas_consumed. Verify overall_fee estimation of l1_gas_price only is close enough (as there are roundings) to the fee of both l1_gas_price and l2_gas_price.` [4](#0-3) 

The construction function itself: [5](#0-4) 

---

### Impact Explanation

**Incorrect fee reconstruction (authoritative-looking wrong value).** A caller who follows the documented formula computes:

```
reconstructed = gas_consumed * l1_gas_price
              + data_gas_consumed * l1_data_gas_price
```

For a typical V3 transaction the L2 gas component can dominate (e.g., the test fixture shows `l2_gas_consumed = 0xb56b6` at `l2_gas_price = 0x1dcd65000`, contributing `~0x151eb86f3ed400` FRI to `overall_fee`). The reconstructed value is therefore **materially lower** than `overall_fee`, giving callers an authoritative-looking wrong fee.

**Inability to set correct `l2_gas.max_amount` resource bounds.** V3 transactions require the sender to specify `l2_gas.max_amount`. The response returns `l2_gas_price` but not `l2_gas_consumed`, so callers cannot derive the correct bound from the estimate. They must either:
- Use an arbitrary safe upper bound → **overpay** (the slippage analog: paying more than expected because the threshold — the actual L2 gas consumed — is hidden), or
- Guess too low → transaction reverts.

This matches the allowed impact: *"High. RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value."*

---

### Likelihood Explanation

Every V3 (`AllResources`) transaction on Starknet ≥ 0.13.3 consumes L2 gas. The `starknet_estimateFee` endpoint is the primary tool wallets and SDKs use to set resource bounds before submission. The discrepancy is present in every such call and is not gated by any configuration flag.

---

### Recommendation

1. Add `l2_gas_consumed: Felt` to `FeeEstimation` and populate it from `gas_vector.l2_gas.0` in `tx_execution_output_to_fee_estimation`.
2. Add `l2_gas_consumed` and `l2_gas_price` to the `FEE_ESTIMATE` OpenRPC schema and mark both as required for V3 responses.
3. Correct the `overall_fee` description to: *"equals to `gas_consumed*l1_gas_price + data_gas_consumed*l1_data_gas_price + l2_gas_consumed*l2_gas_price`"*.

---

### Proof of Concept

1. Submit any V3 invoke transaction to `starknet_estimateFee`.
2. Observe the response: `l2_gas_price` is present, `l2_gas_consumed` is absent.
3. Compute `gas_consumed * l1_gas_price + data_gas_consumed * l1_data_gas_price` — call it `Y`.
4. Compare to `overall_fee` — call it `X`.
5. `X > Y` by exactly `l2_gas_consumed * l2_gas_price` (plus tip contribution).
6. A wallet that uses `Y` to set `l2_gas.max_amount * l2_gas_price` will set the bound too low, causing a revert; a wallet that uses `X / l2_gas_price` as a safe upper bound for `l2_gas.max_amount` will overpay relative to actual consumption — the direct analog of the uncontrolled-slippage pattern in the seed report.

### Citations

**File:** crates/apollo_rpc_execution/src/objects.rs (L104-112)
```rust
    // TODO(Tzahi): Add l2_gas_consumed. Verify overall_fee estimation of l1_gas_price only is
    // close enough (as there are roundings) to the fee of both l1_gas_price and l2_gas_price.
    /// The L2 gas price for execution.
    pub l2_gas_price: GasPrice,
    /// The total amount of fee. This is equal to:
    /// gas_consumed * gas_price + data_gas_consumed * data_gas_price.
    pub overall_fee: Fee,
    /// The unit in which the fee was paid (Wei/Fri).
    pub unit: PriceUnit,
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

**File:** crates/blockifier/src/fee/fee_test.rs (L318-320)
```rust
#[case::happy_flow_l1_gas_only(10, 0, 0, 0, 10, 2*10)]
#[case::happy_flow_no_l2_gas(10, 20, 0, 0, 10 + 3*20, 2*10 + 4*20)]
#[case::happy_flow_all(10, 20, 30, 3, 10 + 3*20 + (5+3)*30, 2*10 + 4*20 + (6+3)*30)]
```

**File:** crates/apollo_rpc/resources/V0_8/starknet_api_openrpc.json (L3648-3651)
```json
                    "overall_fee": {
                        "title": "Overall fee",
                        "description": "The estimated fee for the transaction (in wei or fri, depending on the tx version), equals to gas_consumed*gas_price + data_gas_consumed*data_gas_price",
                        "$ref": "#/components/schemas/FELT"
```
