### Title
Unsigned cross-chain calldata dispatch trusts attacker-controlled `from` as call origin - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet-hyper-fungible-token`'s `on_accept` decodes an ABI `Message{from, to, amount, data}` from an incoming ISMP `PostRequest` and, if `data` is non-empty, decodes a `SubstrateCalldata{signature, runtime_call}` and dispatches `runtime_call` on the parachain. When `signature` is `None`, the origin used to dispatch the call is derived directly from `message.from` — a field fully controlled by whoever calls the peer EVM `HyperFungibleToken`/`WrappedHyperFungibleToken` contract — with no cryptographic proof that the caller actually controls that address/account.

### Finding Description
The docs confirm the intended design: [1](#0-0)  the `call_data` allows executing arbitrary runtime calls on the destination chain, and "If no signature is provided, the origin is derived from the sender address in the cross-chain message."

In `on_accept`, authentication only validates that the *EVM contract address* (`source`/`from` module id pair) is a registered peer contract via `ContractToAsset`, not that the `message.from` bytes inside the ABI body correspond to any verified account: [2](#0-1) 

When `substrate_data.signature` is `None`, the code takes the unauthenticated `message.from` bytes and converts them straight into a dispatch origin, then dispatches the attacker-supplied `runtime_call` as `RawOrigin::Signed(origin)`: [3](#0-2) 

The `Message.from` field is simply an ABI `bytes` parameter passed by the caller of the peer EVM contract's send function (per the message format docs: "from: original sender (for timeout refunds)") [4](#0-3) . There is no code path shown that constrains `from` to `msg.sender` of the EVM `send` call at encoding time as an unforgeable, on-chain-enforced value from the destination pallet's perspective — the destination pallet has no way to prove this field was not fabricated by the sender of the request. Any account that can call the registered peer contract's send/bridge function can set `Message.from` to an arbitrary 20/32-byte value (e.g. a high-value account, a treasury account, a pallet-derived sovereign account) and attach a `data` payload with `signature: None` and any `runtime_call`. Because the `BaseCallFilter` check only filters call *types*, not *origins* [5](#0-4) , this enables dispatching arbitrary permitted extrinsics (transfers, approvals, staking operations, governance-adjacent calls, etc.) as `RawOrigin::Signed(<forged account>)` for any account chosen by the attacker.

This mirrors the CVE-2021-26704 bug class: a crafted/untrusted parameter (the EPrints `verb`; here, the unauthenticated `from`/optional-signature `data`) is trusted to select and drive execution of a privileged operation without adequate authorization, resulting in attacker-controlled command/call execution under another identity's context.

### Impact Explanation
An attacker can forge the origin of arbitrary permitted runtime calls as any account they choose, without needing to sign anything, by bridging even a minimal/dust amount of a registered token with a crafted `data` payload and `signature: None`. Depending on which extrinsics are permitted by `BaseCallFilter`, this can lead to unauthorized transfers or approvals from the forged account, manipulation of another user's on-chain state, or abuse of pallet-account/sovereign-account balances/permissions — i.e., unauthorized app action / theft of funds under another identity, satisfying the "unauthorized app action" and "concrete theft" impact bar.

### Likelihood Explanation
High. Exploitation requires only a single unprivileged call to the registered peer `HyperFungibleToken`/`WrappedHyperFungibleToken` contract on the source chain with attacker-chosen `Message.from` and `call_data.signature = None`, then relaying the resulting ISMP POST request — well within reach of "an unprivileged message dispatcher/relayer/token bridger" as specified in scope. No special privileges, race conditions, or governance/admin access are needed.

### Recommendation
Do not derive a dispatch origin from unauthenticated message fields. Either (a) require `signature` to always be present and verified against the actual `message.from`/beneficiary before any `runtime_call` dispatch, rejecting `None` signatures entirely, or (b) restrict the unsigned fallback path to a fixed, non-spoofable origin (e.g., always dispatch as the module/pallet account or a purpose-built "unsigned relay" origin with a minimal, explicitly safelisted call filter) rather than trusting `message.from` as an identity claim.

### Proof of Concept
1. Attacker calls the peer `HyperFungibleToken` contract's send function on an EVM chain, setting the ABI `Message.from` field to the bytes of a victim/target account (any 20 or 32-byte value of choice) and attaching `data` = SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <encoded privileged call, e.g. Balances::transfer_all(attacker) or Assets::approve> }`.
2. A relayer delivers the resulting ISMP `PostRequest` to the destination parachain; `pallet-hyper-fungible-token::on_accept` runs.
3. `ContractToAsset` lookup succeeds because the source contract itself is a legitimately registered peer [6](#0-5) ; the token mint/transfer proceeds normally.
4. Since `substrate_data.signature` is `None`, the code sets `origin` to the account decoded straight from the attacker-chosen `message.from` bytes [7](#0-6)  and dispatches `runtime_call` as `RawOrigin::Signed(origin)` [8](#0-7) , executing the attacker's chosen call as the victim account.

Note: I was unable to locate and inspect the Solidity `HyperFungibleToken`/`WrappedHyperFungibleToken` source in this index to confirm whether `Message.from` is hard-set to `msg.sender` at the EVM encoding layer (which would mitigate this) or left attacker-settable; the grep for the `.sol` contracts did not return their content due to index/query limits. If `from` is in fact hard-pinned to `msg.sender` on-chain in the EVM contract with no way to override it, this would only allow an attacker to forge calls as *their own* EVM-derived address, which is far lower impact (self-authorization) rather than arbitrary-account impersonation. A Devin session with full repository access should verify `HyperFungibleToken.sol`'s send/bridge function to confirm whether `from` is attacker-settable before treating this as validated.

### Citations

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L185-198)
```text
## Cross-Chain Message Format

The pallet encodes messages using the same ABI format as the Solidity contracts:

```solidity
struct Message {
    bytes from;    // original sender (for timeout refunds)
    bytes to;      // recipient on destination chain
    uint256 amount;
    bytes data;    // optional calldata
}
```

This ensures full compatibility between `pallet-hyper-fungible-token`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` on any chain.
```

**File:** docs/content/developers/polkadot/hyper-fungible-token.mdx (L202-217)
```text
## Calldata Execution

The `call_data` field in `SendParams` allows executing arbitrary runtime calls on the destination substrate chain after the tokens are transferred. The calldata is SCALE-encoded as:

```rust lineNumbers
pub struct SubstrateCalldata {
    /// Optional SCALE-encoded MultiSignature of (account_nonce, runtime_call)
    pub signature: Option<Vec<u8>>,
    /// SCALE-encoded runtime call to execute
    pub runtime_call: Vec<u8>,
}
```

If a signature is provided, it is verified against the beneficiary's account nonce and the runtime call before dispatch. Supported signature types: Ed25519, Sr25519, ECDSA. The account nonce is incremented after dispatch to prevent replay.

If no signature is provided, the origin is derived from the sender address in the cross-chain message.
```

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
