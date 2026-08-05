This confirms the design. The `Checkable::check` implementation constructs the signature payload from `CallAndMaybeEncoded { encoded: self.encoded_call, call: self.function }` combined with `tx_ext`, and verifies the signature against this payload before any transaction extension (including `CheckNonce`) is even invoked. This binds the call, the extension data, and the signature together cryptographically at decode/check time.

### Title
No vulnerability found - nonce `provides`/`requires` tags cannot be used to substitute a different call - (File: substrate/frame/system/src/extensions/check_nonce.rs)

### Summary
The premise that `provides`/`requires` tag matching in `CheckNonce::validate_nonce_for_account` could allow a "different call" to be slotted into a victim's validated nonce sequence is not supported by the code. The `provides`/`requires` tags are derived purely from `(who, nonce)` as the question itself anticipates, but this is not a gap — it is safe precisely because the call and signature are bound together and verified before extensions run, and no reachable path lets the transaction pool substitute a different call payload while reusing the tags of an already-signed extrinsic without forging the signature.

### Finding Description
`validate_nonce_for_account` at [1](#0-0)  computes `provides = Encode::encode(&(who, nonce))` and `requires` from `(who, nonce - 1)`. These tags are only consumed by the transaction pool's dependency graph to decide ordering/eligibility among transactions in the pool, not to select which call payload gets executed. The call payload itself is fixed to the specific extrinsic bytes decided at construction time.

Before `CheckNonce::validate` or `prepare` ever run, `Checkable::check` for `UncheckedExtrinsic` (the signed preamble path) builds the `SignedPayload` from `CallAndMaybeEncoded { encoded: self.encoded_call, call: self.function }` together with the transaction extensions (`tx_ext`), hashes it if large, and calls `signature.verify(payload.as_ref(), &signed)`, rejecting with `InvalidTransaction::BadProof` on mismatch, as seen at [2](#0-1) . This means the call `C1` and the specific `CheckNonce` value (nonce `N`) that will be used in `prepare` are cryptographically bound to the victim's signature; an attacker who cannot forge the victim's signature cannot produce a second extrinsic with a *different* call `C2` but the *same* signature that would validate.

Consequently, at the pool level, an attacker's own transaction (call `C2`, nonce `N`, different signature) is a distinct extrinsic with its own signature check. It may indeed also produce `provides = (who, N)` if — hypothetically — it were signed by `who`, but the attacker cannot produce a valid signature for the victim's account without the private key (stated precondition: cannot forge signature). If the attacker instead tries to submit a transaction *purporting* to be from `who` with a bad signature, `Checkable::check` rejects it with `BadProof` before `CheckNonce::validate` is even reached, so it never enters the transaction pool as a "valid" transaction with those tags at all.

The pool mechanic where two transactions from the *same* signer with the *same* nonce collide on the `provides` tag is intentional and well known: only one of them (chosen by priority/first-seen policy) occupies that pool slot, and the other is dropped/pending — but both would have to be validly signed by the same account for their `provides` tags to collide in the first place. There is no path by which the tag mechanism causes the runtime to *execute* a call other than the one whose signature was verified for that specific nonce during `prepare_nonce_for_account`, since `prepare` operates on the decoded `CheckedExtrinsic`'s own `self.0` (the nonce embedded in that exact checked extrinsic) and its own `function`/call, not on some pool-tag-derived value.

### Impact Explanation
No impact. Call execution is strictly tied to the specific `CheckedExtrinsic` produced by `Checkable::check`, which already verified the signature over the call and extension data. The `provides`/`requires` tags only affect transaction-pool ordering/inclusion decisions among competing valid transactions, never which call payload is dispatched for a given signature.

### Likelihood Explanation
Not applicable — the described substitution requires either forging the victim's signature (explicitly excluded by preconditions) or a code path where dispatch content is chosen independently of the verified signature payload, which does not exist in `check_nonce.rs`, `unchecked_extrinsic.rs`'s `Checkable::check`, or the executive's `do_apply_extrinsic`/`validate_transaction` ( [3](#0-2) ).

### Recommendation
No fix needed for this scoped concern. If auditing further, confirm that any custom `TransactionExtension` compositions (e.g., `VerifySignature`, `AuthorizeCall`) that authorize an origin without the classic `Checkable::check` signed preamble still bind their authorization payload to the specific call and subsequent extension data before nonce or dispatch logic runs, which is the pattern already followed by `VerifySignature::validate` ( [4](#0-3) ).

### Proof of Concept
Not applicable; no exploitable gap exists to reproduce. A confirmatory test would simply assert that `Checkable::check` rejects an extrinsic where the call bytes differ from those covered by the signature (`BadProof`), which is already covered by existing tests such as `badly_signed_check_should_fail` and `large_signed_check_fails_if_signed_over_unhashed_payload` at [5](#0-4)  and [6](#0-5) .

### Citations

**File:** substrate/frame/system/src/extensions/check_nonce.rs (L70-91)
```rust
	pub fn validate_nonce_for_account(
		who: &T::AccountId,
		nonce: T::Nonce,
	) -> Result<ValidNonceInfo, TransactionValidityError> {
		let account = crate::Account::<T>::get(who);
		if account.providers.is_zero() && account.sufficients.is_zero() {
			// Nonce storage not paid for
			return Err(InvalidTransaction::Payment.into());
		}
		if nonce < account.nonce {
			return Err(InvalidTransaction::Stale.into());
		}

		let provides = vec![Encode::encode(&(who.clone(), nonce))];
		let requires = if account.nonce < nonce {
			vec![Encode::encode(&(who.clone(), nonce.saturating_sub(One::one())))]
		} else {
			vec![]
		};

		Ok(ValidNonceInfo { provides, requires })
	}
```

**File:** substrate/primitives/runtime/src/generic/unchecked_extrinsic.rs (L657-679)
```rust
	fn check(self, lookup: &Lookup) -> Result<Self::Checked, TransactionValidityError> {
		Ok(match self.preamble {
			Preamble::Signed(signed, signature, tx_ext) => {
				let signed = lookup.lookup(signed)?;
				// The `Implicit` is "implicitly" included in the payload.
				let raw_payload = SignedPayload::new(
					CallAndMaybeEncoded { encoded: self.encoded_call, call: self.function },
					tx_ext,
				)?;

				let mut payload = Vec::with_capacity(self.encoded_len.unwrap_or_default());
				raw_payload.0.encode_to(&mut payload);

				let payload =
					if payload.len() > 256 { blake2_256(&payload).to_vec() } else { payload };

				if !signature.verify(payload.as_ref(), &signed) {
					return Err(InvalidTransaction::BadProof.into());
				}

				let (function, tx_ext, _) = raw_payload.deconstruct();
				CheckedExtrinsic { format: ExtrinsicFormat::Signed(signed, tx_ext), function }
			},
```

**File:** substrate/primitives/runtime/src/generic/unchecked_extrinsic.rs (L1337-1350)
```rust
	#[test]
	fn badly_signed_check_should_fail() {
		let ux = Ex::new_signed(
			vec![0u8; 0].into(),
			TEST_ACCOUNT,
			TestSig(TEST_ACCOUNT, vec![0u8; 0].into()),
			DummyExtension,
		);
		assert!(!ux.is_inherent());
		assert_eq!(
			<Ex as Checkable<TestContext>>::check(ux, &Default::default()),
			Err(InvalidTransaction::BadProof.into()),
		);
	}
```

**File:** substrate/primitives/runtime/src/generic/unchecked_extrinsic.rs (L1422-1438)
```rust
	#[test]
	fn large_signed_check_fails_if_signed_over_unhashed_payload() {
		// If the signer (incorrectly) signs the *raw* > 256 byte payload instead of the
		// blake2_256 hash, `check` must reject it with `BadProof` because `check` always
		// hashes payloads that exceed 256 bytes.
		let large_call_data = vec![0u8; 257];
		let call: TestCall = large_call_data.into();
		let raw_payload = (call.clone(), DummyExtension, ()).encode();
		assert!(raw_payload.len() > 256);

		let ux =
			Ex::new_signed(call, TEST_ACCOUNT, TestSig(TEST_ACCOUNT, raw_payload), DummyExtension);
		assert_eq!(
			<Ex as Checkable<TestContext>>::check(ux, &Default::default()),
			Err(InvalidTransaction::BadProof.into()),
		);
	}
```

**File:** substrate/frame/executive/src/lib.rs (L857-895)
```rust
	fn do_apply_extrinsic(
		uxt: Block::Extrinsic,
		is_inherent: bool,
		check: impl FnOnce(
			Block::Extrinsic,
			&Context,
		) -> Result<CheckedOf<Block::Extrinsic, Context>, TransactionValidityError>,
	) -> ApplyExtrinsicResult {
		sp_io::init_tracing();
		let encoded = uxt.encode();
		let encoded_len = encoded.len();
		sp_tracing::enter_span!(sp_tracing::info_span!(
			"apply_extrinsic",
			ext=?sp_core::hexdisplay::HexDisplay::from(&encoded)
		));

		let uxt = <Block::Extrinsic as codec::DecodeLimit>::decode_all_with_depth_limit(
			MAX_EXTRINSIC_DEPTH,
			&mut &encoded[..],
		)
		.map_err(|_| InvalidTransaction::Call)?;

		// Verify that the signature is good.
		let xt = check(uxt, &Context::default())?;

		let dispatch_info = xt.get_dispatch_info();

		if !is_inherent && !<frame_system::Pallet<System>>::inherents_applied() {
			Self::inherents_applied();
		}

		// We don't need to make sure to `note_extrinsic` only after we know it's going to be
		// executed to prevent it from leaking in storage since at this point, it will either
		// execute or panic (and revert storage changes).
		<frame_system::Pallet<System>>::note_extrinsic(encoded);

		// AUDIT: Under no circumstances may this function panic from here onwards.

		let r = Applyable::apply::<UnsignedValidator>(xt, &dispatch_info, encoded_len)?;
```

**File:** substrate/frame/verify-signature/src/extension.rs (L138-154)
```rust
		// Construct the payload that the signature will be validated against. The inherited
		// implication contains the encoded bytes of the call and all of the extension data of the
		// extensions that follow in the `TransactionExtension` pipeline.
		//
		// In other words:
		// - extensions that precede this extension are ignored in terms of signature validation;
		// - extensions that follow this extension are included in the payload to be signed (as if
		//   they were the entire `SignedExtension` pipeline in the traditional signed transaction
		//   model).
		//
		// The encoded bytes of the payload are then hashed using `blake2_256`.
		let msg = inherited_implication.using_encoded(blake2_256);

		// The extension was enabled, so the signature must match.
		if !signature.verify(&msg[..], account) {
			Err(InvalidTransaction::BadProof)?
		}
```
