### Title
Panic-Induced DoS via Unvalidated `message.from` Length in HyperFungibleToken `on_accept` - ([File: modules/pallets/hyper-fungible-token/src/module.rs])

### Summary
`pallet_hyper_fungible_token::Pallet::on_accept` decodes an attacker-controlled ABI `Message.from` field and slices it with `from_bytes[from_bytes.len() - 20..]` without first validating its length, unlike the symmetric refund path (`on_timeout`) which explicitly checks the length and returns a typed error. A `from` field shorter than 20 bytes triggers a `usize` subtraction underflow / out-of-bounds slice panic inside message execution reachable from a permissionless, unsigned `pallet_ismp::handle_unsigned` extrinsic — mirroring the HAX CMS pattern where an unchecked field dereference on attacker-supplied data crashes request handling before any output is produced.

### Finding Description
`on_accept` is invoked for every incoming `PostRequest` routed to the HyperFungibleToken pallet via the `ProxyModule` router (`parachain/runtimes/*/src/ismp.rs`), which itself is called from `pallet_ismp::Pallet::execute` / `handle_unsigned` — an unsigned, permissionless, fee-free extrinsic path documented as reachable by "anyone" with a valid proof: [1](#0-0) [2](#0-1) 

Inside `on_accept`, the attacker-controlled `message` is ABI-decoded from the request body: [3](#0-2) 

The recipient field (`message.to`) is explicitly length-checked before use: [4](#0-3) 

But when the optional-calldata branch executes (`message.data` non-empty and no `substrate_data.signature`), the sender field (`message.from`) is used **without any length validation** before being sliced: [5](#0-4) 

`from_bytes.len() - 20` underflows if the attacker supplies `message.from` shorter than 20 bytes (e.g., empty bytes), and the subsequent slice `from_bytes[from_bytes.len() - 20..]` panics. This is a direct structural analog of the reported bug: `tmpFile.originalname.replace(...)` dereferences an unchecked/attacker-influenced field without validation, crashing request handling. The pallet's own `on_timeout` handler for the *same* field demonstrates the fix is already known and applied elsewhere but omitted here: [6](#0-5) 

### Impact Explanation
A single crafted cross-chain `PostRequest` (attacker fully controls `message.from`, `message.data`, and `source` via the ABI-encoded body) submitted through the permissionless `handle_unsigned` unsigned extrinsic can panic the runtime during extrinsic execution/`ValidateUnsigned::validate_unsigned` at the transaction-pool layer. `validate_unsigned` runs `Self::execute(messages.clone())` directly at the mempool validation stage before a block is even produced: [7](#0-6) 

Because unsigned transactions are gossiped and validated by every peer, a single malicious message can be propagated network-wide and trigger the same panic on every full node that validates it, which is a Denial-of-Service on the collator/validator set analogous to the HAX CMS "single request takes the whole process offline" scenario. This satisfies the "route unable to deliver messages" / no-impact-analog exclusion boundary by producing a genuine service outage rather than a mere contained revert (contrast with the EVM-side `body[0]` index patterns in `IntentGatewayV2.onAccept`/`HostManager.onAccept`, which are caught by `EvmHost.dispatchIncoming`'s try/catch and do not crash the host).

### Likelihood Explanation
High reachability: the path requires only a standard cross-chain `PostRequest` targeting the HyperFungibleToken pallet ID with an ABI-encoded `Message` whose `from` field is shorter than 20 bytes, `data` non-empty, and no `substrate_data.signature` — all attacker-controlled fields with no prerequisite privilege, matching the "unprivileged message dispatcher/relayer" reachable-path criteria in scope.

### Recommendation
Add the same explicit length validation used in `on_timeout` (accepting only 20 or 32-byte values and returning a typed `HftError`, e.g., `InvalidSenderLength`) to the `message.from` usage inside `on_accept`'s optional-calldata branch before any slicing/subtraction is performed.

### Proof of Concept
1. On a source EVM chain, dispatch a `PostRequest` to the HyperFungibleToken pallet's module ID with body ABI-encoding a `Message` where:
   - `to` is a valid 20/32-byte recipient (to pass the earlier check),
   - `amount` is any valid value,
   - `data` is a non-empty `SubstrateCalldata` with `signature = None` and any `runtime_call`,
   - `from` is set to `0x` (empty bytes) or any length < 20 bytes.
2. Relay this request through `pallet_ismp::handle_unsigned` (unsigned, feeless, permissionless) with a valid proof, or let it be gossiped as an unsigned transaction for `validate_unsigned` to process directly.
3. Execution reaches `modules/pallets/hyper-fungible-token/src/module.rs:177-181`, computing `from_bytes.len() - 20` which underflows, causing the slice operation to panic during message handling/validation, matching the report's crash-before-completion pattern.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L406-422)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_accept(request),

			#[cfg(not(feature = "no-bandwidth"))]
			id if id == ModuleId::Pallet(pallet_bandwidth::pallet::PALLET_BANDWIDTH) =>
				pallet_bandwidth::Pallet::<Runtime>::default().on_accept(request),

			pallet_hyper_fungible_token::PALLET_ID =>
				pallet_hyper_fungible_token::Pallet::<Runtime>::default().on_accept(request),

			_ => Err(anyhow!("Destination module not found")),
		}
	}
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L58-59)
```rust
		// Decode the Message
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L62-71)
```rust
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

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L223-232)
```rust
				// Refund the original sender
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
