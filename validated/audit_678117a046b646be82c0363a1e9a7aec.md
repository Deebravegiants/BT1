### Title
Relayer profitability check trusts an unguarded single-block Uniswap V2 spot price as gas-cost oracle - (File: tesseract/messaging/evm/src/gas_oracle.rs)

### Summary
`get_price_from_uniswap_router` in the relayer's gas oracle prices the destination chain's native/fee token entirely from a single, unguarded, same-block `getAmountsIn` call to a configured Uniswap V2 router, with no TWAP, no minimum-liquidity check, and no deviation/staleness bound — the same bug class as the MorphoBlue exploit, where a single manipulable spot price fed a financial decision (there: LTV/borrow limit; here: the USD gas cost used to gate relayer delivery).

### Finding Description
`get_current_gas_cost_in_usd` computes the USD cost of relaying a message by combining the node's raw gas price with a USD/token conversion pulled from `get_price_from_uniswap_router`: [1](#0-0) 

This function reads `IUniswapV2Router.getAmountsIn` for a single trade path (`feeToken -> nativeToken`) at the **current block only** — there is no TWAP window, no sanity bound against a reference price, and no minimum-liquidity/staleness check: [2](#0-1) 

This is exactly the MorphoBlue bug class: a protocol-critical financial computation (there, LTV/borrow capacity; here, `gas_price_cost`, the USD-denominated execution cost) is derived from one spot AMM read that an attacker can move within the same transaction via a flash-loan-funded swap on the configured V2 pool, with no manipulation resistance.

`gas_price_cost` (via `est.execution_cost`) then directly gates the relayer's decision to deliver a message: `return_successful_queries` compares the on-chain-attached user fee (`fee_metadata`) against `fee_with_profit = total_gas_to_be_expended_in_usd + profit`, and skips delivery entirely if the fee doesn't cover it: [3](#0-2) 

### Impact Explanation
An attacker who can cheaply move the price on the configured `uniswapV2` router/pair (e.g. a low-liquidity fee-token/native pool, manipulated via flash loan in the same block the relayer queries it) can inflate the computed `gas_price_cost`. Since `return_successful_queries` treats an inflated cost as unprofitable and skips the message (`retriable_messages`), this lets an attacker selectively stall/park delivery of specific in-flight ISMP requests to a targeted destination chain — a denial-of-delivery on a route that otherwise has funded, legitimate messages waiting. Conversely, a deflated manipulated price could induce the relayer to submit at an actual loss. Both outcomes map to the report's "route unable to deliver messages" / relayer-fee-accounting-exploited categories.

### Likelihood Explanation
Every EVM destination chain not on Arbitrum/Optimism-stack special-casing (and even those, only for the L1 base-fee/L2 gas price legs, not this USD conversion) uses this single-spot-price path each time `get_current_gas_cost_in_usd` is invoked, i.e. on every profitability evaluation cycle. The manipulation only needs to move price for the duration of one RPC read that the relayer's async task performs, which is well within reach of a same-block flash-loan swap against whatever `uniswapV2` pool is configured as `hostParams.uniswapV2` for that chain — a config value governance sets, but the pool's live liquidity/manipulability is not controlled by governance and can be thin on smaller or newer deployments.

### Recommendation
Replace the single-block `getAmountsIn` read with a manipulation-resistant price source: a TWAP over a meaningful window (or Uniswap V3 `observe`), a Chainlink feed where available (mirroring the pattern already used correctly in `SimplexPaymaster._getOraclePrice`, which enforces staleness bounds), or at minimum a sanity/deviation bound against a governance-set reference price before the value is allowed to gate delivery decisions.

### Proof of Concept
Conceptual PoC (mirrors the MorphoBlue flash-loan pattern):
1. Attacker identifies the `uniswapV2` router/pair configured in `EvmHost.hostParams()` for a target destination chain, and observes it has thin liquidity for the `feeToken`/native pair.
2. Attacker submits a flash-loan-funded swap against that pair in the same block a relayer is expected to poll `get_price_from_uniswap_router`, moving `getAmountsIn(1 native, [feeToken, nativeToken])` far from the true market price.
3. The relayer's `get_current_gas_cost_in_usd` returns an inflated `gas_price_cost`; `return_successful_queries` computes `fee_with_profit` above the user-attached `fee_metadata` for a specific pending request targeting that chain, and marks it `retriable`/unprofitable rather than delivering it.
4. Attacker repeats each retry cycle to keep the targeted message perpetually parked, denying delivery on that route while the manipulation persists, or times it around known consensus-update triggers to block a specific message's window.

(Note: I could not fully trace every downstream caller of `get_current_gas_cost_in_usd`/`estimate_gas_batched` in this pass — confirming exactly how often/where each relayer implementation re-polls this price per retry cycle would need a closer read of `tesseract/messaging/evm/src/provider.rs` and `tx.rs`.)

### Citations

**File:** tesseract/messaging/evm/src/gas_oracle.rs (L183-223)
```rust
async fn get_price_from_uniswap_router(
	ismp_host: H160,
	client: Arc<AlloyProvider>,
) -> Result<U256, Error> {
	let host = EvmHostInstance::new(Address::from_slice(&ismp_host.0), client.clone());
	let params = host.hostParams().block(BlockId::latest()).call().await?;

	// There are no uniswap pool on testnet, return 1 usd as native token value
	if params.hyperbridge.0.starts_with(b"KUSAMA") {
		return Ok(U256::from(10).pow(U256::from(27)));
	}

	let uniswap_v2 = H160::from_slice(params.uniswapV2.as_slice());
	let fee_token = Address::from_slice(params.feeToken.as_slice());

	if uniswap_v2 == H160::zero() {
		return Err(anyhow!("Uniswap V2 Router not configured in Host Params"));
	}

	let router = IUniswapV2Router::IUniswapV2RouterInstance::new(params.uniswapV2, client.clone());
	let native_token = router.WETH().block(BlockId::latest()).call().await?;

	let fee_token_contract = IERC20::IERC20Instance::new(fee_token, client.clone());
	let fee_token_decimals = fee_token_contract.decimals().block(BlockId::latest()).call().await?;

	let native_token_contract = IERC20::IERC20Instance::new(native_token, client.clone());
	let native_decimals = native_token_contract.decimals().block(BlockId::latest()).call().await?;

	let path = vec![fee_token, native_token];
	let amount_out = primitive_to_alloy_u256(U256::from(10).pow(U256::from(native_decimals)));

	let amounts = router.getAmountsIn(amount_out, path).block(BlockId::latest()).call().await?;

	if amounts.is_empty() {
		return Err(anyhow!("Invalid amounts returned from Uniswap V2 Router"));
	}

	let amount_stable = alloy_u256_to_primitive(amounts[0]);

	let target_decimals = 27;
	Ok(amount_stable * U256::from(10).pow(U256::from(target_decimals - fee_token_decimals as u32)))
```

**File:** tesseract/messaging/messaging/src/events.rs (L500-539)
```rust
					let value = if coprocessor != sink.state_machine_id().state_id {
						let total_gas_to_be_expended_in_usd = est.execution_cost;
						// what kind of message is this?
						let Some(og_source)  = client_map.get(&query.source_chain) else {
							tracing::info!(target: crate::LOG_TARGET, "Skipping tx because fee metadata cannot be queried, client for {:?} was not provided", query.source_chain);
							return Ok((None, None))
						};

						let fee_metadata = match msg {
							// A GetResponse is gated on the fee attached to its origin GetRequest,
							// which the EVM host pays the relayer when it dispatches the response.
							// `query.commitment` is the request commitment for both message kinds.
							Message::Request(_) | Message::Response(_) =>
								og_source.query_request_fee_metadata(query.commitment).await?,
							_ => Err(anyhow!("Unexpected message: {msg:?}"))?
						};

						// normalize fee_metadata to 18 decimals since gas cost is calculated in 18 decimals
						let fee_token_decimal = og_source.fee_token_decimals().await?;
						let mut fee_metadata: Cost = (fee_metadata * U256::from(10u128.pow(18u32.saturating_sub(fee_token_decimal.into()) as u32))).into();

						let profit = (U256::from(minimum_profit_percentage) *
							total_gas_to_be_expended_in_usd.0) /
							U256::from(10000);
						// 0 profit percentage means we want to relay all requests for free
						let fee_with_profit: Cost = total_gas_to_be_expended_in_usd + profit;
						if minimum_profit_percentage == 0 {
							fee_metadata = U256::MAX.into()
						};

						if fee_metadata < fee_with_profit {
							tracing::info!(target: crate::LOG_TARGET, "Skipping unprofitable tx. Expected ${fee_with_profit}, user provided ${fee_metadata}");
							(None, Some(msg))
						} else {
							tracing::trace!(
								target: crate::LOG_TARGET, "Pushing tx to {:?} with cost ${fee_with_profit} and profit: ${}",
									sink.state_machine_id().state_id, Cost(profit)
							);
							(Some(query), None)
						}
```
