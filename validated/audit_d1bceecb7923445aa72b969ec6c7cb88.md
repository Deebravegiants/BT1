### Title
Missing Hyperbridge instance/chain identifier in `beneficiary_message` allows signed fee-redirect replay across separate Hyperbridge deployments - (File: modules/pallets/relayer/src/accumulate.rs)

### Summary
`pallet-relayer`'s `beneficiary_message()` builds the signed payload that authorizes redirecting a relayer's accrued fees to a `beneficiary_address`, hashing only `(nonce, state_machine, beneficiary)`. Like the Opera-Bridge `_verifySignatures()` bug, this hash has no binding to the identity of the verifying chain/pallet instance (no genesis hash, no host `StateMachine`/instance id), relying solely on an externally-facing `state_machine` (the *destination* chain being proven against) and a locally-scoped `nonce` counter for replay protection.

### Finding Description
`beneficiary_message` is defined as: [1](#0-0) 

It is used in `accumulate()` to authorize a beneficiary redirect: [2](#0-1) 

The message is `keccak256(nonce, state_machine, beneficiary)`, where:
- `state_machine` is the identifier of the **external** chain being proven against (e.g. `EVM-1`), not the Hyperbridge instance itself.
- `nonce` is `Nonce::<T>::get(&delivery_address, state_machine)` — a counter scoped only to `(delivery_address, state_machine)` **within this one pallet instance**.

Nothing in the hash commits to which Hyperbridge deployment (parachain/relay chain, genesis hash, or runtime instance) the signature is valid for. Because `pallet-relayer` is a generic, reusable pallet in the `modules/pallets` workspace, it can be (and per the repo's structure is designed to be) instantiated on more than one chain. If the same relayer key delivers messages destined for the same external `state_machine` on two independent Hyperbridge instances, the `(delivery_address, state_machine)` nonce counters advance independently and can coincide (e.g., both at `nonce = 0` for a freshly active relayer on that route). A signature published on-chain for instance A (visible in the extrinsic calldata) is then valid, byte-for-byte, as the signed payload for instance B once B's nonce reaches the same value — exactly the "signature replayable in different bridge contracts" scenario described in the report, generalized to a Substrate pallet replayed across separate runtime instances rather than an EVM contract replayed across chains.

This mirrors the exact fix pattern the report recommends for `Opera-Bridge`: add `block.chainid`/`address(this)`-equivalent domain separation (e.g., the Hyperbridge instance's own `StateMachine`/genesis hash) to the signed struct, which `beneficiary_message` omits.

### Impact Explanation
A successfully replayed `beneficiary_message` signature lets an unprivileged third party resubmit the captured extrinsic on the other Hyperbridge instance via `accumulate()`, silently redirecting that relayer's accrued fees on the second instance to whatever `beneficiary_address` was chosen in the first instance's authorization — an outcome the relayer never signed for that specific chain. This is a violation of the signature's intended scope (fund redirection performed without a valid per-instance authorization), matching the "Medium" bug class in the reference report: replayable signatures due to missing domain separation in the message hash.

### Likelihood Explanation
Exploitation requires: (1) `pallet-relayer` (or an identical build of it) running as more than one independent instance/network, (2) a relayer active with the same key on the same external destination `state_machine` on both instances, and (3) the two instances' independent nonce counters coinciding for that `(delivery_address, state_machine)` pair. This is a real but non-trivial precondition (lower likelihood than the original EVM report, where every EVM contract redeployment/fork immediately reproduces the exact same signature space); it is plausible given the pallet's design for reuse and multi-network deployment, and requires no privileged access to trigger once the precondition holds — merely resubmitting already-public calldata.

### Recommendation
Bind `beneficiary_message` (and, for consistency, `outbound_request_delivery_message`) to the specific Hyperbridge instance, e.g. by hashing in `frame_system::Pallet::<T>::block_hash(0)` (genesis hash) or `host.host_state_machine()` (the *own* chain identifier, not just the destination), analogous to adding `block.chainid`/`address(this)` in the EVM fix. This ensures a signature produced for one Hyperbridge deployment cannot verify against another.

### Proof of Concept
1. Deploy `pallet-relayer` on two Hyperbridge instances, A and B, both configured to relay to `EVM-1`.
2. Relayer key `R` delivers messages to `EVM-1` on both A and B; suppose `Nonce::<T>::get(R, EVM-1) == 0` on both (first redirect for that route on each).
3. On instance A, `R` signs `beneficiary_message(0, EVM-1, X)` and submits `accumulate()` with `beneficiary_details = (R, sig)`, redirecting A's fees to `X`. The signature `sig` is now public in A's block.
4. An unprivileged third party observes `sig`, constructs an `accumulate()` call on instance B (with a valid delivery proof so `delivery_address == R` and `Nonce::<T>::get(R, EVM-1) == 0` there too), and submits `(R, sig)` as `beneficiary_details`.
5. `beneficiary_message(0, EVM-1, X)` on B hashes identically to the value signed on A; `Signature::Evm.verify` recovers `R`, matching `delivery_address`, so B accepts the redirect and reassigns `R`'s fees on B to `X` — an authorization `R` never issued for chain B. [3](#0-2)

### Citations

**File:** modules/pallets/relayer/src/accumulate.rs (L106-126)
```rust
		// Let's verify the beneficiary address
		let beneficiary_address = if let Some((beneficiary_address, signature)) =
			withdrawal_proof.beneficiary_details
		{
			let nonce = Nonce::<T>::get(&delivery_address, state_machine);
			let msg = beneficiary_message(nonce, state_machine, &beneficiary_address);
			match &signature {
				Signature::Evm { .. } => {
					let eth_address =
						signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
					if eth_address != delivery_address {
						Err(Error::<T>::InvalidPublicKey)?
					}
				},
				Signature::Sr25519 { .. } | Signature::Ed25519 { .. } => {
					// verify the signature with the delivery address from the state proof
					let _ = signature
						.verify(&msg, Some(delivery_address.clone()))
						.map_err(|_| Error::<T>::InvalidSignature)?;
				},
			}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L309-315)
```rust
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}
```
