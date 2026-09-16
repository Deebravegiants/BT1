Confirmed: `message.from = abi.encodePacked(msg.sender)` is set honestly by the EVM `HyperFungibleToken.sol` sender, so a sending contract cannot forge an arbitrary `from`. However, the Rust-side `hyper-fungible-token` pallet (`modules/pallets/hyper-fungible-token/src/module.rs`) accepts messages from **any registered token-gateway contract**, and each contract independently controls what `Message.from`/`data` it puts in the body it sends. Not every peer implementation is `HyperFungibleToken.sol` — the interface only requires an ABI-compatible `Message{from,to,amount,data}`, so any owner-registered peer contract (or a Substrate-side pallet peer) can freely choose the `from` field it emits.

### Title
Unsigned cross-chain calldata execution lets any registered token-gateway peer dispatch arbitrary runtime calls as an attacker-chosen account - (File: `modules/pallets/hyper-fungible-token/src/module.rs`)

### Summary
`Pallet::on_accept` in the hyper-fungible-token ISMP module decodes an ABI `Message` from an authenticated peer contract and, if `message.data` is non-empty and carries no valid signature, derives a dispatch `origin` purely from the attacker-supplied `message.from` field and dispatches an arbitrary `T::RuntimeCall` as that origin — with no proof that the real owner of that account authorized the call.

### Finding Description
In `on_accept` [1](#0-0) , when `substrate_data.signature` is `None`, the code takes `message.from` — a byte string chosen entirely by whichever ISMP module (EVM contract or Substrate pallet) is registered as this asset's counterparty on the source chain — converts it to an `AccountId` and immediately dispatches the attacker-controlled `runtime_call` with `RawOrigin::Signed(origin)`: [2](#0-1) 

The only gate on the request itself is `ContractToAsset::<T>::get(source, &from)` at the top of the function, which authenticates that the *request* came from the registered peer contract address — it says nothing about the *body* the peer contract chooses to send. On the reference EVM implementation, `from` inside `Message` is honestly set to `abi.encodePacked(msg.sender)` [3](#0-2) , but that is a property of one specific peer contract, not of the ISMP module interface or the pallet's trust model. The pallet only requires the request to originate from the address stored in `ContractToAsset`; it never verifies that the `from` field embedded in the body is cryptographically tied to a real signer, nor that it matches any escrowed/burn accounting on the source side. Any owner-registered peer (a custom EVM gateway, an upgraded gateway, or a Substrate-side peer pallet) can freely populate `message.from` with an arbitrary 20/32-byte value and `message.data` with an arbitrary encoded `RuntimeCall`, causing this pallet to dispatch that call as `RawOrigin::Signed(<attacker-chosen account>)`. The only remaining check is `BaseCallFilter`, which filters call *types*, not origins — it does not prevent, e.g., `Balances::transfer_all` or governance-adjacent calls filtered only by origin checks elsewhere from being executed as any account the message names.

This mirrors the GHSA-2x54-j4m3-r6wx bug class: a value that is supposed to be inert "data" (the YAML fixture text / here, the cross-chain calldata) is instead trusted enough to drive execution (`eval`-like `runtime_call.dispatch`) under an identity (`origin`) that the executor does not actually control or verify, based solely on an untrusted embedded byte string.

### Impact Explanation
A malicious/compromised/misconfigured peer contract that the pallet owner has registered via `addChain`/`ContractToAsset` can execute arbitrary filtered dispatchables as any Substrate account on the destination chain simply by naming that account's bytes in `message.from` and supplying `data` with no signature. This allows unauthorized privileged actions (e.g., moving another user's `Assets`/`Balances`, calling other pallets that accept `Signed` origin) without that user's consent — a direct "unauthorized app action" / fund-theft path once combined with any dispatchable that moves value from the named origin.

### Likelihood Explanation
Requires the destination pallet's owner to have added a peer whose gateway logic is attacker-influenced or which the pallet author trusted only for token minting semantics, not for the identity it stamps into optional calldata's implicit origin. Given the module interface explicitly supports "transfer-and-call" composability with peers across chains/VMs (EVM and Substrate), and the trust boundary (`ContractToAsset`) authenticates only the sender contract, not the semantic honesty of the `from` field it emits, this is a realistic, low-effort path for any party that operates or compromises a registered peer contract.

### Recommendation
Remove the no-signature branch, or require that unsigned calldata always dispatch with an origin derived deterministically and unforgeably from the request's ISMP-verified `from`/`source` (e.g., a dedicated cross-chain-derived account distinct from any real user's local account, as is done elsewhere for EVM-to-Substrate address mapping), never trusting `message.from` to select an arbitrary existing local account without a valid signature proving ownership.

### Proof of Concept
1. Pallet owner registers a peer gateway (EVM or Substrate) for asset `X` via `ContractToAsset`.
2. That peer's gateway (attacker-controlled, buggy, or upgraded without the same invariants as `HyperFungibleToken.sol`) sends a POST whose ABI-encoded `Message` sets `to = attacker`, `amount = 0` (or non-zero), `from = <victim account bytes>`, and `data = SubstrateCalldata { signature: None, runtime_call: <encoded call moving victim's funds/pallet-X call> }`.
3. `on_accept` mints/transfers per `to`/`amount`, then decodes `substrate_data`, takes the `else` branch since `signature` is `None`, sets `origin = victim` from `message.from`, and dispatches `runtime_call` as `RawOrigin::Signed(victim)` — executing an action as the victim with no signature from the victim ever verified. [2](#0-1)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-203)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;

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
					MultiSignature::Ecdsa(sig) => {
						let payload = (nonce, substrate_data.runtime_call.clone()).encode();
						let preimage = vec![
							format!("{ETHEREUM_MESSAGE_PREFIX}{}", payload.len())
								.as_bytes()
								.to_vec(),
							payload,
						]
						.concat();
						let msg = sp_io::hashing::keccak_256(&preimage);
						let pub_key = sp_io::crypto::secp256k1_ecdsa_recover(&sig.0, &msg)
							.map_err(|_| HftError::EcdsaRecoveryFailed)?;
						let eth_address =
							H160::from_slice(&sp_io::hashing::keccak_256(&pub_key[..])[12..]);
						let substrate_account = T::EvmToSubstrate::convert(eth_address);
						if substrate_account != beneficiary {
							Err(HftError::SignatureVerificationFailed)?
						}
					},
					MultiSignature::Eth(_) => Err(HftError::EthSignatureUnsupported)?,
				};

				beneficiary.clone()
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L237-256)
```text
    function _buildDispatchPost(SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```
