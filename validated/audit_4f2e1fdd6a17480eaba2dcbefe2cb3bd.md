## Title
Optimism dispute-game UUID front-running griefing permanently blocks Hyperbridge's `op-verifier` consensus client from advancing the OP state machine - (File: `modules/ismp/clients/optimism/src/lib.rs`)

### Summary
Hyperbridge's Optimism consensus client (`op-host`/`op-verifier`) treats an OP Stack Fault Dispute Game as finalized proof of an L2 output root as soon as the game exists in the `DisputeGameFactory` and its `claimData` array has exactly one entry (i.e. is "unchallenged"), rather than waiting for full game resolution. This is the exact same `DisputeGameFactory` UUID mechanism described in the referenced report (`getGameUUID(gameType, rootClaim, extraData)`), so the reported griefing attack (create-and-self-counter a game for the correct-but-not-yet-safe output root) also permanently prevents Hyperbridge from ever accepting that block's state commitment.

### Finding Description
Hyperbridge derives a game's identity the same way OP's factory does: [1](#0-0) 

and looks it up via `dispute_game_key`/`DISPUTE_GAMES_SLOT` in the factory's storage proof: [2](#0-1) 

Instead of waiting for the dispute game's 3.5‑day clock + resolution, Hyperbridge accepts the root as valid purely based on the `FaultDisputeGame`'s `claimData` array length being `1` (i.e. no counter-claim has ever been made): [3](#0-2) 

If `claimData.length != 1`, Hyperbridge returns `FaultDisputeGameChallenged` and the relayer skips that game entirely, as implemented in `fetch_dispute_game_payload`, which silently `continue`s past any game whose root does not derive cleanly and picks only the highest-height accepted payload: [4](#0-3) 

Because dispute game creation on L1 is fully permissionless (anyone can call `create(gameType, rootClaim, extraData)` on the factory) exactly as in the referenced report, an attacker can:
1. Predict/front-run the batcher's next L2 block (or simply wait for it to be posted) and immediately create a `FaultDisputeGame` whose `rootClaim` equals the output root that will become the real safe/canonical root for that L2 block.
2. Immediately counter their own claim in the same transaction, appending a second `claimData` entry.

This produces exactly the state Hyperbridge's `verify_not_challenged` rejects (`claimData.length == 2`), for the identical UUID (`getGameUUID`) that the honest/legitimate root would also hash to, since a game with that UUID already exists and a new `create()` call with the same `(gameType, rootClaim, extraData)` reverts with `GameAlreadyExists` (mirrored from the report's snippet). No honest party can ever register an "unchallenged" game for that exact output root afterward.

### Impact Explanation
For every L2 block that the attacker grieves this way, Hyperbridge's `op-host`/`op-verifier` client can never produce a valid `IntermediateState`/state machine commitment for that height, because the only on-chain proof of that root (the dispute game) will always show `claimData.length != 1`. If the attacker continuously grieves every new L2 block (the same cost model as in the referenced report), the Optimism-based state machine's `latestStateMachineHeight` in `IsmpHost` never advances, which:
- Halts delivery of ISMP `PostRequest`/`GetResponse` messages that rely on state proofs against that chain's commitment (`handlePostRequests`/`handleGetResponses` in `HandlerV2.sol` require `host.stateMachineCommitment(...)` to be non-zero and fresh).
- Permanently blocks any withdrawal/message route that depends on a state commitment for that OP state machine — i.e. "a route unable to deliver messages," matching the accepted impact category for this scan.

This is strictly worse for Hyperbridge than for native OP withdrawals: OP's own `OptimismPortal` can eventually use a *resolved* (won) game even if it took the full challenge period, but Hyperbridge's shortcut of accepting only "never-challenged" games means a game that is challenged-and-later-resolved-in-favor-of-the-root-claim is still never picked up, since `fetch_dispute_game_payload` only checks the instantaneous `claimData.length`, not final game resolution.

### Likelihood Explanation
The attack requires the same capital/gas outlay analyzed in the referenced report (continuously creating and self-countering a dispute game for every relevant block), which the original judges rated as unlikely to be economically worthwhile but still a valid Medium-severity issue because it is fully permissionless, requires no privileged role, and produces a genuine availability failure for the affected route. The same cost/likelihood profile applies here, since Hyperbridge is a passive downstream consumer of the identical `DisputeGameFactory` state.

### Recommendation
Do not rely solely on the "unchallenged claimData length == 1" heuristic to accept an OP output root. Either:
- Require full game resolution (`resolve()` outcome favoring the root claim) before accepting the state commitment, or
- Include additional binding context (e.g., `parentHash`) in the acceptance check so that a self-countered/challenged game for the correct root does not permanently exclude it, and instead allow Hyperbridge to pick up the root once the dispute resolves in its favor rather than only trusting pristine, never-challenged games.

### Proof of Concept
1. Attacker monitors the OP L2 chain and, immediately after (or in anticipation of) a block being posted/becoming safe, calls `DisputeGameFactory.create(gameType, rootClaim, extraData)` with `rootClaim` equal to that block's correct output root.
2. In the same transaction, the attacker calls `attack()`/`move()` on the freshly created game to counter their own root claim, so `claimData.length` becomes `2`.
3. Hyperbridge's relayer picks up the `DisputeGameCreated` event, builds a proof via `fetch_dispute_game_payload`, and `verify_optimism_dispute_game_proof` → `verify_not_challenged` returns `Err(Error::FaultDisputeGameChallenged)` (see `modules/ismp/clients/optimism/src/lib.rs:452-459`), causing the payload for that block to be skipped (`tesseract/consensus/op-host/src/lib.rs:587-590` and surrounding `continue` branches).
4. No other game can ever be created with the same `getGameUUID(gameType, rootClaim, extraData)` (factory-level `GameAlreadyExists` revert), so the honest root for that block can never be re-submitted and accepted "unchallenged."
5. Repeating this for every new L2 block permanently stalls `latestStateMachineHeight` for the OP state machine in Hyperbridge, halting message/withdrawal delivery on that route.

### Citations

**File:** modules/ismp/clients/optimism/src/lib.rs (L248-257)
```rust
// https://github.com/ethereum-optimism/optimism/blob/f707883038d527cbf1e9f8ea513fe33255deadbc/packages/contracts-bedrock/src/dispute/DisputeGameFactory.sol#L127
pub fn get_game_uuid<H: Keccak256>(game_type: u32, root_claim: H256, extra_data: Vec<u8>) -> H256 {
	let tokens = [
		ethabi::Token::Uint(game_type.into()),
		ethabi::Token::FixedBytes(root_claim.0.to_vec()),
		ethabi::Token::Bytes(extra_data),
	];
	let encoded = ethabi::encode(&tokens);
	H::keccak256(&encoded)
}
```

**File:** modules/ismp/clients/optimism/src/lib.rs (L307-319)
```rust
	let game_uuid = get_game_uuid::<H>(payload.game_type, root_claim, payload.extra_data);

	let dispute_game_key = derive_map_key::<H>(game_uuid.0.to_vec(), DISPUTE_GAMES_SLOT);

	// Does the dispute game's unique identifier exist in the _disputeGames map?
	let proof_value = match get_value_from_proof::<H>(
		dispute_game_key.0.to_vec(),
		factory_storage_root,
		payload.dispute_game_proof,
	)? {
		Some(value) => value.clone(),
		_ => Err(Error::DisputeGameIdMissing)?,
	};
```

**File:** modules/ismp/clients/optimism/src/lib.rs (L429-461)
```rust
	match kind {
		DisputeGameImpl::FaultDisputeGame => {
			// `claimData` is a dynamic `ClaimData[]` at `FAULT_DISPUTE_CLAIM_DATA_SLOT`. Solidity
			// stores a dynamic array's element count in the slot itself (the elements live at
			// `keccak256(slot)`). A freshly created, unchallenged game holds exactly one entry —
			// the root claim appended in `initialize()` — and every `move()` (attack or defense)
			// appends another. So `claimData.length == 1` iff the game has not been challenged.
			// Any other length (including absence, i.e. length 0 for a game that never registered
			// its root claim) is rejected.
			//
			// The MPT trie path for a direct storage slot is `keccak256(slot)`.
			let storage_key = U256::from(FAULT_DISPUTE_CLAIM_DATA_SLOT).to_big_endian();
			let trie_path = H::keccak256(&storage_key);
			let value = get_value_from_proof::<H>(
				trie_path.0.to_vec(),
				proxy_storage_root,
				challenge_proof,
			)?
			.ok_or(Error::ClaimDataSlotMissing)?;
			let raw = <alloy_primitives::Bytes as Decodable>::decode(&mut &*value)
				.map_err(|_| Error::DecodeClaimData(format!("{:?}", value)))?
				.0
				.to_vec();
			if raw.len() > 32 {
				Err(Error::ClaimDataTooLong)?
			}
			// RLP strips leading zeros from the stored length; reconstruct the uint256 and require
			// it to be exactly one.
			if U256::from_big_endian(&raw) != U256::one() {
				Err(Error::FaultDisputeGameChallenged)?
			}
			Ok(())
		},
```

**File:** tesseract/consensus/op-host/src/lib.rs (L579-597)
```rust
			// Check if rootClaim matches derived output root.
			let output_root = calculate_output_root::<Hasher>(
				payload.version,
				payload.header.state_root,
				payload.withdrawal_storage_root,
				l2_block_hash,
			);

			if output_root.0 != event.rootClaim.0 {
				log::trace!(target: LOG_TARGET, "Found a dispute game event with an invalid output root, Expected: {output_root:?}, Found: {:?}", event.rootClaim);
				continue;
			}

			payloads.push(payload)
		}

		payloads.sort_unstable_by(|a, b| a.header.number.cmp(&b.header.number));

		Ok(payloads.last().cloned())
```
