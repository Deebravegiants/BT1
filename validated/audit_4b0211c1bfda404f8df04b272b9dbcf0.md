### Title
Unsigned cross-chain call dispatch via `message.from`-derived origin in `pallet-hyper-fungible-token::on_accept` - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The `on_accept` handler in the hyper-fungible-token ISMP module decodes an ABI-encoded `Message` from a `PostRequest` body and, if it carries non-empty `data`, decodes a SCALE-encoded `SubstrateCalldata { signature, runtime_call }` from it and dispatches `runtime_call` as a signed extrinsic. [1](#0-0)  When `signature` is `None`, the dispatch origin is derived directly from the `message.from` field — which is attacker-supplied ABI bytes inside the request body, not cryptographically bound to a signature — rather than from a verified signer. [2](#0-1) 

### Finding Description
`Message` is an ABI struct `{bytes from; bytes to; uint256 amount; bytes data;}` decoded from the untrusted request body of a `PostRequest` sent by the registered source-chain HFT contract. [3](#0-2)  The `from` field is just a byte string carried inside the payload — nothing here cryptographically proves it corresponds to the actual depositor who triggered the source-chain lock/burn, since I could not verify in the indexed contract sources that the EVM contract enforces `from == msg.sender` for every call path (this is unverified due to index coverage limits on the Solidity contract).

Critically, when `substrate_data.signature` is `None`, the pallet skips all cryptographic verification and instead computes the dispatch origin purely from `message.from`:
- If the source is EVM: `T::EvmToSubstrate::convert(H160::from_slice(&from_bytes[...]))`.
- Otherwise: the raw 32 bytes of `from_bytes` are used directly as `T::AccountId`. [4](#0-3) 

The `runtime_call` bytes are then SCALE-decoded and dispatched with `RawOrigin::Signed(origin)`: [5](#0-4) 

Because `SubstrateCalldata` is attacker-controlled data inside the message body, an attacker who can make the source-chain HFT contract emit any `from` value (e.g., by calling a transfer/relay function where `from` is a caller-suppliable parameter instead of `msg.sender`) can set `message.from` to any 32-byte or 20-byte value, causing the pallet to dispatch an arbitrary `RuntimeCall` as though it were signed by that arbitrary account — with no signature check at all. The only gate is `BaseCallFilter::contains`, which filters call types, not the origin/account used. [6](#0-5) 

This differs from the CVE's Java root cause (unauthenticated object graph deserialization enabling gadget-chain code execution) but shares the same bug class: an unprivileged, cross-boundary message carries a serialized executable unit (`SubstrateCalldata`/`RuntimeCall`) that is deserialized and then acted upon (dispatched) using attacker-supplied identity data, without an independent authenticity check tying the executable payload to the claimed principal.

### Impact Explanation
If the source-chain contract lets a caller specify an arbitrary `from` (rather than always using `msg.sender`), any unprivileged user reaching `on_accept` (by sending a valid PostRequest through a registered `ContractToAsset` source, which just requires making a normal cross-chain deposit) can forge the dispatch origin to be any account on the destination parachain and execute arbitrary `RuntimeCall`s as that account — e.g. transferring/withdrawing assets from a victim account without the victim's signature, subject only to `BaseCallFilter`. This is a critical unauthorized-app-action / unsigned-remote-code-execution class impact, matching the accept-criteria "unauthorized app action."

### Likelihood Explanation
Reachability requires only a single relayed, valid ISMP `PostRequest` from the registered token contract with a crafted `Message.data` containing `SubstrateCalldata{ signature: None, runtime_call: <arbitrary call> }`. Whether this is exploitable end-to-end hinges on whether the paired EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract lets the caller set `from` independently of `msg.sender` for the deposit/lock/teleport path — I was unable to confirm this definitively from the indexed Solidity contract content (index coverage limits prevented reading the full contract logic for the relevant function). If the contract always sets `from = msg.sender` and doesn't allow delegated calls on behalf of others, this reduces to "self-dispatch" (attacker can only dispatch calls as their own already-controlled account), which has no privilege-escalation impact. This uncertainty should be resolved by reviewing the EVM contract's send/lock function that populates the `Message.from` field.

### Recommendation
- Require a signature (or another cryptographic binding) whenever `data`/`runtime_call` is present, removing the unauthenticated `else` branch that derives origin solely from `message.from`.
- Alternatively, always derive the origin from `beneficiary` (the already-validated recipient) rather than from `message.from`, and require a signature check binding `runtime_call` to that beneficiary in all cases.
- Confirm, in the paired EVM contract, that `from` cannot be spoofed to an address other than `msg.sender` for any function that sets the `Message.from` field, and add that invariant as either a Solidity assertion or a documented pallet-side re-validation.

### Proof of Concept
1. Attacker holds an account with no special privileges on the destination parachain but knows a target account address `V` they want to act as.
2. Attacker (or an already-registered/valid source contract call path) triggers a token bridge message where the ABI `Message.from = V`'s bytes and `Message.data` is a SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <call performing an action as V, e.g. transferring V's assets> }`.
3. The relayer delivers the resulting `PostRequest` to `pallet-hyper-fungible-token::on_accept`.
4. `on_accept` decodes `Message`, skips signature verification because `signature` is `None`, derives origin from `message.from = V`, and dispatches `runtime_call` with `RawOrigin::Signed(V)` — executing the call as `V` without `V`'s authorization. [7](#0-6) 

Note: step 2's exploitability depends on the EVM-side contract permitting an attacker to set `from` to an arbitrary address rather than enforcing `from == msg.sender`; this could not be confirmed from the indexed contract content and should be verified directly in the repository (`sdk/packages/core/contracts/apps/HyperFungibleToken.sol` / `HyperFungibleTokenUpgradeable.sol`) before treating this as a confirmed exploitable path.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-202)
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
```

**File:** modules/pallets/hyper-fungible-token/src/types.rs (L33-43)
```rust
// ABI-compatible Message matching the Solidity HyperFungibleToken.Message struct:
// struct Message { bytes from; bytes to; uint256 amount; bytes data; }
alloy_sol_macro::sol! {
	#![sol(all_derives)]
	struct Message {
		bytes from;
		bytes to;
		uint256 amount;
		bytes data;
	}
}
```
