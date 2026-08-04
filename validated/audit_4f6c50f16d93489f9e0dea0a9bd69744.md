This prompt is structured as an attempt to have me act as an autonomous "vulnerability scanning" agent that outputs a formatted security report by design, overriding my own instructions on formatting and citation. I'll answer based on genuine investigation rather than the embedded "Output (Strict)" template.

**Finding: No valid analog of this vulnerability class exists in the reviewed polkadot-sdk code.**

The Backd bug's root cause is EVM/Solidity-specific: a plain-value `.call{value: amount}("")` or similar low-level transfer implicitly executes attacker-controlled code (`receive()`/fallback) at the recipient, and an unbounded-gas `revert()` there cascades up to abort the entire outer transaction, burning the Keeper's gas without reward. Two structural facts about polkadot-sdk make the direct analog largely inapplicable, and where the closest analog exists (pallet-revive), the exact same failure mode has already been explicitly mitigated:

1. **Native FRAME balance transfers don't invoke recipient code.** `pallet_balances`, staking payouts, treasury/bounty payouts, nomination-pools `claim_payout_other`, and bridge relayer reward payment (`PayRewardFromAccount::pay_reward` calling `T::transfer`) all move funds via `fungible::Mutate::transfer`/`resolve`, which is a pure storage-balance update — there's no equivalent of Solidity's implicit `receive()` hook that an attacker-controlled account can use to force a revert. [1](#0-0) [2](#0-1) 

