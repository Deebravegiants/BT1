# Analog Found: Cross-Domain Signature Replay Between Relayer Fee Accumulation and Withdrawal

Both `pallet-ismp-relayer` extrinsics that consume a relayer's per-chain signature — `accumulate_fees` (beneficiary redirect) and `withdraw_fees` — share the same `Nonce` storage map and, critically, produce **byte-for-byte identical signed message hashes** when their arguments coincide. This lack of domain separation lets a signature authorized for one action (a small beneficiary redirect during fee accumulation) be replayed by anyone as the other action (a full balance withdrawal), analogous to CVE-2017-0921's core flaw: an action-authorizing credential that isn't properly scoped/bound to the specific action it authorizes, enabling an unintended, unauthorized state change (there: password change; here: forced fee withdrawal).

### Title
Cross-domain signature replay lets attacker force early/unauthorized relayer fee withdrawals by replaying `accumulate_fees` beneficiary signatures into `withdraw_fees` (and vice versa) - (File: `modules/pallets/relayer/src/accumulate.rs`, `modules/pallets/relayer/src/withdrawal.rs`)

### Summary
The relayer fee module uses the same `Nonce` map and near-identical message-construction functions for two distinct signed operations:
- `beneficiary_message(nonce, state_machine, beneficiary: &[u8])` used in `accumulate()`'s optional beneficiary redirect [1](#0-0) 
- `message(nonce, dest_chain, beneficiary: Option<Vec<u8>>)` used in `withdraw()` [2](#0-1) 

When `beneficiary` is `Some(..)`, both functions SCALE-encode the identical tuple shape `(u64, StateMachine, Vec<u8>/&[u8])` and hash it with `keccak_256`, producing an identical pre-image and therefore an identical signature-verifiable digest whenever `nonce`, chain, and beneficiary bytes match.

### Finding Description
`accumulate()` verifies a relayer-supplied signature over `beneficiary_message(nonce, state_machine, beneficiary_address)` to redirect just the newly accumulated batch fee to a beneficiary, using the nonce fetched from `Nonce::<T>::get(&delivery_address, state_machine)` [3](#0-2) , then increments the same nonce [4](#0-3) .

`withdraw()` verifies a signature over `message(nonce, dest_chain, beneficiary)` using `Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain)` [5](#0-4) , and on success it **empties the relayer's entire accumulated fee balance** for that chain and dispatches a payout of the full `available_amount`: [6](#0-5) 

Because both extrinsics are unsigned (`ensure_none`) and dispatched via `validate_unsigned`/`ValidateUnsigned` for the pallet [7](#0-6) , anyone observing a relayer's in-flight `accumulate_fees` (with `beneficiary_details`) call in the transaction pool/gossip can lift that `(address, signature)` pair and resubmit it inside a `withdraw_fees` call before the original transaction lands. Since the `Nonce` value hasn't advanced yet, the signature check in `withdraw()` succeeds (`eth_address == address` recovered from the same signature), and the module immediately drains the relayer's **entire** currently accumulated `Fees[dest_chain][address]` to the beneficiary embedded in the original signed message, rather than the small newly-accumulating amount the relayer actually authorized. This also burns the nonce, causing the relayer's original, legitimately-intended transaction to subsequently fail signature verification (`Error::<T>::InvalidSignature`) once it lands, denying the intended operation.

### Impact Explanation
This breaks the intended invariant that a relayer explicitly, deliberately controls the timing and amount of "withdraw_fees" (which the docs describe as "withdraw their fees at any time" by signing with intent) [8](#0-7) . Any third party can force an involuntary, premature full withdrawal of a relayer's accrued balance and simultaneously DoS the relayer's legitimate transaction via nonce exhaustion — an unauthorized app action against relayer reward accounting reachable by any unprivileged network participant who observes gossiped extrinsics, with no signature or state-proof forgery required.

### Likelihood Explanation
High reachability: both calls are `ensure_none` (unsigned, permissionless) extrinsics validated purely by `validate_unsigned`, and anyone can submit `withdraw_fees` with data copied from a public, not-yet-included `accumulate_fees` transaction. No special privileges, consensus proof forgery, or state manipulation are required — only observing gossip/mempool traffic and re-encoding the intercepted `(address, signature, beneficiary)` triple into the `withdraw_fees` payload before the original lands.

### Recommendation
Add domain separation to the signed payloads so a signature for one action can never validate for the other — e.g., prefix each message with a distinct domain tag/discriminant (`b"ACCUMULATE_BENEFICIARY"` vs `b"WITHDRAW"`) before hashing in `beneficiary_message` and `message`, and/or use separate `Nonce` maps per action so intercepting one signature cannot advance or satisfy the other's replay-protection state.

### Proof of Concept
1. Relayer `R` has accrued `Fees[ChainX][R] = 1000` and `Nonce[R][ChainX] = N`.
2. `R` signs `beneficiary_message(N, ChainX, B)` and submits `accumulate_fees` with `beneficiary_details = Some((B, sig))`, intending only the newly proven batch's small fee to go to `B`.
3. Attacker observes `sig` in the mempool and immediately submits `withdraw_fees` with `WithdrawalInputData { signature: Evm{address: R, signature: sig}, dest_chain: ChainX, beneficiary: Some(B) }`.
4. `message(N, ChainX, B)` (withdrawal.rs) == `beneficiary_message(N, ChainX, B)` (accumulate.rs) byte-for-byte, so `withdraw()`'s signature check passes; `Nonce[R][ChainX]` becomes `N+1`, and the **entire** `Fees[ChainX][R] = 1000` is dispatched to `B` and zeroed [6](#0-5) .
5. When `R`'s original `accumulate_fees` transaction lands, `Nonce::<T>::get` now returns `N+1`, so the signature (over nonce `N`) fails verification and the transaction is rejected — `R`'s intended beneficiary redirect never executes, while an unauthorized, premature full withdrawal already occurred.

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L106-126)
```rust
		// Let's verify the beneficiary address
		let beneficiary_address = if let Some((beneficiary_address, signature)) =
			withdrawal_proof.beneficiary_details
		{
			let nonce = Nonce::<T>::get(&delivery_address, state_machine);
			let msg = beneficiary_message(nonce, state_machine, &beneficiary_address);
			match &signature {
				Signature::Evm { .. } => {
					let eth_address =
						signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
					if eth_address != delivery_address {
						Err(Error::<T>::InvalidPublicKey)?
					}
				},
				Signature::Sr25519 { .. } | Signature::Ed25519 { .. } => {
					// verify the signature with the delivery address from the state proof
					let _ = signature
						.verify(&msg, Some(delivery_address.clone()))
						.map_err(|_| Error::<T>::InvalidSignature)?;
				},
			}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L128-132)
```rust
			Nonce::<T>::try_mutate(&delivery_address, state_machine, |value| {
				*value += 1;
				Ok::<(), ()>(())
			})
			.map_err(|_: ()| Error::<T>::ErrorCompletingCall)?;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L309-315)
```rust
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L88-115)
```rust
		let nonce = Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain);
		let msg = message(nonce, withdrawal_data.dest_chain, withdrawal_data.beneficiary.clone());

		match &withdrawal_data.signature {
			Signature::Evm { address, .. } => {
				let eth_address = withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
				if &eth_address != address {
					Err(Error::<T>::InvalidPublicKey)?
				}
			},
			Signature::Sr25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
			Signature::Ed25519 { .. } => {
				// Verify signature with public key provided in signature enum
				withdrawal_data
					.signature
					.verify(&msg, None)
					.map_err(|_| Error::<T>::InvalidSignature)?;
			},
		};
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-184)
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
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L192-197)
```rust
pub fn message(nonce: u64, dest_chain: StateMachine, beneficiary: Option<Vec<u8>>) -> [u8; 32] {
	if let Some(beneficiary) = beneficiary {
		return sp_io::hashing::keccak_256(&(nonce, dest_chain, beneficiary).encode());
	}
	sp_io::hashing::keccak_256(&(nonce, dest_chain).encode())
}
```

