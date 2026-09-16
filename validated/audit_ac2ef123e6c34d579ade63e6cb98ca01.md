### Title
Unsigned cross-chain calldata dispatches an arbitrary `RuntimeCall` as the *message sender's* derived account without requiring that sender's authorization - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
The CVE describes eval-injection: attacker-controlled input reaches a code-execution sink without adequate authorization/sanitization. The closest reachable analog in Hyperbridge is `HyperFungibleToken::on_accept`, an ISMP module handler invoked for every cross-chain token-transfer message relayed to this chain. When the message carries optional `data`, it is decoded into `SubstrateCalldata { signature: Option<Vec<u8>>, runtime_call: Vec<u8> }` and, if no `signature` is supplied, the pallet derives an origin **directly from the message's `from` field** and dispatches the attacker-chosen `runtime_call` as that origin — with no proof that the actual holder of that derived account authorized this specific call.

### Finding Description
`on_accept` decodes `message.data` as `SubstrateCalldata` [1](#0-0) . When `substrate_data.signature` is `None`, the origin used for dispatch is computed purely from `message.from` — the sender field of the cross-chain post request, which is fully controlled by whoever calls the source-chain `HyperFungibleToken`/`WrappedHyperFungibleToken` contract (an unprivileged token bridger) [2](#0-1) . The decoded `runtime_call` is only checked against the `BaseCallFilter`, then dispatched with `RawOrigin::Signed(origin)` [3](#0-2) .

Because `from` is attacker-supplied bytes on the source chain (any EVM address or arbitrary 32 bytes for non-EVM sources) that get mapped 1:1 to a substrate `AccountId` via `EvmToSubstrate::convert` or direct byte copy, an attacker can pick `from` to equal the SS58 byte representation of *any* victim account (or a pallet-controlled account, e.g. `Pallet::<T>::pallet_account()` which is derived deterministically) and cause a `RuntimeCall` of their choosing to execute "signed by" that account — without the victim/target ever approving a specific `runtime_call`. This is functionally an unauthenticated code-execution sink reachable by a single cross-chain message from an unprivileged bridger, echoing the CVE's pattern of unsanitized attacker input reaching an execution primitive.

The unsigned path exists as a deliberate feature (execute calldata as the sender's mirrored account without requiring a signature when the call is "self-authorizing" by convention), but the implementation trusts the *message field* as sufficient identity proof for dispatch authority, rather than requiring the message relay itself to be cryptographically tied to that specific `runtime_call`. Any account whose corresponding 20/32-byte representation can be forged as a `from` value (all of them, since `from` is arbitrary bytes chosen by the caller of the source contract) is dispatchable-against.

### Impact Explanation
An attacker can force execution of arbitrary permitted `RuntimeCall`s "as" the pallet's own custody account (`Pallet::<T>::pallet_account()`) or as any other derivable account, by crafting `message.from` to match that account's byte encoding and sending a message with `SubstrateCalldata{ signature: None, runtime_call: <malicious call> }`. If the pallet account or any known-address account holds privileges (e.g., is a proxy, has approvals, holds funds subject to `transfer`/`approve`-style calls not blocked by the base filter), this allows theft or manipulation of state under that account's authority — a Critical-class unauthorized-app-action / fund-theft primitive reachable from a single cross-chain post request.

### Likelihood Explanation
High. `on_accept` runs on every relayed cross-chain token message from a registered contract on a registered source chain — an unprivileged relayer/token-bridger interaction that anyone can trigger by calling the source-chain HFT/WrappedHFT contract with a chosen `from` and `data` payload and having a relayer deliver the ISMP post request. No signature is required for this path by design; only `ContractToAsset` mapping validity and `BaseCallFilter::contains` gate execution.

### Recommendation
Require a valid signature (or an equivalent cryptographic binding) for *every* `SubstrateCalldata` execution, tying the specific `runtime_call` bytes to the account it will be dispatched as — do not allow the unsigned branch to derive dispatch authority solely from the attacker-controlled `message.from` field. If the "no signature" convenience path is intentional (e.g., only for self-transfers with no privileged effect), restrict it to a narrow allow-list of calls (e.g., only benign local accounting calls) rather than any `BaseCallFilter`-passing call, and explicitly forbid it from resolving to the pallet's own custody account or other privileged accounts.

### Proof of Concept
1. Attacker calls the source-chain `HyperFungibleToken` contract's send function, setting `message.from` to the 20-byte (or 32-byte) representation of a target account (e.g., the pallet's derived custody account on the destination chain) and `message.data` to SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <encoded privileged call, e.g. Balances::transfer_all or an asset transfer from that account> }`.
2. A relayer delivers the resulting ISMP `PostRequest` to the destination chain; `HyperFungibleToken::on_accept` processes it [4](#0-3) .
3. Since `substrate_data.signature` is `None`, the origin is computed from `message.from` alone [2](#0-1) .
4. `runtime_call` is decoded and dispatched as `RawOrigin::Signed(origin)` after only a `BaseCallFilter` check [3](#0-2) , executing the attacker's chosen call under the impersonated account's authority.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-59)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;

		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-123)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L176-187)
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
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-200)
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
```
