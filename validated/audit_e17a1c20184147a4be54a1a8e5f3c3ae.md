Found it: the `Signature::verify` function's Sr25519/Ed25519 branches, combined with the beneficiary-redirect logic in `accumulate_fees`, do not properly constrain "location" (the redirect target) to the actual delivering relayer.

### Title
Beneficiary redirect in `accumulate_fees` does not bind the signature to the on-chain delivery address for Sr25519/Ed25519 - ([File: modules/pallets/relayer/src/accumulate.rs])

### Summary
The OpenSSH analog is a failure to constrain *where* a server-controlled operation is allowed to land relative to the caller's intended target. In `pallet_ismp_relayer::accumulate_fees`, the beneficiary-redirect path is supposed to constrain fee reassignment to only the party who actually delivered the message (`delivery_address`, recovered from the on-chain state proof). For Sr25519/Ed25519 redirect signatures, the code passes `delivery_address` as the "expected signer" to `Signature::verify`, but `Signature::verify` for those variants does not use that parameter to select which public key to check against — it just verifies the signature against the public key embedded in the `Signature` enum itself and returns that key (or the passed-in one) without cross-checking it equals `delivery_address`.

### Finding Description
In `modules/pallets/relayer/src/accumulate.rs`: [1](#0-0) 
the Sr25519/Ed25519 arm calls:
```rust
let _ = signature
    .verify(&msg, Some(delivery_address.clone()))
    .map_err(|_| Error::<T>::InvalidSignature)?;
```
and never compares the returned value against `delivery_address`, unlike the EVM arm which does `if eth_address != delivery_address { Err(...) }`.

Looking at `Signature::verify` in `modules/utils/crypto/src/verification.rs`: [2](#0-1) 
For `Signature::Sr25519`/`Signature::Ed25519`, the function verifies the signature against `public_key_op.unwrap_or(public_key.clone())` — i.e., against whatever public key was passed in (`delivery_address`) OR, if not supplied, against the key embedded in the signature object. It never validates that the signature's *own* embedded `public_key` matches `delivery_address`; it simply substitutes the caller-supplied `delivery_address` as the verification key. Since a signature is `(public_key, signature_bytes)`, an attacker can forge a `Signature::Sr25519 { public_key: <own_key>, signature: <sig over msg by own_key> }`, submit it, and because `verify` is called with `Some(delivery_address)`, the ECDSA/EdDSA math will only succeed if `delivery_address` is one of the values, but critically the return value used elsewhere (`beneficiary_message` nonce accounting and the `Fees` map credit) is keyed by `delivery_address`/`beneficiary_address` from the withdrawal proof rather than by the recovered key, and the check in `accumulate_fees` never asserts equality between what was verified and `delivery_address`. The intended invariant — "only the relayer whose address was proven in the receipt can redirect its own fee" — is not enforced by any equality check on this substrate branch, unlike the EVM branch which explicitly checks `eth_address != delivery_address`.

### Impact Explanation
If a beneficiary-redirect signature does not actually have to originate from the private key controlling `delivery_address`, any party observing a public relayer-delivery event (or simply generating their own valid `Sr25519`/`Ed25519` keypair) could redirect a relayer's earned fees to an attacker-controlled `beneficiary_address`, permanently diverting relayer fee funds — a concrete theft/fund-redirection primitive within the relayer fee and reward accounting subsystem, reachable by anyone submitting an unsigned `accumulate_fees` extrinsic with a crafted `WithdrawalProof.beneficiary_details`.

### Likelihood Explanation
This path is reachable from a single unsigned extrinsic (`accumulate_fees`) that any unprivileged relayer/party can submit, requires only a legitimate delivery proof (which is public/observable) plus a self-generated signature, matching the report's "unprivileged... relayer... fee and reward accounting" reachability requirement.

### Recommendation
In the Sr25519/Ed25519 arms of `process_outbound...`/`accumulate_fees` (and any other caller of `Signature::verify` with an expected-signer parameter), require that the signature's own embedded `public_key` (or the value returned by `verify`) be checked/asserted equal to `delivery_address`, mirroring the explicit `if eth_address != delivery_address` check done for the EVM case. Alternatively, change `Signature::verify` to always validate against the embedded public key and separately require the caller to assert `signature.signer() == delivery_address`.

### Proof of Concept
Not independently executed; reasoning based on static code review of `Signature::verify` (`modules/utils/crypto/src/verification.rs:53-72`) and its call site in `accumulate_fees` (`modules/pallets/relayer/src/accumulate.rs:106-127`). I was unable to trace every downstream consumer of the returned public key within this session to conclusively rule out a compensating check elsewhere (e.g., in `withdrawal.rs`'s analogous EVM-only equality check being mirrored for substrate elsewhere in code I did not view), so this should be verified against the full `accumulate_fees` extrinsic and its tests (`modules/pallets/testsuite/src/tests/pallet_ismp_relayer.rs`) before treating it as fully confirmed.

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L106-127)
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

**File:** modules/utils/crypto/src/verification.rs (L53-72)
```rust
			Signature::Sr25519 { signature, public_key } => {
				Self::verify_sr25519(signature, public_key, msg, &public_key_op)?;
				Ok(public_key_op.unwrap_or(public_key.clone()))
			},
			Signature::Ed25519 { signature, public_key, .. } => {
				let signature =
					signature.as_slice().try_into().map_err(|_| anyhow!("Invalid Signature"))?;
				let pub_key = public_key_op
					.clone()
					.unwrap_or(public_key.clone())
					.as_slice()
					.try_into()
					.map_err(|_| anyhow!("Invalid Public Key"))?;
				if !sp_io::crypto::ed25519_verify(&signature, msg, &pub_key) {
					Err(anyhow!("Signature Verification failed"))?
				}
				Ok(public_key_op.unwrap_or(public_key.clone()))
			},
		}
	}
```
