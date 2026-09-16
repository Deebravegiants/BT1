### Title
Hardcoded 18-decimal `MinWithdrawal` default freezes relayer fee withdrawals on non-18-decimal fee-token chains - ([File: modules/pallets/relayer/src/withdrawal.rs])

### Summary
`pallet-ismp-relayer`'s `withdraw()` gates a relayer's fee withdrawal against a minimum threshold that is compared directly to the raw `Fees` balance, but that balance is denominated in the destination chain's fee-token native units (whatever decimals that token uses), while the fallback minimum (`MinWithdrawal`) is hardcoded assuming an 18-decimal token. This is structurally the same bug class as TRST-M-1: a dollar-denominated minimum compared against a value expressed in different units/decimals, causing legitimate holders to be unable to withdraw funds they otherwise qualify for.

### Finding Description
`Pallet::withdraw` in `modules/pallets/relayer/src/withdrawal.rs` checks: [1](#0-0) 

against `MinimumWithdrawalAmount::<T>` for the destination `StateMachine`, falling back to `MinWithdrawal::get()`: [2](#0-1) 

`MinWithdrawal` is a hardcoded constant of `10 * 10^18` raw units — an assumption that the fee token uses 18 decimals ("$10"): [3](#0-2) 

However, the `Fees` balance being compared is accumulated in `accumulate.rs` directly from the raw, undecoded fee amount recorded on the source chain — an EVM `RequestMetadata.fee` (raw `U256`) or a substrate `RequestMetadata.fee.fee` (raw `u128`) — with **no decimal normalization** applied: [4](#0-3) 

The system explicitly tracks that fee tokens can have decimals other than 18 — `pallet-host-executive::FeeTokenDecimals` stores per-substrate-chain decimals, and the indexer's event handler even performs its own decimal-aware rescale (`rawAmount / 10n ** (18n - decimals)`) when reporting accumulated fees, confirming the raw on-chain `Fees`/event amount is not universally 18-decimal-normalized: [5](#0-4) [6](#0-5) 

Because `MinWithdrawal` is a single, decimals-agnostic constant baked into the pallet, any destination `StateMachine` whose fee token does not use 18 decimals (e.g. a 6-decimal stablecoin) and for which governance has not explicitly called `set_minimum_withdrawal` to override the default with the correct decimal scale, will have its minimum threshold silently mis-scaled by up to 10^12×. In the common case of a 6-decimal fee token this makes the effective minimum absurdly high (≈10^12 "dollars"), permanently blocking `withdraw()` for every relayer earning fees on that chain via `Error::<T>::NotEnoughBalance`, regardless of how large their legitimately accrued balance actually is.

### Impact Explanation
This is a protocol-level freezing-of-funds condition reachable by any relayer through the normal, unsigned `withdraw_fees` extrinsic — a single submitted transaction. Relayer fees, once accumulated via valid state proofs, become permanently unwithdrawable on any destination chain configured with a non-18-decimal fee token unless/until governance manually calls `set_minimum_withdrawal` for that exact `StateMachine`. This directly matches the "permanent freezing of funds" acceptance criterion, and affects a core, unprivileged economic actor (relayers) rather than an admin/governance path.

### Likelihood Explanation
Likelihood is medium-to-high in any deployment that onboards a destination chain whose fee token is not 18-decimal (a very common real-world scenario, e.g. USDC/USDT with 6 decimals) before governance remembers to explicitly configure `set_minimum_withdrawal` for that chain. The bug requires no attacker — it triggers automatically as an operational default, and the tesseract relayer's own auto-withdraw client-side logic (`tesseract/messaging/relayer/src/fees.rs`, `tesseract/messaging/messaging/src/fees.rs`) demonstrates that these clients already understand `fee_token_decimals` must be applied to compute a meaningful "$X" threshold — the on-chain pallet default does not do the equivalent scaling per-chain.

### Recommendation
Remove the fixed 18-decimal assumption from `MinWithdrawal`. Either (a) require `MinimumWithdrawalAmount` to be mandatorily set per `StateMachine` at chain-onboarding time (no silent fallback), or (b) scale the fallback default using the chain's known fee-token decimals (from `pallet-host-executive::FeeTokenDecimals` or the EVM host params) before comparing it to `available_amount`, so the minimum is expressed in the same unit basis as the accumulated `Fees` balance for that specific chain.

### Proof of Concept
1. Governance/onboarding registers a new destination `StateMachine` (e.g. EVM chain X) whose configured fee token uses 6 decimals, without calling `set_minimum_withdrawal(X, ...)`.
2. A relayer delivers messages on chain X and successfully accumulates a large, real balance of fees (e.g. equivalent of $50) via `accumulate_fees`, stored in `Fees::<T>` as raw 6-decimal units (≈50 * 10^6).
3. The relayer calls `withdraw_fees` for chain X. `Self::min_withdrawal_amount(X)` returns `None` (never set), so the check falls back to `MinWithdrawal::get() == 10 * 10^18`.
4. `available_amount (50 * 10^6) < MinWithdrawal (10 * 10^18)` is always true, so `withdraw()` reverts with `Error::<T>::NotEnoughBalance` no matter how much the relayer has earned — the relayer's fees on chain X are permanently unwithdrawable until governance manually intervenes.

*Note: I was unable to directly inspect the EVM-side `EvmHostParam`/fee-token decimal wiring or confirm whether any additional pallet migration enforces `set_minimum_withdrawal` at onboarding time for every EVM chain; this could partially mitigate the issue in practice if such a migration exists, but no such safeguard was found in the code reviewed.*

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-123)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}
```

**File:** modules/pallets/relayer/src/lib.rs (L137-150)
```rust
	/// Default minimum withdrawal is $10
	pub struct MinWithdrawal;

	impl Get<U256> for MinWithdrawal {
		fn get() -> U256 {
			U256::from(10u128 * 1_000_000_000_000_000_000)
		}
	}

	/// Minimum withdrawal amount
	#[pallet::storage]
	#[pallet::getter(fn min_withdrawal_amount)]
	pub type MinimumWithdrawalAmount<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachine, U256, OptionQuery>;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L260-297)
```rust
			let fee = match proof.source_proof.height.id.state_id {
				s if crate::is_pharos(&s) =>
					if encoded_metadata.len() == 32 {
						U256::from_big_endian(&encoded_metadata)
					} else {
						return Err(Error::<T>::ProofValidationError);
					},
				s if s.is_evm() => {
					use alloy_rlp::Decodable;
					let fee = alloy_primitives::U256::decode(&mut &*encoded_metadata)
						.map_err(|_| Error::<T>::ProofValidationError)?;
					U256::from_big_endian(&fee.to_be_bytes::<32>())
				},
				s if s.is_substrate() => {
					use codec::Decode;
					let fee: u128 = pallet_ismp::dispatcher::RequestMetadata::<T>::decode(
						&mut &*encoded_metadata,
					)
					.map_err(|_| Error::<T>::ProofValidationError)?
					.fee
					.fee
					.into();
					U256::from(fee)
				},
				// unsupported
				_ => Err(Error::<T>::MismatchedStateMachine)?,
			};
			let encoded_receipt = dest_result
				.get(&dest_key)
				.cloned()
				.flatten()
				.ok_or_else(|| Error::<T>::ProofValidationError)?;
			let address = Self::decode_receipt_relayer(
				proof.dest_proof.height.id.state_id,
				&encoded_receipt,
			)?;
			let entry = result.entry(address).or_insert(U256::zero());
			*entry += fee;
```

**File:** modules/pallets/host-executive/src/lib.rs (L85-89)
```rust
	/// Stores the fee token decimals for only substrate based chains
	#[pallet::storage]
	#[pallet::getter(fn fee_token_decimals)]
	pub type FeeTokenDecimals<T: Config> =
		StorageMap<_, Blake2_128Concat, StateMachine, u8, OptionQuery>;
```

**File:** sdk/packages/indexer/src/handlers/events/fees/accumulatedFees.event.handler.ts (L52-57)
```typescript
		const decimals = await DailyTreasuryRewardService.getFeeTokenDecimals(stateMachineId)
		logger.info(`accumulated fees event gotten for relayer ${relayerBytes}, with token fee decimals ${decimals}`)

		const normalizedAmount = rawAmount / 10n ** (18n - BigInt(decimals))

		record.lifetimeFees += normalizedAmount
```
