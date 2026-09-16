### Title
Unbounded, fee-free execution of `Ismp::handle_unsigned` batches during transaction-pool `validate_unsigned` allows CPU/memory exhaustion analogous to CVE-2015-5162 - (File: modules/pallets/ismp/src/lib.rs)

### Summary
`pallet_ismp`'s `ValidateUnsigned::validate_unsigned` runs the **full** message-execution path (`Self::execute(messages.clone())`) for every unsigned `handle_unsigned` extrinsic that reaches a node's transaction pool — before the extrinsic is included in a block and before any fee is charged. The `messages: Vec<Message>` parameter, and the `consensus_proof: Vec<u8>` / `proof: Vec<u8>` fields nested inside each `Message` variant, are plain, unbounded `Vec<u8>`/`Vec<Message>` (no `BoundedVec`, no per-message or per-proof size/count cap at the pallet level). This mirrors the OpenStack CVE-2015-5162 pattern: an unauthenticated caller supplies a crafted, oversized/adversarial input that is fed straight into expensive parsing/verification (there: `qemu-img` on an untrusted disk image; here: BEEFY/consensus and storage-proof verification) with no upfront bound, so a single free submission can force disproportionate CPU/memory consumption on every node that validates it.

### Finding Description
`pallet_ismp::Pallet::<T>::handle_unsigned` is dispatched with `ensure_none(origin)` and is deliberately fee-free so relayers can submit proofs without paying gas: [1](#0-0) 

Critically, `ValidateUnsigned::validate_unsigned` for this call does **not** perform a cheap sanity/size check before running verification — it directly calls the same `Self::execute(messages.clone())` that a full dispatch would run, and only then classifies the transaction for pool inclusion: [2](#0-1) 

`Message::Consensus(ConsensusMessage)` carries a raw, unbounded `consensus_proof: Vec<u8>`: [3](#0-2) 

For BEEFY-class consensus proofs, verification recovers an ECDSA public key and hashes for **every** signature in the submitted commitment before any cap is enforced against the (relatively cheap) participation-threshold check: [4](#0-3) 

Notably, the project already recognizes and mitigates exactly this bug class in one entry point — `pallet-beefy-consensus-proofs::submit_proof` uses a `BoundedVec<u8, MaxProofSize>` so oversized payloads are rejected at the **txpool decode stage**, before any verification work happens: [5](#0-4) 

That same bound is absent from the generic `pallet_ismp::Call::handle_unsigned { messages: Vec<Message> }` path: `Vec<Message>` has no length cap, and each `Message` variant's inner proof bytes (`consensus_proof`, request/response `Proof.proof`, etc.) are plain `Vec<u8>` with no per-call `BoundedVec` limit, so the only ceiling is the substrate node's global "maximum unsigned/pool extrinsic size" configuration — which is far larger than what a single cheap validation pass should be allowed to spend CPU/memory parsing and cryptographically verifying, especially when this happens repeatedly (every time the transaction is (re)gossiped or the pool revalidates it) and for free.

`docs/content/developers/polkadot/pallet-ismp/overview.mdx` even documents the intended safety property that "the transaction pool validation logic prevent[s] unnecessary processing and potential network congestion" — but this safety net depends on validation itself being cheap, which it is not here, since `validate_unsigned` performs the *entire* verification workload rather than a bounded structural pre-check.

### Impact Explanation
Any unprivileged party (no signature, no fee, no prior state) can submit crafted `handle_unsigned` extrinsics carrying maximal-size `Vec<Message>` batches with maximal-size/adversarial `consensus_proof`/proof byte blobs and inflated signature-set arrays. Each node in the network must run `Self::execute()` — full consensus/storage-proof verification, MMR walks, ECDSA recovery per signature, trie proof decoding — merely to *validate* the transaction for its pool, before it is even accepted or included. Because this is unsigned and free, an attacker pays no economic cost, and the same computational burden is repeated across the network on every node's mempool and on every re-broadcast/re-validation. This is a Denial-of-Service on relayer/node availability (CPU and memory exhaustion), matching the CWE-400 classification and CVSS profile of the source advisory (`AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`).

### Likelihood Explanation
High. The `handle_unsigned` extrinsic and its `validate_unsigned` implementation are the primary, publicly documented, unauthenticated ingress path for ISMP messages ("This allows users execute ISMP datagrams for free. Use with caution." — comment directly above the vulnerable code). No signature or stake is required, and the codebase's own tests/fixes for `BeefyConsensusProofs::submit_proof` and `pallet-call-decompressor` (both fixed for closely related "unbounded work before/at validation" bugs, per in-repo comments about "zstd-bomb" and oversized-claim guards) demonstrate the team is actively hardening this exact bug class elsewhere, but `pallet_ismp::handle_unsigned` itself was not shown to have an equivalent upfront bound in the reviewed code.

### Recommendation
- Bound `Vec<Message>` batch size and the byte length of every embedded proof (`consensus_proof`, `Proof.proof`) with `BoundedVec<_, MaxX>` types enforced at SCALE-decode time (the pool rejects oversized calls before `validate_unsigned` even runs), mirroring the `BoundedVec<u8, MaxProofSize>` pattern already used in `pallet-beefy-consensus-proofs::submit_proof`.
- Add a cheap structural pre-check (message count, proof length, signature-array length) inside `validate_unsigned` that runs and fails fast **before** invoking `Self::execute`, so malformed/oversized submissions are rejected without doing full verification work.
- Cap the number of BEEFY signatures processed per consensus update to the minimum needed for the supermajority check, rejecting the transaction early if the array is implausibly large.

### Proof of Concept
1. Construct a `pallet_ismp::Call::handle_unsigned` extrinsic with `messages: Vec<Message>` containing the pool's maximum allowed number of `Message::Consensus` entries.
2. For each, set `consensus_proof` to a maximal-size byte blob (or a BEEFY commitment with a very large `signatures` array) that is syntactically decodable but will ultimately fail final signature/threshold checks.
3. Submit as an unsigned extrinsic (no fee, no signer) to a node's RPC.
4. Observe that `validate_unsigned` calls `Self::execute(messages.clone())`, which fully parses and attempts to cryptographically verify every proof/signature in the batch, consuming disproportionate CPU/memory, before ultimately rejecting the transaction — repeatable at zero cost per attempt and amplified across every node that (re)validates the gossiped transaction.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
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

**File:** modules/ismp/core/src/messaging.rs (L41-48)
```rust
pub struct ConsensusMessage {
	/// Scale Encoded Consensus Proof
	pub consensus_proof: Vec<u8>,
	/// The consensus state Id
	pub consensus_state_id: ConsensusStateId,
	/// Public key of the sender
	pub signer: Vec<u8>,
}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L146-162)
```rust
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}
```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L355-366)
```rust
	// 6. submit_proof oversized payload — `proof: BoundedVec<u8, MaxProofSize>` rejects at the
	//    txpool decode stage, before dispatch. We send `MaxProofSize + 1` bytes prefixed with
	//    `PROOF_TYPE_NAIVE`.
	let mut oversized_proof = vec![PROOF_TYPE_NAIVE; MAX_PROOF_SIZE + 1];
	oversized_proof[0] = PROOF_TYPE_NAIVE;
	let call = subxt::dynamic::tx(
		"BeefyConsensusProofs",
		"submit_proof",
		vec![Value::from_bytes(&oversized_proof)],
	);
	let result = submit_signed(&client, &rpc_client, call, Keyring::Bob).await;
	assert!(result.is_err(), "oversized submit_proof must be rejected by the BoundedVec decode",);
```