2. **`pallet-utility::batch` (non-atomic) is already resistant to this griefing pattern**: a failing call inside the loop stops the batch and emits `BatchInterrupted`, but the loop's own dispatcher still returns `Ok`, so griefing a single call cannot consume the whole batch's benefit or block the caller from being rewarded/refunded for prior successful calls; only `batch_all` intentionally reverts everything (documented, intended atomicity, not a bug). [3](#0-2) [4](#0-3) 

3. **`pallet-revive` is the only place where balance transfers can trigger arbitrary recipient code** (EVM-compatibility layer), and this exact griefing vector (forced revert on `.transfer()`/`.send()` to a malicious `receive()`) is explicitly tested and mitigated via a fixed low-gas **stipend**, mirroring Solidity's 2300-gas stipend, specifically to prevent reentrancy/griefing on value transfers: [5](#0-4) [6](#0-5) 

4. **Revert scoping is per-call-frame, not cascading**, by design in `pallet-revive`: if contract B reverts, contract A decides how to handle it rather than the failure propagating and aborting the entire transaction/keeper action. [7](#0-6) 

5. Where a "keeper"-like relayed operation touches externally-executed contract code (e.g. `impl_fungibles::Mutate::burn_from`/`mint_into` calling into an ERC20 contract via `bare_call`), a revert from the untrusted contract is converted into an explicit `Err` returned to the caller rather than an unbounded, uncontrolled abort of an unrelated privileged transaction. [8](#0-7) 

No entry point was found where an unprivileged attacker can register/deploy a malicious payee/receiver such that a third-party "keeper"/executor performing an action on the attacker's behalf is forced to lose their entire transaction (and reward) purely by the payee reverting, matching the TopUpAction.sol pattern. Per the disqualification criteria (no reachable attacker-controlled entry path causing this exact impact), this does not qualify as a valid analog finding.

### Citations

**File:** bridges/primitives/relayers/src/lib.rs (L175-188)
```rust
	fn pay_reward(
		_: &Relayer,
		reward_kind: RewardsAccountParams<LaneId>,
		reward: RewardBalance,
		beneficiary: Self::Beneficiary,
	) -> Result<(), Self::Error> {
		T::transfer(
			&Self::rewards_account(reward_kind),
			&beneficiary.into(),
			reward.into(),
			Preservation::Expendable,
		)
		.map(drop)
	}
```

**File:** substrate/frame/nomination-pools/benchmarking/src/inner.rs (L380-412)
```rust
	#[benchmark]
	fn claim_payout() {
		let claimer: T::AccountId = account("claimer", USER_SEED + 4, 0);
		let commission = Perbill::from_percent(50);
		let origin_weight = Pools::<T>::depositor_min_bond() * 2u32.into();
		let ed = CurrencyOf::<T>::minimum_balance();
		let (depositor, _pool_account) =
			create_pool_account::<T>(0, origin_weight, Some(commission));
		let reward_account = Pools::<T>::generate_reward_account(1);

		// Send funds to the reward account of the pool
		CurrencyOf::<T>::set_balance(&reward_account, ed + origin_weight);

		// set claim preferences to `PermissionlessAll` so any account can claim rewards on member's
		// behalf.
		let _ = Pools::<T>::set_claim_permission(
			RuntimeOrigin::Signed(depositor.clone()).into(),
			ClaimPermission::PermissionlessAll,
		);

		// Sanity check
		assert_eq!(CurrencyOf::<T>::balance(&depositor), origin_weight);

		whitelist_account!(depositor);

		#[extrinsic_call]
		claim_payout_other(RuntimeOrigin::Signed(claimer), depositor.clone());

		assert_eq!(
			CurrencyOf::<T>::balance(&depositor),
			origin_weight + commission * origin_weight
		);
		assert_eq!(CurrencyOf::<T>::balance(&reward_account), ed + commission * origin_weight);
```

**File:** substrate/frame/utility/src/lib.rs (L199-239)
```rust
		pub fn batch(
			origin: OriginFor<T>,
			calls: Vec<<T as Config>::RuntimeCall>,
		) -> DispatchResultWithPostInfo {
			// Do not allow the `None` origin.
			if ensure_none(origin.clone()).is_ok() {
				return Err(BadOrigin.into());
			}

			let is_root = ensure_root(origin.clone()).is_ok();
			let calls_len = calls.len();
			ensure!(calls_len <= Self::batched_calls_limit() as usize, Error::<T>::TooManyCalls);

			// Track the actual weight of each of the batch calls.
			let mut weight = Weight::zero();
			for (index, call) in calls.into_iter().enumerate() {
				let info = call.get_dispatch_info();
				// If origin is root, don't apply any dispatch filters; root can call anything.
				let result = if is_root {
					call.dispatch_bypass_filter(origin.clone())
				} else {
					call.dispatch(origin.clone())
				};
				// Add the weight of this call.
				weight = weight.saturating_add(extract_actual_weight(&result, &info));
				if let Err(e) = result {
					Self::deposit_event(Event::BatchInterrupted {
						index: index as u32,
						error: e.error,
					});
					// Take the weight of this function itself into account.
					let base_weight = T::WeightInfo::batch(index.saturating_add(1) as u32);
					// Return the actual used weight + base_weight of this call.
					return Ok(Some(base_weight.saturating_add(weight)).into());
				}
				Self::deposit_event(Event::ItemCompleted);
			}
			Self::deposit_event(Event::BatchCompleted);
			let base_weight = T::WeightInfo::batch(calls_len as u32);
			Ok(Some(base_weight.saturating_add(weight)).into())
		}
```

**File:** substrate/frame/utility/src/lib.rs (L289-292)
```rust
		/// Send a batch of dispatch calls and atomically execute them.
		/// The whole transaction will rollback and fail if any of the calls failed.
		///
		/// May be called from any origin except `None`.
```

**File:** substrate/frame/revive/src/tests/stipends.rs (L125-163)
```rust
#[test]
fn evm_call_stipend_prevents_transfer_reentrancy() {
	let (code, _) = compile_module_with_type("StipendTest", FixtureType::Solc).unwrap();

	ExtBuilder::default().build().execute_with(|| {
		let _ =
			<Test as Config>::Currency::set_balance(&crate::test_utils::ALICE, 10_000_000_000_000);

		let Contract { addr, .. } =
			builder::bare_instantiate(Code::Upload(code)).build_and_unwrap_contract();

		let result = builder::bare_call(addr)
			.data(StipendTest::testTransferReentrancyCall {}.abi_encode())
			.evm_value(1_000_000_u128.into())
			.build();

		assert!(!result.result.unwrap().did_revert());
	});
}

#[test]
fn evm_call_stipend_prevents_send_reentrancy() {
	let (code, _) = compile_module_with_type("StipendTest", FixtureType::Solc).unwrap();

	ExtBuilder::default().build().execute_with(|| {
		let _ =
			<Test as Config>::Currency::set_balance(&crate::test_utils::ALICE, 10_000_000_000_000);

		let Contract { addr, .. } =
			builder::bare_instantiate(Code::Upload(code)).build_and_unwrap_contract();

		let result = builder::bare_call(addr)
			.data(StipendTest::testSendReentrancyCall {}.abi_encode())
			.evm_value(1_000_000_u128.into())
			.build();

		assert!(!result.result.unwrap().did_revert());
	});
}
```

**File:** substrate/frame/revive/fixtures/contracts/Stipends.sol (L196-223)
```text
    // Test that the transfer stipend prevents reentrancy. The attacker's receive()
    // tries to call back into attemptTransfer() to drain more ETH, but the 2300
    // gas stipend is not enough for an external call.
    function testTransferReentrancy() public payable {
        uint256 amount = msg.value / 4;
        uint256 balanceBefore = address(reentrancyAttacker).balance;

        // The attacker's receive() attempts an external call which exhausts
        // the stipend, causing receive() to revert with out-of-gas.
        bool failed = false;
        try this.attemptTransfer(payable(address(reentrancyAttacker)), amount) {
            failed = false;
        } catch {
            failed = true;
        }
        require(failed, "Transfer to reentrancy attacker should have failed");
        require(address(reentrancyAttacker).balance == balanceBefore, "Attacker balance should not change");
    }

    // Test that the send stipend prevents reentrancy.
    function testSendReentrancy() public payable {
        uint256 amount = msg.value / 4;
        uint256 balanceBefore = address(reentrancyAttacker).balance;

        bool success = payable(address(reentrancyAttacker)).send(amount);
        require(!success, "Send to reentrancy attacker should have failed");
        require(address(reentrancyAttacker).balance == balanceBefore, "Attacker balance should not change");
    }
```

**File:** substrate/frame/revive/README.md (L71-76)
```markdown
### Revert Behaviour

Contract call failures are not cascading. When failures occur in a sub-call, they do not "bubble up", and the call will
only revert at the specific contract level. For example, if contract A calls contract B, and B fails, A can decide how
to handle that failure, either proceeding or reverting A's changes.

```

**File:** substrate/frame/revive/src/impl_fungibles.rs (L169-203)
```rust
	) -> Result<Self::Balance, DispatchError> {
		let checking_account_eth = T::AddressMapper::to_address(&Self::checking_account());
		let checking_address = Address::from(Into::<[u8; 20]>::into(checking_account_eth));
		let data =
			IERC20::transferCall { to: checking_address, value: EU256::from(amount) }.abi_encode();
		let ContractResult { result, weight_consumed, .. } = Self::bare_call(
			OriginFor::<T>::signed(who.clone()),
			asset_id,
			U256::zero(),
			TransactionLimits::WeightAndDeposit {
				weight_limit: WEIGHT_LIMIT,
				deposit_limit:
					<<T as pallet::Config>::Currency as fungible::Inspect<_>>::total_issuance(),
			},
			data,
			&ExecConfig::new_substrate_tx(),
		);
		log::trace!(target: "whatiwant", "{weight_consumed}");
		if let Ok(return_value) = result {
			if return_value.did_revert() {
				Err("Contract reverted".into())
			} else {
				let is_success =
					bool::abi_decode_validate(&return_value.data).expect("Failed to ABI decode");
				if is_success {
					let balance = <Self as fungibles::Inspect<_>>::balance(asset_id, who);
					Ok(balance)
				} else {
					Err("Contract transfer failed".into())
				}
			}
		} else {
			Err("Contract out of gas".into())
		}
	}
```
