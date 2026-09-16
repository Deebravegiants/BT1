### Title
Unbounded, unmetered state-proof verification in `pallet-coprocessor::handle_unsigned` — CPU/memory exhaustion via a fixed-weight unsigned extrinsic - ([File: modules/pallets/state-coprocessor/src/impls.rs])

### Summary
`pallet-coprocessor`'s `handle_get_requests` performs full membership and state-proof verification (trie decoding, RLP parsing, storage-trie rebuilding per contract) for every `GetRequest` and every key inside it in a single `GetRequestsWithProof` message, with no upper bound on `requests.len()` or `req.keys.len()`. The per-app bandwidth allowance check (`BandwidthGate::try_consume`) — the only cost control — is applied *after* this expensive verification work is done, not before it. Worse, this function is invoked directly from `validate_unsigned` on every unsigned extrinsic submission/gossip, under a fixed, size-independent extrinsic weight (`DbWeight::get().reads_writes(1, 2)`), so the runtime's weight accounting does not scale with the attacker-controlled amount of verification work performed.

### Finding Description
`handle_get_requests` in <cite repo="AYontt/hyperbridge--003" path="modules/pallets/state-coprocessor/src/impls.rs" start="62,133" end="64,155" /> loops over an unbounded `requests: Vec<GetRequest>` (itself declared with no `BoundedVec`/`MaxEncodedLen` cap in `GetRequestsWithProof`, [1](#0-0) ) and, for each request, calls `dest_state_machine.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)`, where `req.keys: Vec<Vec<u8>>` is likewise unbounded (`modules/ismp/core/src/router.rs:128`). This verification is the expensive path: for EVM/Substrate-EVM state machines it decodes an attacker-supplied proof blob, clones per-contract proofs, rebuilds Merkle-Patricia/child tries and RLP-decodes accounts for every key (`modules/ismp/state-machines/evm/src/lib.rs:149-261`, `modules/ismp/state-machines/evm/src/substrate_evm.rs:182-248`).

Only *after* `verify_state_proof` returns does the code call `BandwidthGate::try_consume` to check whether the app (`req.source`, `req.from`) is even allowed this much data (`modules/pallets/state-coprocessor/src/impls.rs:142-151`, documented explicitly at `modules/pallets/state-coprocessor/src/lib.rs:60-64`: "Charged after proof verification so the value sizes are final"). This mirrors the Grav pattern precisely: the resource-intensive operation (image buffer allocation / trie verification) runs unconditionally before the bound/quota check (`max_dimension` / bandwidth allowance) that is supposed to gate it.

This code path is reachable without any signed transaction or fee: `handle_unsigned` is a `#[pallet::call_index(0)]` extrinsic that only requires `ensure_none(origin)` (no signer, no fee) at `modules/pallets/state-coprocessor/src/lib.rs:92-104`, and the *same* unbounded verification (`Self::handle_get_requests(message.clone())`) is executed again inside `validate_unsigned` (`modules/pallets/state-coprocessor/src/lib.rs:121-129`) — meaning every node that receives the gossiped unsigned transaction independently performs the full, unbounded verification work during mempool validation, before the transaction is even included in a block. The extrinsic's declared weight is a constant `DbWeight::get().reads_writes(1, 2)` (`modules/pallets/state-coprocessor/src/lib.rs:91`), completely decoupled from the number of requests/keys and the actual trie-verification cost incurred.

### Impact Explanation
An unauthenticated party (no signature, no relayer fee, no bandwidth allowance) can submit a single `handle_unsigned` message containing many `GetRequest`s, each with many storage keys, each key length crafted to force full trie reconstruction and RLP account decoding. Every node in the network that validates this unsigned transaction (mempool gossip re-validation) performs the same expensive verification, and the weight charged to the chain if included is fixed and far below the true cost — a direct network-wide CPU/consensus-availability DoS, matching the CWE-770 class of the reference report (unbounded, unmetered resource consumption gating check placed after the expensive work rather than before it). This can degrade or halt block production/relaying for the coprocessor’s state-proof-driven GET flow, which is a route used to deliver messages; a sustained attack is a "route unable to deliver messages" condition.

### Likelihood Explanation
High: `handle_unsigned` requires no signer and no fee, and `validate_unsigned` unconditionally re-executes `handle_get_requests` — meaning malicious traffic doesn't even need to be included in a block to cost CPU across the network. No special privileges, governance, or existing bandwidth allowance are required to trigger the expensive path since the check happens only after the work is done.

### Recommendation
Move the bandwidth/size gate before any proof verification: bound `requests.len()` and `req.keys.len()` (or a combined declared-size claim) with an explicit ceiling (e.g., via `BoundedVec` or an explicit `ensure!` check against `MaxKeys`/`MaxRequests`), and call `BandwidthGate::try_consume` using the *claimed* request/key sizes (mirroring the `encoded_call_size` pre-check pattern already used in `pallet-call-decompressor::decompress`, [2](#0-1) ) prior to calling `verify_membership`/`verify_state_proof`. Additionally, make the `handle_unsigned` extrinsic's declared weight proportional to `requests.len()` and total key bytes, so the runtime's weight accounting reflects the true cost, and reject unsigned transactions whose claimed cost exceeds `MaxCallSize`-like limits during `validate_unsigned` without doing the verification work itself.

### Proof of Concept
1. Craft a `GetRequestsWithProof` with a large `requests` vector (e.g., thousands of `GetRequest`s), each containing many 52-byte EVM storage keys (`req.keys`), targeting many distinct contract addresses to maximize the number of tries/RLP decodes performed by `verify_state_proof`.
2. Submit this as an unsigned `Call::handle_unsigned { message }` extrinsic — no signature, no fee required (`ensure_none(origin)` at `modules/pallets/state-coprocessor/src/lib.rs:96`).
3. Every peer node's `validate_unsigned` (`modules/pallets/state-coprocessor/src/lib.rs:121-129`) calls `handle_get_requests(message.clone())`, which runs `verify_membership` and, for every request, `verify_state_proof` — performing full trie reconstruction/RLP decoding for each key/contract before the `BandwidthGate::try_consume` check at `impls.rs:146-151` is ever reached.
4. Because the declared extrinsic weight is the fixed `DbWeight::get().reads_writes(1, 2)` regardless of the actual `requests`/`keys` size, this cost is essentially "free" from the runtime's perspective while consuming disproportionate CPU/memory on every validating node, repeated on every re-gossip/re-validation cycle.

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L46-55)
```rust
pub struct GetRequestsWithProof {
	/// The associated Get requests
	pub requests: Vec<GetRequest>,
	/// Proof of these requests on the source chain
	pub source: Proof,
	/// State proof of the requested values in the Get requests.
	pub response: Proof,
	/// Address that should be credited with fees
	pub address: Vec<u8>,
}
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L220-231)
```rust
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);
```
