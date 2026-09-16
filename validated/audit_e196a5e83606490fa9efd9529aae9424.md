Based on my investigation, I found a genuine analog to the "unsafe deserialization → unauthenticated remote code execution" bug class in the `pallet-hyper-fungible-token` module's ISMP callback, where cross-chain-message-controlled bytes are decoded straight into an executable `RuntimeCall` and dispatched, with an authentication branch that can bind execution to an origin without any cryptographic proof of ownership.

### Title
Unauthenticated dispatch of attacker-supplied `RuntimeCall` via HFT cross-chain calldata bypasses signature verification - (`modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` (the `IsmpModule` callback invoked for every delivered HFT bridge message) SCALE-decodes an attacker/app-supplied byte blob directly into a fully-privileged `T::RuntimeCall` and executes it via `Dispatchable::dispatch`. When the accompanying `SubstrateCalldata.signature` is omitted, the code skips all cryptographic authentication and derives the dispatch `origin` purely from the unauthenticated `message.from` field taken from the same untrusted message body, then runs the decoded call as `RawOrigin::Signed(origin)`.

### Finding Description
`on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs:50-212` processes every incoming HFT `PostRequest`. After minting/transferring tokens, it decodes optional calldata: [1](#0-0) 

The decoded `substrate_data.runtime_call` bytes are the raw, attacker/app-controlled payload from the cross-chain message body. If a `signature` is present, it is verified against `beneficiary` (the token recipient) — but if `signature` is `None`, the branch instead derives `origin` straight from `message.from`, with **no signature check whatsoever**: [2](#0-1) 

The only defensive check applied to the decoded call is `BaseCallFilter`, which filters call *types*, not call *authorization*: [3](#0-2) 

This mirrors the CVE's root cause: user-controlled bytes crossing a trust boundary are deserialized directly into an executable construct (`T::RuntimeCall`) and executed, with the security-critical decision (which account authorizes the action) taken from the same untrusted blob rather than from a verified credential.

### Impact Explanation
If the value placed into `message.from` at the EVM/source-chain sender's discretion is not strictly forced to equal the depositor's own address by every source-chain app contract, this allows execution of arbitrary (filter-permitted) runtime calls under the identity of any account, without ever presenting that account's signature — i.e., unauthorized app action / privilege impersonation reachable from a single relayed token-bridge message, satisfying "unauthorized app action" impact.

**Caveat (explicitly unverified):** I was not able to confirm within the available tool budget whether every EVM/source-chain contract that emits an HFT `PostRequest` (e.g., `HyperFungibleToken.sol`, `WrappedHyperFungibleToken.sol`, `BridgeToken.sol`) rigidly binds the encoded `message.from` field to `msg.sender` of the deposit call with no way for a caller to specify a different address. If it does bind strictly, the no-signature branch is a self-authorization mechanism (you can only ever act as yourself) and not exploitable for impersonation. If any code path allows the caller to set `from` independently of `msg.sender` (e.g., relayed/permit-style deposits, or a "deposit on behalf of" flow), the no-signature branch becomes full account impersonation. This binding should be verified against the actual Solidity source (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol` and siblings) before treating this as confirmed-exploitable, and the index did not resolve those files' exact `from` field derivation within the available searches.

### Likelihood Explanation
The `on_accept` path is reached by any unprivileged token bridger sending an ordinary HFT-mapped cross-chain transfer with non-empty calldata — no relayer collusion, governance compromise, or special privilege is required. If the source-chain `from` binding is not enforced, exploitation requires only crafting a message body with `data` containing a `SubstrateCalldata` with no signature and a chosen `runtime_call`.

### Recommendation
Require a valid signature (or equivalent cryptographic proof of authorization) for every dispatched `runtime_call`, unconditionally — do not allow an unauthenticated path that derives `origin` from unauthenticated message fields. If the "no signature" branch is intended for self-deposit convenience, verify at the pallet level (not just trust the source-chain encoding) that `message.from` is provably equal to the actual depositor, e.g., by having the ISMP dispatcher itself supply/attest the caller's identity rather than relying on app-encoded bytes.

### Proof of Concept
Not constructible with full confidence given the unresolved question of whether source-chain contracts constrain `message.from` to `msg.sender`. Conceptually: craft an HFT `PostRequest` body whose ABI-encoded `Message.data` decodes to a `SubstrateCalldata { signature: None, runtime_call: <arbitrary permitted call> }` and whose `Message.from` bytes equal a victim account's address bytes; deliver it through the normal bridge path. If the source-chain sender can set `from` independently of their own address, `on_accept` dispatches `<arbitrary permitted call>` with `RawOrigin::Signed(victim)` with no signature check, as shown at `modules/pallets/hyper-fungible-token/src/module.rs:176-200`.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-126)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

			let origin = if let Some(signature) = substrate_data.signature {
				let multi_signature = MultiSignature::decode(&mut &*signature)
					.map_err(HftError::SignatureDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-203)
```rust
			} else {
				let from_bytes = message.from.as_ref();
				if source.is_evm() {
					T::EvmToSubstrate::convert(H160::from_slice(
						&from_bytes[from_bytes.len() - 20..],
					))
				} else {
					let mut account = [0u8; 32];
					account.copy_from_slice(from_bytes);
					account.into()
				}
			};

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
		}
```
