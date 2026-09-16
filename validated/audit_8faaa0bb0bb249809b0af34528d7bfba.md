Found a concrete panic condition reachable from an unprivileged relayer delivering a cross-chain PostRequest through `pallet-hyper-fungible-token`'s `on_accept`.

### Title
Denial-of-service via out-of-bounds slice indexing on attacker-controlled `message.from`/`message.data` in HFT's `on_accept` calldata path - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`Pallet::on_accept` (the `IsmpModule` handler invoked when a relayer delivers a POST request to the hyper-fungible-token bridge) ABI-decodes an attacker-controlled `message` and then, when `message.data` carries a `SubstrateCalldata` payload without a signature, derives the dispatch origin from `message.from` using unchecked slicing and `copy_from_slice`, exactly analogous to CVE-2017-6010's unchecked buffer indexing on corrupted/attacker-supplied input.

### Finding Description
In `on_accept`, when `message.data` is non-empty and `substrate_data.signature` is `None`, the code computes the dispatch origin directly from `message.from`: [1](#0-0) 

Two issues exist here, both mirroring the "corrupted input drives unchecked buffer access" bug class from the CVE:

1. `&from_bytes[from_bytes.len() - 20..]` — if `source.is_evm()` is true but `from_bytes.len() < 20` (an attacker on an EVM source chain can set `message.from` to an arbitrary-length ABI `bytes` value, e.g. empty or 5 bytes), `from_bytes.len() - 20` underflows in `usize` arithmetic, causing a panic (in debug: subtract-with-overflow panic; in release with overflow-checks enabled in this security-sensitive runtime path, likewise a panic/trap).
2. `account.copy_from_slice(from_bytes)` — if `source` is not EVM but `from_bytes.len() != 32`, `copy_from_slice` panics on a length mismatch. This is the same "fixed-size buffer written from adversarial-length input without a length check" defect that the codebase itself has patched in numerous other locations (see the `as_utf8_string`, `StateMachine::from_str`, and `to_bytes_32` fixes below), but this specific call site remains unguarded.

By contrast, the same file's `on_accept` earlier and `on_timeout` code paths for `message.to`/`message.from` correctly validate the byte length before use: [2](#0-1) [3](#0-2) 

This shows the length-check pattern is known and used elsewhere in the same file, but was missed at line 177-186. The codebase has a demonstrated, repeated history of exactly this bug class being found and fixed as "untrusted input drives unchecked fixed-size buffer/index access, panicking the node," e.g.: [4](#0-3) [5](#0-4) [6](#0-5) 

### Impact Explanation
`on_accept` runs as part of dispatched-message execution in `pallet-ismp`'s message-handling path, triggered by any relayer delivering a valid state/membership proof for a POST request destined for the HFT module. Since the panic happens after successful ABI decoding and successful minting/transfer of funds (the mint/transfer call at lines 94-117 executes before the vulnerable code at 176-187), a transaction that reaches this branch will trap mid-execution. In a Substrate runtime, an uncaught panic inside dispatch aborts the extrinsic/executive and can, depending on how the panic manifests (wasm trap vs. graceful `Result`), disrupt block execution for the message-processing extrinsic, effectively giving any user who can source a legitimate cross-chain PostRequest (or forge one that reaches this decode point) a way to make honest relayers' `handle_unsigned`/message-execution calls fail deterministically for that message, causing message-delivery denial-of-service for the destination chain's fungible-token bridge. This matches the "route unable to deliver messages" acceptance criterion.

### Likelihood Explanation
Reaching the vulnerable code requires: (1) a registered source contract mapped via `ContractToAsset`, (2) a `message.data` payload that ABI/SCALE-decodes into a valid `SubstrateCalldata` with `signature = None`, and (3) `message.from` set to a length other than 20 (EVM source) or other than 32 (non-EVM source). All of these fields are attacker/relayer-controlled at the source-chain contract or via a permissioned mint/burn path that ultimately becomes a POST request body — the attacker needs no privileged role, only the ability to originate a bridge transfer with custom calldata from a source chain contract already registered as a valid asset-issuing contract. This makes the trigger conditions realistic for any user of the token bridge.

### Recommendation
Add explicit length checks before both the EVM slicing (`from_bytes.len() >= 20`) and the non-EVM `copy_from_slice` (`from_bytes.len() == 32`) in the `on_accept` calldata-origin-derivation branch, returning a typed `HftError` (e.g. `InvalidFromLength`) instead of panicking, matching the pattern already used for `message.to` earlier in the same function and for `message.from` in `on_timeout`.

### Proof of Concept
1. Register a source EVM contract in `ContractToAsset` for some `local_asset_id`.
2. From that contract, submit a POST request whose ABI-encoded `Message` body has: `to` = a valid 20/32-byte recipient, `amount` = any nonzero value, `data` = SCALE-encoded `SubstrateCalldata { signature: None, runtime_call: <any allowed call> }`, and `from` set to an ABI `bytes` value of length 0 (or any length ≠ 20).
3. Relay this POST request to the destination chain running `pallet-hyper-fungible-token`; when `on_accept` executes, `from_bytes.len() - 20` underflows because `source.is_evm()` is true and `from_bytes.len() == 0`, triggering a panic/trap during message dispatch. [1](#0-0)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L61-71)
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L223-230)
```rust
				// Refund the original sender
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
```

**File:** modules/utils/serde/src/lib.rs (L529-532)
```rust
	// `as_utf8_string` deserializes into a fixed `[u8; 4]`. It used to `copy_from_slice`
	// straight from the input, which panics on any length mismatch — and it runs on
	// untrusted RPC input (`consensus_state_id`), so the panic aborted the node's `rpc`
	// worker thread and took the process down. Wrong lengths must be serde errors.
```

**File:** modules/ismp/core/src/host.rs (L470-474)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L118-128)
```rust
pub(super) fn to_bytes_32(bytes: &[u8]) -> Result<[u8; 32], Error> {
	if bytes.len() != 32 {
		return Err(EvmStateMachineError::BadByteLength(bytes.len()).into());
	}

	let mut array = [0u8; 32];

	array.copy_from_slice(&bytes);

	Ok(array)
}
```
