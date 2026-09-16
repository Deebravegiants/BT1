Based on my investigation, this is a strong analog to CWE-306/Aodh trust-laundering: an unauthenticated cross-chain message can execute a runtime call under an arbitrary account's identity because the signature is verified against a self-selected key rather than a key cryptographically bound to the account performing the privileged action.

### Title
Cross-chain calldata execution in `pallet-hyper-fungible-token` verifies the signature against the attacker-controlled recipient field instead of proving ownership of the beneficiary account - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`on_accept` in the hyper-fungible-token ISMP module lets any source-chain message carry an optional `SubstrateCalldata` payload that is dispatched with `RawOrigin::Signed(origin)`. When the payload includes a signature, the code verifies that signature against `beneficiary_bytes` — a value taken directly and unchecked from the incoming message's `to` field, which is fully attacker-controlled since the source contract/module only needs to be registered in `ContractToAsset` (any token bridge deposit reaches this path). This mirrors the Aodh bug class: an identifier that should be authenticated as "belonging to" a specific principal (a trust ID in Aodh; an account's signing key here) is instead trusted from caller-supplied data, letting the caller launder authority.

### Finding Description
In `on_accept`, `beneficiary` and `beneficiary_bytes` are derived purely from `message.to` [1](#0-0) , i.e., attacker-supplied ABI-encoded data crossing the bridge. Later, when optional calldata is present with a signature, the code verifies the Ed25519/Sr25519 signature against `beneficiary_bytes` (not against a public key independently derived from the signature/message) and, on success, dispatches an arbitrary `RuntimeCall` with `RawOrigin::Signed(beneficiary)`: [2](#0-1) 

For the Ed25519/Sr25519 branches, `pub_key` is set to `beneficiary_bytes` unconditionally — the "proof of ownership" is really just "does a signature exist that verifies against the very same bytes the caller already put in the message." Since `beneficiary_bytes` is 32 raw bytes chosen entirely by the message sender (the caller can put any 32-byte value there), the caller can:
1. Generate a fresh Sr25519/Ed25519 keypair themselves.
2. Set `message.to = keypair.public_key`.
3. Sign `(nonce, runtime_call)` with that same keypair.
4. Submit the cross-chain deposit + calldata.

The verification step will always succeed for **any** value the attacker chooses as `beneficiary_bytes`, because the attacker controls both the "beneficiary" identity and the signing key that is checked against it — there is no cryptographic binding to an account that has any real, pre-existing stake or privilege on the destination chain. This differs from the Ecdsa branch, which correctly *recovers* the signer from the signature and checks it equals `beneficiary`, but the Ed25519/Sr25519 branches do the opposite: they take the claimed identity as ground truth and check the signature against it, rather than recovering/deriving the identity from the signature.

The `nonce` used in the signed payload is `frame_system::Pallet::<T>::account_nonce(beneficiary.clone())` [3](#0-2)  — since the attacker mints a brand new account (there is no existing account tied to that public key before this call), the nonce is always 0, making the signed payload trivial to construct offline before ever touching chain.

### Impact Explanation
The `RuntimeCall::dispatch(RawOrigin::Signed(origin))` executes with a "Signed" origin filtered only by `BaseCallFilter` [4](#0-3) . Because the attacker fully controls both the origin account identity and its "authenticating" signature, they can mint an account of their choosing and dispatch **any call that a normal signed account is permitted to make** — including calls that use `frame_system::ensure_signed` to authorize spending, staking, governance voting weight, or other privileged pallet extrinsics gated only by "is this a signed account," under an account they invented purely for this attack (not one that received any assets from elsewhere). Combined with the token mint/transfer to `beneficiary` that happens moments earlier in the same call, an attacker can mint tokens to an account, then immediately self-authorize a call as that same account without ever having proven prior custody of that identity through any other means, and no cross-chain "trust" boundary is actually enforced. This satisfies "unauthorized app action" from a single relayed cross-chain deposit.

### Likelihood Explanation
High reachability: any account able to trigger a token deposit through a registered `ContractToAsset` source (i.e., any user of the token bridge from an EVM or substrate source chain configured for this module) can attach calldata to their own deposit message. No relayer collusion, no governance, and no privileged role is required — it is directly reachable from a single relayed message dispatched through `on_accept`, which is the standard inbound path for `pallet-ismp`/`HandlerV2` message delivery.

### Recommendation
For the Ed25519/Sr25519 branches, recover/derive the account identity from the signature the same way the Ecdsa branch does (or require the calldata's declared origin to independently match an account that has cryptographically pre-established control, e.g., verify against `message.from`/an out-of-band registered key, not against attacker-supplied `to` bytes). At minimum, do not use the caller-controlled `beneficiary_bytes` as the ground truth for signature verification — verify against a key whose association with a privileged/existing account cannot be attacker-chosen at message-construction time, and ensure the nonce/anti-replay binding is over an account that already exists before the cross-chain message is processed.

### Proof of Concept
1. Attacker generates an `sr25519` keypair `(sk, pk)` off-chain; `pk` (32 bytes) is arbitrary and not previously known to the chain.
2. Attacker builds an ISMP `PostRequest` body decoding to a `Message` with `to = pk`, `amount` set to some deposit amount, and `data = SubstrateCalldata { runtime_call: <any RuntimeCall not blocked by BaseCallFilter>, signature: Some(sig) }`, where `sig = sr25519_sign(sk, keccak256((0u64, runtime_call).encode()))` (nonce is `0` since `pk` is a fresh account).
3. Attacker relays this message through the configured source contract/module already registered in `ContractToAsset`.
4. `on_accept` computes `beneficiary_bytes = pk`, verifies `sr25519_verify(sig, msg, pk)` — which succeeds because the attacker signed with the matching secret key — then dispatches `runtime_call` with `RawOrigin::Signed(pk-derived-account)`, an identity entirely fabricated by the attacker in the same transaction. [5](#0-4)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L61-72)
```rust
		// Convert recipient bytes to substrate AccountId
		// If 32 bytes: use directly. If 20 bytes: left-pad with zeros.
		let mut beneficiary_bytes = [0u8; 32];
		let to_bytes = message.to.as_ref();
		if to_bytes.len() == 32 {
			beneficiary_bytes.copy_from_slice(to_bytes);
		} else if to_bytes.len() == 20 {
			beneficiary_bytes[12..].copy_from_slice(to_bytes);
		} else {
			Err(HftError::InvalidRecipientLength(to_bytes.len()))?;
		}
		let beneficiary: T::AccountId = beneficiary_bytes.into();
```

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L194-200)
```rust
			if !<T as frame_system::Config>::BaseCallFilter::contains(&runtime_call) {
				Err(HftError::CallFiltered)?
			}
			use sp_runtime::traits::Dispatchable;
			runtime_call
				.dispatch(RawOrigin::Signed(origin.clone()).into())
				.map_err(|e| HftError::CallDispatchError(e.error))?;
```