**File:** modules/pallets/relayer/src/lib.rs (L453-502)
```rust
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T>
	where
		<T as frame_system::Config>::Hash: From<H256>,
		<T as frame_system::Config>::AccountId: From<[u8; 32]>,
		T::Balance: Into<u128>,
	{
		type Call = Call<T>;

		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let res = match call {
				Call::accumulate_fees { withdrawal_proof } =>
					Self::accumulate(withdrawal_proof.clone()),
				Call::withdraw_fees { withdrawal_data } => Self::withdraw(withdrawal_data.clone()),
				Call::claim_outbound_consensus_delivery_reward { claim } =>
					Self::process_outbound_consensus_delivery_claim(claim.clone()),
				Call::claim_outbound_request_delivery_reward { claim } =>
					Self::process_outbound_request_delivery_claim(claim.clone()),
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			if let Err(err) = res {
				log::error!(target: "ismp", "Pallet Relayer Fees error {err:?}");
				Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?
			}

			let encoding = match call {
				Call::accumulate_fees { withdrawal_proof } => withdrawal_proof.encode(),
				Call::withdraw_fees { withdrawal_data } => withdrawal_data.encode(),
				Call::claim_outbound_consensus_delivery_reward { claim } => claim.encode(),
				Call::claim_outbound_request_delivery_reward { claim } => claim.encode(),
				_ => unreachable!(),
			};

			let msg_hash = sp_io::hashing::keccak_256(&encoding).to_vec();

			Ok(ValidTransaction {
				priority: 100,
				requires: vec![],
				provides: vec![msg_hash],
				longevity: TransactionLongevity::MAX,
				propagate: true,
			})
		}
	}
```

**File:** docs/content/developers/explore/nexus/relayer.mdx (L25-27)
```text
## Withdrawals

If a relayer wishes to withdraw their fees, they can do so at any time. They simply need to sign a transaction to the relayer module showing that they possess the private key of the account in question. Recall that their account on the delivery chain is associated with any fees that they may have accumulated. This account scheme may be different from the Hyperbridge account scheme. To allow for this, the relayer can sign a withdrawal request with the private key of the account in question. The `pallet-ismp-relayer` module will then verify the signature and if it is valid, the module will dispatch a request to the `HostManager` to perform the withdrawal on the destination chain.
```
