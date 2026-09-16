### Title
Unguarded `copy_from_slice` on attacker-influenced `message.from` panics the runtime during ISMP message dispatch - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`HyperFungibleToken::on_accept` (the `IsmpModule` callback invoked by `pallet-ismp` when delivering a verified `PostRequest`) contains a length-checked path for the `to` recipient but an **unchecked** path for the `from` sender when executing optional calldata. When the request originates from a non-EVM source and carries no signature, the code does `account.copy_from_slice(from_bytes)` into a fixed `[0u8; 32]` buffer without first validating `from_bytes.len() == 32`, unlike every other analogous conversion in this file.

### Finding Description
In `on_accept`: [1](#0-0) 
the `to` (recipient) bytes are explicitly length-checked and rejected with `HftError::InvalidRecipientLength` if not 20 or 32 bytes.

The equivalent conversion for the timeout path is likewise guarded: [2](#0-1) 

However, inside the optional-calldata branch of `on_accept`, when there is no signature and the source state machine is not EVM, the `from` bytes taken from the ABI-decoded `Message` are copied unguarded: [3](#0-2) 

`account.copy_from_slice(from_bytes)` traps (panics) in the Rust standard library whenever the source slice length does not equal the destination array length (32). `message.from` originates from `Message::abi_decode(&body)` — application-layer bytes inside the ISMP request body, not the outer authenticated ISMP `from`/`source` fields: [4](#0-3) 

This mirrors the exact bug class described in the CVE (malformed/oversized input to a length-sensitive field causing an application/process crash), and matches a pattern the codebase has explicitly hardened against elsewhere — e.g. `StateMachine::from_str`, `as_utf8_string`, `ByteVector<N>::decode`, the RLP node codec, and the sync-committee/BEEFY multi-proof length checks all carry comments and regression tests stating that "this runs on untrusted input and must not panic": [5](#0-4) [6](#0-5) 

The `on_accept` path here was missed in that hardening pass.

### Impact Explanation
A panic raised inside `on_accept` during dispatch of a delivered ISMP `PostRequest` aborts the dispatchable that is executing message handling (`pallet_ismp::Call::handle_unsigned` / the underlying request-handling extrinsic). Depending on execution context this either aborts the transaction (denial of service for that specific message/application) or, if triggered inside offchain/unsigned validation logic that is not panic-safe, can disrupt the node's transaction-validation worker — consistent with the CVE's "denial of service ... crash the application" impact. In Hyperbridge terms this is a route that becomes unable to deliver messages for the affected HFT application instance until the code is patched, which the validation criteria explicitly accept as in-scope impact.

### Likelihood Explanation
Reachability requires: (1) the destination chain having a `ContractToAsset` mapping for a non-EVM `source` state machine and its `from` contract identifier, (2) a `PostRequest` delivered to that mapping with non-empty `message.data` and no `signature` in the decoded `SubstrateCalldata`, and (3) `message.from` (an application-layer field controlled by whatever logic constructs the outgoing message on the source chain) not being exactly 32 bytes. I was not able to fully verify, within the available index, whether the paired sender-side pallet on the source chain always encodes `from` as exactly 32 bytes or whether an attacker able to influence that sender's construction of the message body could supply an arbitrary length. This uncertainty affects the exploitability assessment — the unguarded operation itself is a confirmed code defect and inconsistent with the length-checked siblings in the same file, but full end-to-end attacker control of `message.from`'s length was not independently confirmed from the code retrieved.

### Recommendation
Add the same length validation used for `to_bytes` and the `on_timeout` `sender_bytes` conversion before the unguarded copy:
```rust
} else {
    let mut account = [0u8; 32];
    if from_bytes.len() != 32 {
        Err(HftError::InvalidSenderLength(from_bytes.len()))?
    }
    account.copy_from_slice(from_bytes);
    account.into()
}
```
Additionally, audit the file for any other unguarded fixed-size `copy_from_slice`/`try_into().unwrap()` conversions on ABI-decoded, cross-chain-message-supplied bytes.

### Proof of Concept
1. Register a `ContractToAsset` mapping for `(source = <non-EVM StateMachine>, from = <attacker-influenced contract id>)`.
2. Construct/deliver a `PostRequest` whose ABI-encoded body decodes to a `Message` with non-empty `data`, `SubstrateCalldata.signature = None`, and `message.from` of a length other than 32 bytes (e.g., 19 or 33 bytes).
3. Have a relayer submit the request with a valid proof through the normal `pallet_ismp` handling path so `HyperFungibleToken::on_accept` executes.
4. Execution reaches `account.copy_from_slice(from_bytes)` with mismatched lengths, panicking and aborting the dispatch — reproducing the CVE's "malformed input causes crash" pattern inside message dispatch rather than a GUI text field.

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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L224-232)
```rust
				let from_bytes = message.from.as_ref();
				let mut sender_bytes = [0u8; 32];
				if from_bytes.len() == 32 {
					sender_bytes.copy_from_slice(from_bytes);
				} else if from_bytes.len() == 20 {
					sender_bytes[12..].copy_from_slice(from_bytes);
				} else {
					Err(HftError::InvalidSenderLength(from_bytes.len()))?
				}
```

**File:** modules/ismp/core/src/host.rs (L470-474)
```rust
	// A malformed `SUBSTRATE-`/`TNDRMINT-` id whose byte length is not exactly 4
	// must return an error rather than panic. The id is copied into a `[u8; 4]`,
	// and `copy_from_slice` traps on a length mismatch — in the runtime this is a
	// wasm trap reachable from untrusted input (e.g. `BandwidthManager.purchase`),
	// so the length is now checked up-front (matching the `RELAY-` arm).
```

**File:** modules/utils/serde/src/lib.rs (L118-136)
```rust
	/// Deserialize a string into utf8 bytes
	///
	/// The string must be exactly 4 bytes long (bytes, not chars — a 4-char string of
	/// multi-byte codepoints is rejected). Anything else is a deserialization error; this
	/// runs on untrusted RPC input, so it must never panic.
	pub fn deserialize<'de, D, T>(deserializer: D) -> Result<T, D::Error>
	where
		D: serde::Deserializer<'de>,
		T: From<[u8; 4]>,
	{
		let s = <String>::deserialize(deserializer)?;

		// `s.len()` is the utf-8 byte length, which is what the `[u8; 4]` needs to match.
		let bytes: [u8; 4] = s
			.as_bytes()
			.try_into()
			.map_err(|_| serde::de::Error::invalid_length(s.len(), &"a 4-byte utf-8 string"))?;
		Ok(bytes.into())
	}
```
