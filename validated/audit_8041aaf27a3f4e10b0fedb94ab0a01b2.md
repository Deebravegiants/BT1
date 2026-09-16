### Title
Relayer fee balances below the per-destination minimum withdrawal amount can become permanently frozen - (File: `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
`pallet-ismp-relayer`'s `withdraw` extrinsic enforces a per-`(relayer, destination-chain)` minimum balance before it will dispatch a payout, mirroring the `InstantManager` minimum-redemption bug: a balance that ever falls below the threshold — and has no further way to grow — is permanently unreachable by its owner.

### Finding Description
`Pallet::withdraw` rejects any withdrawal whose `available_amount` for the caller on a given destination chain is below `MinimumWithdrawalAmount` (governance-settable per chain, default `$10` via `MinWithdrawal`): [1](#0-0) 

Fees accrue into `Fees::<T>` keyed by `(dest_chain, address)` only through `accumulate_fees`, which credits a relayer for proofs of message deliveries to that specific destination: [2](#0-1) 

There is no path to withdraw a sub-threshold balance, no automatic sweep across chains, and no way to top up a specific `(address, dest_chain)` balance other than delivering more messages to that exact destination. A relayer that has already delivered its available messages to a low-traffic destination (or stops relaying to it) is left with a balance keyed to that chain that can never cross the threshold. Unlike a user's own deposit, this balance cannot be replenished at will — it depends on future message traffic actually routing through that relayer to that destination, something entirely outside the relayer's control.

This is the same root cause as the `InstantManager` minimum-redemption issue: a hard floor gates access to funds already earned/owned by the caller, with no escape hatch for amounts that fall (or start) below it.

### Impact Explanation
Relayer rewards are a form of funds owned by an unprivileged actor (the relayer) reachable through ordinary reward-accounting activity (delivering messages) — squarely within the allowed "relayer fee and reward accounting" surface. A sub-threshold, non-growing balance is functionally frozen: the relayer can never withdraw it through the on-chain path, and no user or governance action recovers it for them. This is an availability/loss-of-funds issue, not attacker-exploitable for profit, matching the disputed-but-valid-Medium disposition of the original finding.

### Likelihood Explanation
Any relayer relaying to a lower-volume destination chain, or one that winds down operations on a chain after accruing some but not $10-worth of fees, hits this deterministically — no adversarial conditions are required, only normal usage patterns across many `(relayer, destination)` pairs in the fee table.

### Recommendation
Allow a relayer to force-withdraw their full sub-threshold balance for a given destination (e.g. an explicit `withdraw_all`/override extrinsic bypassing `MinimumWithdrawalAmount`), or support aggregating/consolidating stranded per-chain balances so relayers are not required to generate further chain-specific traffic just to clear a floor.

### Proof of Concept
1. Relayer `R` delivers a handful of low-value messages to destination chain `D`, accumulating `Fees::<T>::get(D, R) = $6` via `accumulate_fees`.
2. `R` stops delivering to `D` (no more traffic routes through `R` to `D`).
3. `R` calls `withdraw_fees` targeting `D`; `available_amount ($6) < MinWithdrawal::get() ($10)` triggers `Error::<T>::NotEnoughBalance` at [3](#0-2) .
4. `R` has no mechanism to withdraw the $6 or to top it up except by relaying more traffic specifically to `D`, which it cannot control — the balance stays permanently locked.

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

**File:** modules/pallets/relayer/src/lib.rs (L350-358)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight({1_000_000})]
		pub fn accumulate_fees(
			origin: OriginFor<T>,
			withdrawal_proof: WithdrawalProof,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::accumulate(withdrawal_proof)
		}
```
