### Title
Relayer fee withdrawal dispatches a zero-fee ISMP message with no incentive to relay, permanently losing the already-zeroed balance - ([File: modules/pallets/relayer/src/withdrawal.rs])

### Summary
`Pallet::withdraw` lets any relayer burn their own signed withdrawal request into a cross-chain settlement message, but dispatches it with `fee: Default::default()` (zero) and `payer: [0u8; 32]`. Because no relayer has an economic reason to deliver a zero-fee message, the settlement may never land on the destination chain, while the pallet has already unconditionally zeroed the relayer's `Fees` balance before delivery is confirmed. This mirrors the external report's bug class: an unprivileged, reachable action is allowed to set the fee that gates a required follow-up action to zero, and the party relying on that follow-up (here, the relayer waiting to be paid) loses the value with no compensating mechanism.

### Finding Description
`withdraw()` in [1](#0-0)  is invoked by a relayer submitting a signed `(nonce, dest_chain, beneficiary?)` payload. After verifying the signature and checking `available_amount >= min_withdrawal_amount`, it:

1. Builds a `WithdrawalParams`/`WithdrawalRequest` body instructing the destination chain's host manager to disburse `available_amount` to the beneficiary.
2. Dispatches it via `dispatcher.dispatch_request(DispatchRequest::Post(post), FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() })` — i.e. **zero relayer fee, null payer** [2](#0-1) .
3. Immediately zeroes the local `Fees` entry: `Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());` [3](#0-2) .

The zero-fee dispatch goes through the standard `IsmpDispatcher::dispatch_request` path, which only escrows/pays a fee `if fee.fee != Zero::zero()` [4](#0-3) . With `fee == 0`, no funds are escrowed for a relayer, and delivering this particular request earns nothing. This is exactly the pattern independently documented by the maintainers as an unresolved gap:

> "hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, **the relayer pallet's withdrawal request**. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` ... Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism." [5](#0-4) 

Unlike EVM-side dispatches, where a stuck zero/low-fee request can be topped up later via `EvmHost.fundRequest` [6](#0-5) , this substrate-originated withdrawal dispatch has no equivalent "increase fee" recovery path exposed to the relayer or anyone else in `withdrawal.rs`. Once `Fees` is zeroed, the only record of the owed amount is the (unincentivized, possibly never-delivered) in-flight ISMP message.

### Impact Explanation
- The relayer's accumulated fee balance (`Fees::<T>`) is debited to zero unconditionally and before the destination chain confirms receipt/execution of the withdrawal message.
- Because the dispatch carries `fee: 0`, no relayer in the network has an economic incentive to pick up and deliver this particular request; the maintainers' own documentation confirms this delivery today depends purely on altruism, with no fallback.
- If the message is never relayed (a very plausible steady state once the "helpful/altruistic" traffic disappears, or if all willing relayers are busy/absent for that route), the relayer's funds are effectively lost: debited on the source pallet, never credited on the destination chain, and unrecoverable through the pallet (no re-dispatch/re-fund entry point observed in `withdrawal.rs`).
- This is a genuine "permanent freezing/loss of funds" outcome reachable purely through submitting a normal signed withdrawal extrinsic — squarely inside the reachable "relayer fee and reward accounting" category.

### Likelihood Explanation
Likelihood is Medium-to-High: this isn't a contrived edge case — it is the *only* code path for relayers to withdraw their earned fees to another chain, and it is triggered by every legitimate relayer withdrawal. The zero-fee, zero-payer dispatch is unconditional (not a fallback for some rare configuration), and the maintainers themselves flag it as a systemic issue affecting multiple pallets, indicating the delivery-incentive gap is real and currently unaddressed in production code, not merely theoretical.

### Recommendation
- Do not zero `Fees::<T>` until delivery of the withdrawal message is confirmed (e.g., track it as "pending" and only finalize/zero on a delivery acknowledgment), or
- Attach a real, non-zero relayer fee to the withdrawal dispatch (funded from the withdrawn amount itself or a protocol treasury) so a relayer has an economic incentive to deliver it, consistent with the fix direction already proposed in `docs/outbound-request-incentivization.md` (per-module `OutboundRequestDeliveryReward` claimed against a destination state proof), and
- Provide a permissionless "top-up fee" / re-dispatch mechanism analogous to `EvmHost.fundRequest` so a stuck zero-fee withdrawal can be rescued by the relayer or a third party before funds are considered permanently lost.

### Proof of Concept
1. Relayer accumulates fees on Hyperbridge for `dest_chain = Evm(X)` via normal `accumulate_fees` flow, exceeding `MinWithdrawal`.
2. Relayer calls `Pallet::withdraw` with a valid signature for `(nonce, dest_chain, beneficiary)`.
3. `withdraw()` dispatches the ISMP POST with `FeeMetadata { payer: [0u8;32], fee: 0 }` [2](#0-1)  and immediately zeroes `Fees::<T>::get(dest_chain, address)` [3](#0-2) .
4. Because `fee == 0`, `IsmpDispatcher::dispatch_request` escrows nothing for a relayer [4](#0-3) , so no relayer has economic reason to deliver the message to `EvmHost` on the destination chain.
5. If the message is never delivered (plausible per the maintainers' own acknowledgment that these system dispatches "flow" only via altruism), the relayer's withdrawn balance is never credited on the destination chain and cannot be recovered — the funds are permanently lost from the relayer's perspective, with no `fundRequest`-equivalent rescue path in this pallet.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-187)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}

		let dispatcher = <T as Config>::IsmpHost::default();

		Nonce::<T>::try_mutate(address.clone(), withdrawal_data.dest_chain, |value| {
			*value += 1;
			Ok::<(), ()>(())
		})
		.map_err(|_| Error::<T>::ErrorCompletingCall)?;

		let beneficiary_address = withdrawal_data.beneficiary.clone().unwrap_or(address.clone());
		let (to, body) = match withdrawal_data.dest_chain {
			s if s.is_substrate() => (
				HYPERBRIDGE_MODULE_ID.to_vec(),
				Message::WithdrawRelayerFees(WithdrawalRequest {
					amount: available_amount.low_u128(),
					account: AccountId32::try_from(&beneficiary_address[..])
						.map_err(|_| Error::<T>::InvalidPublicKey)?,
				})
				.encode(),
			),
			_ => {
				let HostParam::EvmHostParam(params) =
					HostParams::<T>::get(withdrawal_data.dest_chain)
						.ok_or_else(|| Error::<T>::MissingMangerAddress)?;

				let body = WithdrawalParams {
					beneficiary_address: beneficiary_address.clone(),
					amount: available_amount.into(),
					token: params.fee_token,
				}
				.abi_encode()
				.map_err(|_| Error::<T>::InvalidPublicKey)?;

				(params.host_manager.0.to_vec(), body)
			},
		};

		let post = DispatchPost {
			dest: withdrawal_data.dest_chain,
			from: MODULE_ID.to_vec(),
			to,
			body,
			timeout: 0,
		};

		// Account is not useful in this case
		dispatcher
			.dispatch_request(
				DispatchRequest::Post(post),
				FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() },
			)
			.map_err(|_| Error::<T>::DispatchFailed)?;

		Fees::<T>::insert(withdrawal_data.dest_chain, address.clone(), U256::zero());

		Self::deposit_event(Event::<T>::Withdraw {
			address: sp_runtime::BoundedVec::truncate_from(address.clone()),
			beneficiary_address: sp_runtime::BoundedVec::truncate_from(beneficiary_address),
			state_machine: withdrawal_data.dest_chain,
			amount: available_amount,
		});

		Ok(())
	}
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L96-106)
```rust
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}
```

**File:** docs/outbound-request-incentivization.md (L9-17)
```markdown
A regular cross-chain message that flows *through* hyperbridge has a fee attached at origin (the source chain transfers `fee.payer → RELAYER_FEE_ACCOUNT` and records `RequestPayments[commitment]` in pallet-hyperbridge's child trie). When a relayer delivers and the destination receipt lands back on hyperbridge, the existing `accumulate_fees` flow credits that fee to the relayer. That whole pipeline assumes a *user* paid at origin.

But hyperbridge itself originates requests too: host parameter propagation, host-executive updates, intents-coprocessor responses, token-governor messages, the relayer pallet's withdrawal request. Today these all dispatch with `FeeMetadata { payer: [0u8; 32].into(), fee: Default::default() }` (see `modules/pallets/host-executive/src/lib.rs:228`, `modules/pallets/intents-coprocessor/src/lib.rs:486`, `modules/pallets/relayer/src/lib.rs:638`, and `modules/pallets/token-governor/src/impls.rs`). Zero fee, zero payer. So relayers have no economic reason to pick them up, and the only thing that keeps them flowing today is altruism.

## The shape of the solution

The issue creator's preferred shape ([comment 4428807013](https://github.com/polytope-labs/hyperbridge/issues/532#issuecomment-4428807013)): use `pallet-relayer` to pay BRIDGE to whoever proves they delivered a hyperbridge-originated request. The messaging task in the tesseract relayer submits the claim.

Not every pallet on hyperbridge that dispatches a request is in scope. `pallet_ismp::child_trie::RequestCommitments` ends up holding commitments for every successful dispatch via `IsmpDispatcher`, which includes both the system messages we want to incentivize (host-executive, intents-coprocessor, token-governor, the relayer pallet's withdrawal path, future modules like bandwidth) and any other pallet that ends up dispatching from hyperbridge. The reward storage is therefore keyed by `source_module_id` and only modules with a non-zero reward are eligible. The `module_id` is the `from` field on the `PostRequest`, which each pallet sets to its unique module identifier. A module with zero reward is treated as not on the allowlist and rejected before any state proof verification runs.
```

**File:** evm/src/core/EvmHost.sol (L1031-1051)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
    }
```
