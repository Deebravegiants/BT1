Investigating the actual codebase (not the external Geth report, which is unrelated to this repo) shows a real analog of the same vulnerability class in `pallet-revive`'s Ethereum transaction validation path.

### Title
Expensive ECDSA signature recovery performed before cheap gas-price/chain-id checks in `pallet-revive` Ethereum transaction validation - (File: `substrate/frame/revive/src/evm/runtime.rs`)

### Summary
`EthExtra::try_into_checked_extrinsic`, which is invoked by `Checkable::check` for every unsigned `eth_transact` extrinsic (i.e. on every Ethereum-style transaction submitted to the node, including gossiped transactions validated via `validate_transaction`), performs a full secp256k1 ECDSA public-key recovery before performing the cheap `gas_price`/`chain_id` sufficiency checks that could reject the transaction for free.

### Finding Description
In `try_into_checked_extrinsic`, the sequence of operations is:
1. Decode the RLP `TransactionSigned` payload.
2. Reject unsupported tx types.
3. Call `tx.recover_eth_address()` — an ECDSA public-key recovery over secp256k1 (`secp256k1_ecdsa_recover`) — to obtain the signer. [1](#0-0) 
4. Only afterwards is `GenericTransaction::from_signed(...)` built and `tx.into_call::<Self::Config>(...)` called, which performs the cheap chain-id and `gas_price < base_fee` checks that reject the transaction with `InvalidTransaction::Call`/`InvalidTransaction::Payment`. [2](#0-1) [3](#0-2) 

These `chain_id` and `gas_price` fields are already present in the decoded, *unverified* RLP payload — they do not require knowing the recovered signer at all. `recover_eth_address()` performs an elliptic-curve point-recovery which succeeds (i.e., produces *some* address) for essentially any syntactically valid `(r, s, v)` triple, regardless of whether it corresponds to a real signer — it doesn't need to "verify" against a target public key, so an attacker does not need a genuine private key to make this operation execute its full cost.

This exactly mirrors the reported pattern: an expensive validation step (signature/crypto operation) is performed prior to a cheap resource/fee check, and a rejection at the cheap check "wouldn't cost the caller anything" since this all happens in `Checkable::check`, invoked from `frame_executive::Executive::validate_transaction` before any fee is charged. [4](#0-3) [5](#0-4) 

### Impact Explanation
Since `validate_transaction` is the entry point used by the transaction pool to validate transactions gossiped from unauthenticated peers, an attacker can submit a stream of `eth_transact` extrinsics with random-but-curve-valid `(r, s, v)` and a `gas_price` deliberately below `base_fee` (or an invalid `chain_id`). Each such transaction forces the validating node to execute a full ECDSA recovery before it is rejected by the trivial gas-price/chain-id comparison. This creates an asymmetric cost: crafting the spam transaction is cheap (no need for a valid keypair or funded account) while validating it costs the node a non-trivial EC computation, enabling a computational-resource exhaustion / DoS vector against the tx-pool validation path of any node running `pallet-revive`.

### Likelihood Explanation
High for any unprivileged network participant: `eth_transact` extrinsics can be freely constructed and gossiped without any prior state (no funded account, no valid signature over a real key needed), and `validate_transaction` is called for every extrinsic entering the pool.

### Recommendation
Reorder the checks in `try_into_checked_extrinsic` (`substrate/frame/revive/src/evm/runtime.rs`) so that the cheap, signer-independent checks currently embedded in `GenericTransaction::into_call` (`chain_id` validity and `gas_price >= base_fee`, in `substrate/frame/revive/src/evm/call.rs` lines 82-115) are performed directly on the decoded-but-unverified transaction fields *before* calling `tx.recover_eth_address()`. Only proceed to the expensive ECDSA recovery once the cheap fee/chain checks pass.

### Proof of Concept
1. Construct an RLP-encoded EIP-1559/legacy Ethereum transaction with `gas_price` set below the current `evm_base_fee()` (or an incorrect `chain_id`), and any syntactically valid 65-byte `(r, s, v)` signature (does not need to correspond to a funded/real account).
2. Submit repeated variants of this transaction (varying nonce/payload to bypass pool dedup) as `Call::eth_transact { payload }` extrinsics to the node's transaction pool.
3. Observe that each submission causes `Checkable::check` → `try_into_checked_extrinsic` to execute `recover_eth_address()` (full secp256k1 recovery) before being rejected by the `gas_price < base_fee` check in `into_call`, at zero cost to the attacker (no fee is ever charged since the transaction is rejected pre-dispatch).

### Citations

**File:** substrate/frame/revive/src/evm/runtime.rs (L189-199)
```rust
	fn check(self, lookup: &Lookup) -> Result<Self::Checked, TransactionValidityError> {
		if !self.0.is_signed() {
			if let Some(crate::Call::eth_transact { payload }) = self.0.function.is_sub_type() {
				log::trace!(
					target: LOG_TARGET,
					"eth_transact substrate tx hash: 0x{}",
					sp_core::hexdisplay::HexDisplay::from(&sp_crypto_hashing::blake2_256(&self.encode())),
				);
				let checked = E::try_into_checked_extrinsic(payload, self.encoded_size())?;
				return Ok(checked);
			};
```

**File:** substrate/frame/revive/src/evm/runtime.rs (L354-379)
```rust
		let tx = TransactionSigned::decode(&payload).map_err(|err| {
			log::debug!(target: LOG_TARGET, "Failed to decode transaction: {err:?}");
			InvalidTransaction::Call
		})?;

		// Check transaction type and reject unsupported transaction types
		match &tx {
			crate::evm::api::TransactionSigned::Transaction1559Signed(_) |
			crate::evm::api::TransactionSigned::Transaction2930Signed(_) |
			crate::evm::api::TransactionSigned::TransactionLegacySigned(_) => {
				// Supported transaction types, continue processing
			},
			crate::evm::api::TransactionSigned::Transaction7702Signed(_) => {
				log::debug!(target: LOG_TARGET, "EIP-7702 transactions are not supported");
				return Err(InvalidTransaction::Call);
			},
			crate::evm::api::TransactionSigned::Transaction4844Signed(_) => {
				log::debug!(target: LOG_TARGET, "EIP-4844 transactions are not supported");
				return Err(InvalidTransaction::Call);
			},
		}

		let signer_addr = tx.recover_eth_address().map_err(|err| {
			log::debug!(target: LOG_TARGET, "Failed to recover signer: {err:?}");
			InvalidTransaction::BadProof
		})?;
```

**File:** substrate/frame/revive/src/evm/runtime.rs (L381-394)
```rust
		let signer = <Self::Config as Config>::AddressMapper::to_fallback_account_id(&signer_addr);
		let base_fee = <Pallet<Self::Config>>::evm_base_fee();
		let tx = GenericTransaction::from_signed(tx, base_fee, None);
		let nonce = tx.nonce.unwrap_or_default().try_into().map_err(|_| {
			log::debug!(target: LOG_TARGET, "Failed to convert nonce");
			InvalidTransaction::Call
		})?;

		log::debug!(target: LOG_TARGET, "Decoded Ethereum transaction with signer: {signer_addr:?} nonce: {nonce:?}");
		log::trace!(target: LOG_TARGET, "Decoded Ethereum transaction was: {tx:?}");
		let call_info = tx.into_call::<Self::Config>(CreateCallMode::ExtrinsicExecution(
			encoded_len as u32,
			payload.to_vec(),
		))?;
```

**File:** substrate/frame/revive/src/evm/call.rs (L82-115)
```rust
		match (self.chain_id, self.r#type.as_ref()) {
			(None, Some(super::Byte(TYPE_LEGACY))) => {},
			(Some(chain_id), ..) => {
				if chain_id != <T as Config>::ChainId::get().into() {
					log::debug!(target: LOG_TARGET, "Invalid chain_id {chain_id:?}");
					return Err(InvalidTransaction::Call);
				}
			},
			(None, ..) => {
				log::debug!(target: LOG_TARGET, "Invalid chain_id None");
				return Err(InvalidTransaction::Call);
			},
		}

		let Some(gas) = self.gas else {
			log::debug!(target: LOG_TARGET, "No gas provided");
			return Err(InvalidTransaction::Call);
		};

		// Currently, effective_gas_price will always be the same as base_fee
		// Because all callers of `into_call` will prepare `tx` that way. Some of the subsequent
		// logic will not work correctly anymore if we change that assumption.
		let Some(effective_gas_price) = self.gas_price else {
			log::debug!(target: LOG_TARGET, "No gas_price provided.");
			return Err(InvalidTransaction::Payment);
		};

		if effective_gas_price < base_fee {
			log::debug!(
				target: LOG_TARGET,
				"Specified gas_price is too low. effective_gas_price={effective_gas_price} base_fee={base_fee}"
			);
			return Err(InvalidTransaction::Payment);
		}
```

**File:** substrate/frame/executive/src/lib.rs (L978-993)
```rust
		let xt = within_span! { sp_tracing::Level::TRACE, "check";
			uxt.check(&Default::default())
		}?;

		let dispatch_info = within_span! { sp_tracing::Level::TRACE, "dispatch_info";
			xt.get_dispatch_info()
		};

		if dispatch_info.class == DispatchClass::Mandatory {
			return Err(InvalidTransaction::MandatoryValidation.into());
		}

		within_span! {
			sp_tracing::Level::TRACE, "validate";
			xt.validate::<UnsignedValidator>(source, &dispatch_info, encoded.len())
		}
```
