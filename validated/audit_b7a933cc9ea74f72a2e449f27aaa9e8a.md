### Title
Unpriced CPU exhaustion via `pallet-ismp`'s `validate_unsigned` executing full consensus/message verification for free on every submission - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Pallet::validate_unsigned` runs the **entire** message-handling pipeline (`Self::execute(messages.clone())`) — including full consensus-proof cryptography (GRANDPA ed25519 loops, Tendermint/CometBFT validator-signature loops, storage/child-trie membership proofs) — inside transaction-pool validation, which every full node performs for free, on an unsigned, feeless extrinsic, before any economic cost is paid. [1](#0-0) 

### Finding Description
`handle_unsigned` is dispatched with `ensure_none(origin)` — no signer, no nonce, no transaction fee. [2](#0-1) 

Its `ValidateUnsigned::validate_unsigned` implementation does not perform a cheap, bounded pre-check before doing real work: it calls `Self::execute(messages.clone())`, which is the exact same execution path used at block-authoring time, running full `ConsensusClient::verify_consensus` / handler logic for every message in the batch. [3](#0-2) 

Because `validate_unsigned` is the function every full node in the network runs to admit a transaction into its transaction pool (on submission, on gossip re-validation, and again at block-building/import time), the cryptographic cost of verifying a consensus/message proof is paid by *every node that receives the transaction*, not just the block author, and it is paid *before* the transaction is included in any block and before any fee is charged. The `handle_unsigned` docs and README explicitly acknowledge the free-verification model and rely solely on "invalid proofs get rejected by the pool" as the anti-spam argument: [4](#0-3) 

That argument does not hold for consensus messages whose *verification itself* is CPU-heavy regardless of the final valid/invalid outcome. Two concrete consensus clients reachable this way perform unbounded-size, signature-heavy loops as part of proof verification:

- GRANDPA: `GrandpaJustification::verify_with_voter_set` iterates every precommit in `self.commit.precommits`, performing an `ed25519_verify` per precommit, then walking ancestry for each, before any economic gate is applied. [5](#0-4) [6](#0-5) 

- Tendermint/CometBFT: `verify_header_update` runs `PredicateVerifier::verify_update_header`, which internally verifies signatures/voting power across the (attacker-supplied) validator set via `SpIoSignatureVerifier`. [7](#0-6) [8](#0-7) 

By contrast, the same runtimes explicitly recognized this exact cost/DoS problem for the ECDSA/BEEFY consensus path and closed it off: `IsmpCallFilter` on `nexus` rejects any `handle_unsigned` batch carrying a BEEFY consensus message, forcing BEEFY updates through the fee-paying, signed `submit_proof` extrinsic instead — with the comment explicitly citing that skipping this "would bypass that requirement entirely." [9](#0-8) 

No equivalent filter or fee gate is applied to GRANDPA, Tendermint, or other consensus clients that remain reachable through the free `handle_unsigned`/`validate_unsigned` path, so the mitigation applied to BEEFY was not generalized.

### Impact Explanation
An unprivileged network participant (any relayer/dispatcher, or simply anyone able to submit a transaction to a node's RPC/gossip) can submit a stream of `handle_unsigned` extrinsics carrying maximal-size, maximal-validator-set consensus proofs (crafted to be cryptographically expensive to verify but ultimately invalid or stale) at zero fee cost. Since `validate_unsigned` re-executes the full verification on every node that receives the transaction — during initial submission, on gossip propagation to peers, and again at block-import time for every collator that receives it — this can exhaust CPU resources network-wide, directly analogous to CVE-2021-28089 (Tor directory protocol CPU exhaustion via cheap, remotely-triggerable, but expensive-to-process requests). Sustained CPU exhaustion across relaying/collator nodes degrades throughput, delays legitimate message delivery, and can be used to grief specific consensus clients (GRANDPA/Tendermint) that lack the fee-gated path BEEFY was given.

### Likelihood Explanation
High likelihood: `handle_unsigned` is a public, unsigned, no-nonce extrinsic by design (to allow free relaying), so there is no economic disincentive to spamming it. Building maximal validator-set / precommit-count proof payloads only requires knowing public chain parameters (validator set sizes), not any privileged access. The attack requires no admin/governance/collator compromise — any unprivileged relayer or transaction submitter can trigger it, matching the "unprivileged message dispatcher/relayer" reachability required.

### Recommendation
- Apply the same mitigation already used for BEEFY consensus messages to all other consensus clients reachable via `handle_unsigned`: either require these updates to go through a signed, fee-paying extrinsic, or extend `IsmpCallFilter` to reject consensus messages that are known to be CPU-expensive to verify when submitted through the free unsigned path.
- Add a cheap, bounded pre-validation step inside `pallet_ismp`'s `validate_unsigned` that checks proof size / validator-set-size bounds and rejects oversized or implausible proofs *before* invoking `Self::execute`, so the expensive cryptographic verification is not run for arbitrarily-sized attacker-controlled inputs during mempool validation.
- Consider rate-limiting or requiring a minimal stake/bond for submitting unsigned consensus messages, or capping the number of signatures/precommits/validators processed per `validate_unsigned` call.

### Proof of Concept
1. Craft a `Message::Consensus` (or `Message::Request`/other) payload for the GRANDPA or Tendermint consensus client with the maximum permitted number of precommits/validator signatures (as allowed by `frame_system`'s extrinsic size limits), using arbitrary/garbage signatures so the proof is ultimately rejected.
2. Submit this as an unsigned `Ismp::handle_unsigned` extrinsic to a node's RPC endpoint, or broadcast it over the P2P transaction gossip network.
3. Because `validate_unsigned` calls `Self::execute(messages.clone())` unconditionally (`modules/pallets/ismp/src/lib.rs:619-625`), every node that receives the transaction (via RPC submission or gossip) performs the full GRANDPA justification signature-verification loop (`modules/consensus/grandpa/primitives/src/justification.rs:109-134`, one `ed25519_verify` per precommit) or Tendermint validator-set signature verification (`modules/consensus/tendermint/verifier/src/verifier.rs:21-79`) before rejecting the transaction — paying full cryptographic cost for a transaction that never enters a block and costs the submitter nothing.
4. Repeat at high rate from multiple sources to sustain CPU exhaustion across the relaying/collator network, since resubmission cost is zero (unsigned, no nonce, no fee) and each submission/re-gossip round re-triggers full verification on every receiving node.

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

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L109-134)
```rust
		let mut visited_hashes = BTreeSet::new();
		for signed in self.commit.precommits.iter() {
			let message = finality_grandpa::Message::Precommit(signed.precommit.clone());

			check_message_signature::<_, _>(
				&message,
				&signed.id,
				&signed.signature,
				self.round,
				set_id,
			)?;

			if base_hash == signed.precommit.target_hash {
				continue;
			}

			let route = ancestry_chain
				.ancestry(base_hash, signed.precommit.target_hash)
				.map_err(|_| anyhow!("[verify_with_voter_set] Invalid ancestry!"))?;
			// ancestry starts from parent hash but the precommit target hash has been
			// visited
			visited_hashes.insert(signed.precommit.target_hash);
			for hash in route {
				visited_hashes.insert(hash);
			}
		}
```

**File:** modules/consensus/grandpa/primitives/src/justification.rs (L244-248)
```rust
{
	let buf = (message, round, set_id).encode();

	let valid =
		sp_io::crypto::ed25519_verify(&signature.clone().into(), buf.as_ref(), &id.clone().into());
```

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L21-79)
```rust
pub fn verify_header_update(
	trusted_state: TrustedState,
	consensus_proof: ConsensusProof,
	current_time: u64,
) -> Result<UpdatedTrustedState, VerificationError> {
	consensus_proof.validate().map_err(|e| VerificationError::Invalid(e))?;

	let chain_id = Id::try_from(trusted_state.chain_id.clone())
		.map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let height = Height::try_from(trusted_state.height)
		.map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let timestamp = Timestamp { seconds: trusted_state.timestamp as i64, nanos: 0 };
	let time = Time::try_from(timestamp).map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let next_validators = ValidatorSet::new(trusted_state.next_validators.clone(), None);
	let next_validators_hash = Hash::Sha256(trusted_state.next_validators_hash);

	let tendermint_trusted_state = TrustedBlockState {
		chain_id: &chain_id,
		header_time: time,
		height,
		next_validators: &next_validators,
		next_validators_hash,
	};

	let validators = extract_validators(&trusted_state, &consensus_proof)?;
	let next_validators = consensus_proof
		.next_validators
		.as_ref()
		.map(|validators| ValidatorSet::new(validators.clone(), None));

	let untrusted_block_state = UntrustedBlockState {
		signed_header: &consensus_proof.signed_header,
		validators: &validators,
		next_validators: next_validators.as_ref(),
	};

	let verifier_options = convert_verification_options(
		&trusted_state.verification_options,
		trusted_state.trusting_period_duration(),
	)?;
	let now = convert_timestamp(current_time)?;

	let verifier = SpIoVerifier::default();
	let result = verifier.verify_update_header(
		untrusted_block_state,
		tendermint_trusted_state,
		&verifier_options,
		now,
	);

	match result {
		Verdict::Success => {
			let updated_state = create_updated_trusted_state(&trusted_state, &consensus_proof)?;
			Ok(updated_state)
		},
		Verdict::NotEnoughTrust(tally) =>
			Err(VerificationError::NotEnoughTrust(format!("Voting power tally: {}", tally))),
		Verdict::Invalid(detail) => Err(VerificationError::Invalid(format!("{:?}", detail))),
	}
```

**File:** modules/consensus/tendermint/verifier/src/hashing.rs (L31-86)
```rust
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct SpIoSignatureVerifier;

impl signature::Verifier for SpIoSignatureVerifier {
	fn verify(
		pubkey: PublicKey,
		msg: &[u8],
		signature: &Signature,
	) -> Result<(), signature::Error> {
		match pubkey {
			PublicKey::Ed25519(pk) => {
				let sig = polkadot_sdk::sp_core::ed25519::Signature::try_from(signature.as_bytes())
					.map_err(|_| signature::Error::MalformedSignature)?;
				let pub_key = polkadot_sdk::sp_core::ed25519::Public::try_from(pk.as_bytes())
					.map_err(|_| signature::Error::MalformedPublicKey)?;

				if sp_io::crypto::ed25519_verify(&sig, msg, &pub_key) {
					Ok(())
				} else {
					Err(signature::Error::VerificationFailed)
				}
			},
			PublicKey::Secp256k1(pk) => {
				let pub_key = polkadot_sdk::sp_core::ecdsa::Public::from_raw(
					pk.to_encoded_point(true)
						.as_bytes()
						.try_into()
						.map_err(|_| signature::Error::MalformedPublicKey)?,
				);

				let raw_sig = signature.as_bytes();

				let msg_hash = sp_io::hashing::keccak_256(msg);

				let mut sig_65_bytes = [0u8; 65];
				sig_65_bytes[..64].copy_from_slice(raw_sig);
				sig_65_bytes[64] = 0;

				let sig = polkadot_sdk::sp_core::ecdsa::Signature::from_raw(sig_65_bytes);
				let mut result = sp_io::crypto::ecdsa_verify_prehashed(&sig, &msg_hash, &pub_key);

				if !result {
					sig_65_bytes[64] = 1;
					let sig = polkadot_sdk::sp_core::ecdsa::Signature::from_raw(sig_65_bytes);
					result = sp_io::crypto::ecdsa_verify_prehashed(&sig, &msg_hash, &pub_key);
				}

				if result {
					Ok(())
				} else {
					Err(signature::Error::VerificationFailed)
				}
			},
			_ => Err(signature::Error::UnsupportedKeyType),
		}
	}
```

**File:** parachain/runtimes/nexus/src/lib.rs (L746-772)
```rust
/// Allowing raw updates through `handle_unsigned` would bypass that requirement entirely, so
/// any batch that carries a BEEFY consensus message is rejected here. `fund_message` is also
/// disabled because it will change the child trie root allowing beefy proofs that have no economic
/// value
///
/// A consensus message only names the state it updates, so we ask the host which client owns
/// that state and compare against BEEFY. Reading from the host remains correct even as more
/// states (Polkadot, Paseo) are bound to the same client over time.
pub struct IsmpCallFilter;
impl Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
}
```
