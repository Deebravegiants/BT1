### Title
Missing Domain Separation in `SubstrateCalldata` Signature Allows Cross-Chain Replay of Arbitrary Runtime-Call Dispatch - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
The Jenkins Splunk advisory describes a validation endpoint that compiled and executed user-supplied code without the sandbox restrictions the rest of the system relied on, letting an unprivileged caller escape the intended trust boundary. `pallet-hyper-fungible-token`'s `on_accept` handler has an analogous trust-boundary gap: the "authorization" for an arbitrary `RuntimeCall` dispatched on behalf of a beneficiary is a signature over a bare `(nonce, runtime_call)` tuple with no domain separator — no genesis hash, chain identifier, pallet discriminator, or source-message binding — so a signature legitimately produced for one destination chain/message can be replayed to authorize the same privileged dispatch on any other chain/context running this pallet.

### Finding Description
In `on_accept`, when cross-chain calldata is attached to an HFT transfer, the pallet decodes `SubstrateCalldata { signature: Option<Vec<u8>>, runtime_call: Vec<u8> }` and, if a signature is present, verifies it as: [1](#0-0) 

The signed payload is only `(nonce, runtime_call).encode()`, hashed with `keccak_256`, then verified against the beneficiary's public key bytes. There is no inclusion of:
- the destination `StateMachine` / chain identifier,
- the source chain or contract that relayed the message,
- a pallet- or protocol-specific domain tag identifying this as "HFT calldata authorization".

Only `BaseCallFilter` gates which calls can be dispatched, and dispatch proceeds with full `Signed` origin of the beneficiary: [2](#0-1) 

Because ISMP requests (and thus the embedded `SubstrateCalldata`) are publicly visible on Hyperbridge (any relayer can read/replay dispatched requests), and because `account_nonce` is scoped per-chain (fresh parachains, testnets, or additional deployments of the same runtime template routinely have coinciding nonces, e.g. `0` for freshly funded accounts), a signature a user produces to authorize a call on one destination chain is cryptographically valid input for the identical check on any other chain/instance of this pallet where the beneficiary's nonce happens to match. There is nothing in the signed bytes that ties the authorization to a specific destination chain, message, or even to this specific `on_accept` invocation, so an unprivileged relayer who observes one such signed payload can construct a new cross-chain HFT message (via any registered peer contract) that reuses the exact `signature` and `runtime_call` bytes to force dispatch on a chain/context the beneficiary never intended.

This mirrors the Jenkins bug class precisely: a code-path meant to gate a powerful capability (arbitrary AST-transform-capable Groovy compilation there; arbitrary `RuntimeCall::dispatch` with `Signed` origin here) omits the contextual restriction (sandboxed compiler config there; message/domain binding here) that the rest of the system assumes is present.

### Impact Explanation
A successful replay lets an attacker force `RuntimeCall::dispatch` with `RawOrigin::Signed(beneficiary)` for a call the beneficiary authorized only in a different context, on a chain/timing they did not intend. Depending on the reused `runtime_call` (e.g. a `Balances::transfer`, an `Assets` operation, a governance vote, or any call passing `BaseCallFilter`), this is unauthorized app action performed under the victim's identity — potentially resulting in fund transfers out of the victim's account or other privileged state changes without the victim's contemporaneous consent. This satisfies the "unauthorized app action" / "forged message delivery" impact bar.

### Likelihood Explanation
Exploitation requires only: (1) observing one legitimately signed `SubstrateCalldata` payload (trivially available since ISMP requests are public and relayed by anyone), and (2) the target chain/context having the same account nonce as the original signing context (common for freshly initialized accounts or newly registered parachains sharing a runtime template) and a registered source contract mapping (`ContractToAsset`) that the attacker can route a message through. No signer cooperation or private key compromise is needed — the vulnerability is purely a missing-domain-separation replay, reachable by any unprivileged relayer/message dispatcher who can submit or route a cross-chain HFT `PostRequest`.

### Recommendation
Bind the signed payload to a unique, non-replayable context: include a domain separator (e.g. a fixed pallet identifier string), the destination `StateMachine`, the source `StateMachine`/contract, and the ISMP request's own nonce/commitment hash in the signed message, in addition to the account nonce and `runtime_call`. This ensures a signature is valid only for the exact chain, message, and account state it was created for.

### Proof of Concept
1. Victim signs `SubstrateCalldata` authorizing `runtime_call = Balances::transfer_allow_death(attacker, X)` for delivery on `Destination A`, with their account nonce `0` on chain A, per the pattern exercised in the pallet's own test: [3](#0-2) 
2. Attacker observes this signed `substrate_data` (public on Hyperbridge) and repackages it into a new `Message` body destined for `Destination B` — a different chain/instance running the same pallet where the victim's mapped account also has nonce `0` (e.g. a fresh parachain testnet or the same runtime deployed for a second network).
3. Attacker relays this crafted `PostRequest` through any HFT contract registered in `ContractToAsset` for that destination; `on_accept` verifies the *same* signature bytes against the *same* `(nonce=0, runtime_call)` hash — the check in lines 124-152 has no way to detect this is a different chain/context — and dispatches the call with `Signed(beneficiary)` origin on Destination B, moving the victim's funds there without their consent for that chain. [2](#0-1)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L124-152)
```rust
			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;

				let nonce = frame_system::Pallet::<T>::account_nonce(beneficiary.clone());

				match multi_signature {
					MultiSignature::Ed25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::ed25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Sr25519(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let msg = sp_io::hashing::keccak_256(&payload);
						let pub_key = beneficiary_bytes
							.as_slice()
							.try_into()
							.map_err(|_| HftError::SignatureVerificationFailed)?;
						if !sp_io::crypto::sr25519_verify(&sig, msg.as_ref(), &pub_key) {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-202)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
			// Apply the runtime's base call filter so that cross-chain calls cannot
			// reach dispatchables that the runtime has otherwise filtered out (e.g.
			// during a maintenance mode or a SafeMode period).
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;

			frame_system::Pallet::<T>::inc_account_nonce(origin);
```

**File:** modules/pallets/testsuite/src/tests/pallet_hyper_fungible_token.rs (L271-288)
```rust
		// Build a runtime call: transfer from beneficiary to a final recipient
		let final_recipient = AccountId32::new([5u8; 32]);
		let runtime_call =
			crate::runtime::RuntimeCall::Balances(pallet_balances::Call::transfer_allow_death {
				dest: final_recipient.clone(),
				value: SEND_AMOUNT,
			})
			.encode();

		// Sign with sr25519
		let (pair, ..) = sp_core::sr25519::Pair::generate();
		let beneficiary_bytes = pair.public().0;
		let payload = (0u64, runtime_call.clone()).encode();
		let message_hash = sp_io::hashing::keccak_256(&payload);
		let raw_signature = pair.sign(&message_hash);
		let multisignature = MultiSignature::Sr25519(raw_signature).encode();

		let substrate_data = SubstrateCalldata { signature: Some(multisignature), runtime_call };
```
