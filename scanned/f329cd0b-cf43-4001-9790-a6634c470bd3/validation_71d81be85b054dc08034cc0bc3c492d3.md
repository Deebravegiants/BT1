### Title
Lack of permit-cancellation functionality allows execution of stale/unwanted signed approvals - (File: `substrate/frame/assets/precompiles/src/permit.rs`)

### Summary
The EIP-2612-style `permit` pallet used by the assets precompiles stores a nonce per `(verifying_contract, owner)` pair and only advances it inside `use_permit`, which is invoked when a permit signature is actually consumed. There is no dispatchable or precompile-exposed function that lets the `owner` proactively invalidate/cancel a permit signature they have created but not yet submitted (or that a relayer is holding), analogous to the `SessionOrderModule.sol` finding where a user has no way to cancel an already-signed order before it is executed by a third party.

### Finding Description
`Nonces<T>` is only mutated by `Pallet::<T>::increment_nonce`, which is called from `use_permit` on successful verification/consumption of a permit. [1](#0-0) 

The only other nonce read path, `verify_permit`/`do_verify_permit`, is explicitly documented as *not* incrementing the nonce, and is meant purely for verification, not cancellation: [2](#0-1) 

The digest itself is derived deterministically from the current on-chain nonce (`Self::nonce(verifying_contract, owner)`), so the only way to invalidate a previously-signed permit is to advance the nonce — and the only code path that advances it is successful consumption via `use_permit`. [3](#0-2) 

Searching the pallet and its precompile dispatcher (`lib.rs`) for any owner-invocable "cancel permit" / "invalidate nonce" / "revoke" operation shows only `cancel_approval` calls related to `pallet_assets` allowance bookkeeping inside the `permit` precompile function itself (used to reset an existing allowance before writing a new one) — there is no user-facing entry point to burn/invalidate an unconsumed permit signature independently of submitting (and thereby executing) it. [4](#0-3) 

This mirrors the reported `SessionOrderModule.sol` issue: a signer produces an off-chain signed authorization (a permit, bound by a self-chosen `deadline`) that a relayer/anyone can submit at any point until expiry, and the signer has no on-chain mechanism to cancel it earlier — e.g., if they change their mind about the approval, or if the signature leaks from their wallet/relayer infrastructure before intended submission.

### Impact Explanation
An attacker or a compromised/malicious relayer holding a valid, not-yet-submitted permit signature can submit it at any time up to the signer-chosen `deadline`, granting the `spender` the approved allowance even after the signer no longer wants that approval to take effect. Because allowances translate directly into fund-transfer capability (`transferFrom`), this can result in unwanted token movement by the approved spender. Impact is bounded by the deadline window the signer chose when signing, but there is no way to shorten that window once signed.

### Likelihood Explanation
Likelihood is realistic for any user relying on off-chain relayers (a core intended use case of EIP-2612 permits) or for any user who signs with a long-lived deadline for convenience. Any leaked or intentionally-shared permit signature remains valid and exploitable until its deadline with no recourse for the signer to cancel it.

### Recommendation
Add an owner-callable dispatchable/precompile function (e.g. `cancel_permit` / `invalidate_nonce`) that lets `owner` bump `Nonces::<T>` for a given `verifying_contract` without granting any approval, similar in spirit to the recommendation in the external report ("mark the nonce as used"), restricted so only the `owner` (the account whose nonce is being invalidated) can call it.

### Proof of Concept
1. Owner signs a permit off-chain: `permit(owner=Alice, spender=Bob, value=1000, deadline=T+7days)` at nonce `n`.
2. Owner shares/relays this signature intending immediate submission by a relayer, then changes their mind (e.g., decides not to authorize Bob, or suspects the relayer/signature was leaked).
3. Owner has no function to call to invalidate nonce `n` for that `verifying_contract`; calling `verify_permit` does not mutate state, and there is no `cancel`/`revoke` entry point in `permit.rs` or the precompile dispatcher in `lib.rs`.
4. At any time before `T+7days`, Bob (or anyone with the signature) calls the precompile's `permit(...)`, which succeeds via `use_permit`, granting the allowance the owner no longer wanted to grant. [5](#0-4)

### Citations

**File:** substrate/frame/assets/precompiles/src/permit.rs (L133-146)
```rust
	impl<T: Config> Pallet<T> {
		/// Get the current nonce for an owner on a specific verifying contract.
		pub fn nonce(verifying_contract: &H160, owner: &H160) -> U256 {
			Nonces::<T>::get(verifying_contract, owner)
		}

		/// Increment the nonce for an owner on a specific verifying contract.
		/// Returns the new nonce value, or an error if overflow would occur.
		pub fn increment_nonce(verifying_contract: &H160, owner: &H160) -> Result<U256, Error<T>> {
			Nonces::<T>::try_mutate(verifying_contract, owner, |nonce| {
				*nonce = nonce.checked_add(U256::one()).ok_or(Error::<T>::NonceOverflow)?;
				Ok(*nonce)
			})
		}
```

**File:** substrate/frame/assets/precompiles/src/permit.rs (L301-309)
```rust
		/// Verify a permit signature without consuming it.
		///
		/// **WARNING**: This function does NOT increment the nonce. Using this
		/// function alone will leave the permit vulnerable to replay attacks.
		/// Use `use_permit` instead for production code.
		///
		/// This function is provided for cases where you need to verify a permit
		/// in a read-only context or need to separate verification from consumption.
		///
```

**File:** substrate/frame/assets/precompiles/src/permit.rs (L344-353)
```rust
			let nonce = Self::nonce(verifying_contract, owner);
			let digest = Self::permit_digest(
				verifying_contract,
				name,
				owner,
				spender,
				value,
				&nonce,
				deadline,
			);
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L478-531)
```rust
	pub(crate) fn permit(
		asset_id: <Runtime as Config<Instance>>::AssetId,
		verifying_contract: H160,
		call: &IERC20::permitCall,
		env: &mut impl Ext<T = Runtime>,
	) -> Result<Vec<u8>, Error> {
		// Reserve worst-case gas upfront, then refund the unused portion.
		// The total cost is: use_permit (signature verification + nonce) +
		// worst-case asset approval operations (allowance read + cancel + approve).
		let use_permit_weight = <Runtime as permit::Config>::WeightInfo::use_permit();
		let worst_case = use_permit_weight
			.saturating_add(<Runtime as Config<Instance>>::WeightInfo::allowance())
			.saturating_add(<Runtime as Config<Instance>>::WeightInfo::cancel_approval())
			.saturating_add(<Runtime as Config<Instance>>::WeightInfo::approve_transfer());
		let charged = env.charge(worst_case)?;

		let owner_h160: H160 = call.owner.into_array().into();
		let spender_h160: H160 = call.spender.into_array().into();

		// Convert U256 values to byte arrays
		let value_bytes: [u8; 32] = call.value.to_be_bytes();
		let deadline_bytes: [u8; 32] = call.deadline.to_be_bytes();
		let r_bytes: [u8; 32] = call.r.0;
		let s_bytes: [u8; 32] = call.s.0;

		let transaction_outcome = frame_support::storage::with_transaction(|| {
			let result = (|| {
				// Use the permit - this validates deadline, signature, and increments nonce
				permit::Pallet::<Runtime>::use_permit(
					&verifying_contract,
					&pallet_assets::Pallet::<Runtime, Instance>::name(asset_id.clone()),
					&owner_h160,
					&spender_h160,
					&value_bytes,
					&deadline_bytes,
					call.v,
					&r_bytes,
					&s_bytes,
				)
				.map_err(|e| {
					let msg = match e {
						permit::pallet::Error::PermitExpired => "Permit expired",
						permit::pallet::Error::InvalidSignature => "Invalid signature",
						permit::pallet::Error::SignerMismatch => "Signer does not match owner",
						permit::pallet::Error::SignatureSValueTooHigh => {
							"Signature s value too high (malleability)"
						},
						permit::pallet::Error::InvalidVValue => "Invalid signature v value",
						permit::pallet::Error::NonceOverflow => "Nonce overflow",
						permit::pallet::Error::InvalidOwner => "Invalid owner address",
						permit::pallet::Error::InvalidSpender => "Invalid spender address",
					};
					Error::Revert(Revert { reason: msg.into() })
				})?;
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L533-559)
```rust
				// Delete-set semantic: cancel any existing approval first so
				// do_approve_transfer sets (not accumulates) the new value.
				use frame_support::traits::fungibles::approvals::Inspect as ApprovalsInspect;
				let owner_account =
					<Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&owner_h160);
				let spender_account =
					<Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&spender_h160);

				// Saturate: see `approve` for the rationale (infinite-allowance idiom).
				let new_amount: <Runtime as Config<Instance>>::Balance =
					call.value.unique_saturated_into();
				let current = pallet_assets::Pallet::<Runtime, Instance>::allowance(
					asset_id.clone(),
					&owner_account,
					&spender_account,
				);

				let actual_weight;
				if new_amount.is_zero() {
					if !current.is_zero() {
						// clear approval if it exists, to match ERC-20 semantics of setting
						// allowance to 0
						pallet_assets::Pallet::<Runtime, Instance>::do_cancel_approval(
							&asset_id,
							&owner_account,
							&spender_account,
						)?;
```
