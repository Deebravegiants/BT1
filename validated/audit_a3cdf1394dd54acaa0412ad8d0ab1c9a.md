## Finding: Stale Hardcoded EVM Storage Slot Constants After `_responseCommitments` Removal

### Title
Outdated storage slot constants in the SDK message-proof derivation cause response/state-commitment proofs to target the wrong `EvmHost` storage slot - (File: `sdk/packages/sdk/src/chains/evm.ts`)

### Summary
The reported Scroll bug is a class of "storage layout drifted, hardcoded slot constant did not follow it." The same class of bug exists in Hyperbridge's EVM storage-slot constants used to build proof-query keys for `EvmHost`. The Rust consensus/state-machine client (`modules/ismp/state-machines/evm/src/presets.rs`) was updated with an explicit note that `_responseCommitments` was removed by PR #840 and no longer occupies slot 1, but the parallel TypeScript SDK constants used to derive relaying proof keys were not updated to match.

### Finding Description
`evm/src/core/EvmHost.sol` currently declares state variables in this order:
```
slot0: _requestCommitments
slot1: _requestReceipts
slot2: _responseReceipts
slot3: _stateCommitments
slot4: _stateCommitmentsUpdateTime
slot5: _latestStateMachineHeight
...
``` [1](#0-0) 

The Rust module `modules/ismp/state-machines/evm/src/presets.rs` documents this current layout and only exposes the two slots that are consumed for request commitments/receipts, explicitly noting slot 1 no longer belongs to `_responseCommitments`: [2](#0-1) 

However, `sdk/packages/sdk/src/chains/evm.ts` still defines the pre-PR#840 slot map:
```
REQUEST_COMMITMENTS_SLOT = 0n
RESPONSE_COMMITMENTS_SLOT = 1n
REQUEST_RECEIPTS_SLOT = 2n
RESPONSE_RECEIPTS_SLOT = 3n
STATE_COMMITMENTS_SLOT = 5n
``` [3](#0-2) 

Comparing against the actual layout above:
- `REQUEST_RECEIPTS_SLOT` should be `1`, not `2`.
- `RESPONSE_COMMITMENTS_SLOT` (`1n`) points at a mapping (`_responseCommitments`) that no longer exists — slot 1 is now `_requestReceipts`.
- `STATE_COMMITMENTS_SLOT` should be `3`, not `5` (slot 5 is `_latestStateMachineHeight`, an unrelated mapping).

The same hardcoded `STATE_COMMITMENT_SLOT = 5` value is duplicated in `modules/ismp/state-machines/evm/src/utils.rs::state_comitment_key`, in `tesseract/messaging/evm/src/lib.rs`, and in `sdk/packages/indexer/src/utils/state-machine.helper.ts`, none of which were reconciled with the current slot layout confirmed in `EvmHost.sol`. [4](#0-3) 

The stale `responseCommitmentKey`/`RESPONSE_COMMITMENTS_SLOT` derivation is used directly in the message-proof query path for the Substrate hub chain adapter, which is invoked whenever a relayer or any caller queries a proof for delivering a `Response`: [5](#0-4) 

### Impact Explanation
Because the slot constants no longer match `EvmHost.sol`'s actual storage layout, any code path (SDK-driven relaying, or downstream consumers reusing these constants) that constructs a storage key from `RESPONSE_COMMITMENTS_SLOT`, the shifted `REQUEST_RECEIPTS_SLOT`, or `STATE_COMMITMENTS_SLOT` will resolve to the wrong mapping slot. This can:
- Produce state proofs for the wrong storage location, causing legitimate response/state-commitment proofs to fail verification (denial of message delivery — "route unable to deliver messages").
- In degenerate cases where the mis-derived slot happens to be non-empty, allow reading/asserting data from an unrelated mapping (e.g., `_requestReceipts` instead of the intended response data), producing incorrect proof semantics for downstream consumers of these helper functions.

This mirrors the exact bug class from the Scroll report: functions "become unusable" because they were written against a stale storage layout, and any dependent flow (there, `retryMessageWithProof`; here, response/state-commitment proof construction) breaks silently.

### Likelihood Explanation
This is deterministic, not conditional on an attacker: any relayer or SDK consumer that calls the affected helper (`responseCommitmentKey`, or the duplicated `state_comitment_key`/`STATE_COMMITMENTS_SLOT` logic) after the PR #840 layout change will always compute an incorrect key. The bug is guaranteed to trigger whenever these code paths are exercised against current-layout `EvmHost` deployments; it requires no special privilege, only a normal message relay/proof-query operation.

### Recommendation
- Update `RESPONSE_COMMITMENTS_SLOT`, `REQUEST_RECEIPTS_SLOT`, `RESPONSE_RECEIPTS_SLOT`, and `STATE_COMMITMENTS_SLOT` in `sdk/packages/sdk/src/chains/evm.ts` to match the current `EvmHost.sol` layout (0, 1, 2, 3 respectively), and remove/deprecate `RESPONSE_COMMITMENTS_SLOT` entirely since that mapping no longer exists.
- Consolidate the slot constants into a single source of truth (e.g., re-export the constants already verified in `modules/ismp/state-machines/evm/src/presets.rs`) instead of duplicating magic numbers across `utils.rs`, `tesseract/messaging/evm/src/lib.rs`, the indexer helper, and the SDK, so a future storage layout change cannot silently desynchronize these locations.
- Add a regression/CI check similar to the `presets.rs` comment (`forge inspect EvmHost storage`) that fails the build if the on-chain layout diverges from the hardcoded slot constants anywhere they are duplicated.

### Proof of Concept
1. Deploy/observe the current `EvmHost.sol`; run `forge inspect EvmHost storage` to confirm slot assignments: `_requestCommitments=0`, `_requestReceipts=1`, `_responseReceipts=2`, `_stateCommitments=3`.
2. Call `responseCommitmentKey(commitment)` from `sdk/packages/sdk/src/chains/evm.ts` (uses `RESPONSE_COMMITMENTS_SLOT = 1n`) and compare the derived slot hash against `keccak256(abi.encode(commitment, uint256(1)))` — this resolves into the `_requestReceipts` mapping, not a response commitment.
3. Use this key in `PolkadotHubChain.queryProof` (`sdk/packages/sdk/src/chains/polkadotHub.ts:248-261`) to fetch a storage proof for a `Response` message and observe that the proof targets the wrong mapping/value, causing verification of the response delivery to fail (or, if `_requestReceipts` happens to have non-zero data at the colliding key, return an incorrect value).

Note: I was unable to exhaustively trace every downstream caller of `state_comitment_key` / `STATE_COMMITMENT_SLOT` in `modules/ismp/state-machines/evm/src/utils.rs` (used from `verify_state_proof` and related consensus paths) within the available tool budget, so the extent to which the Rust-side duplication is exercised on the core verification path (versus only in `tesseract` messaging, which is out-of-scope) is not fully confirmed. The SDK-side `RESPONSE_COMMITMENTS_SLOT`/`REQUEST_RECEIPTS_SLOT` mismatch against the current `EvmHost.sol` layout, however, is directly verified against source.

### Citations

**File:** evm/src/core/EvmHost.sol (L117-137)
```text
    // commitment of all outgoing requests and amount put up for relayers.
    mapping(bytes32 => FeeMetadata) private _requestCommitments;

    // commitment of all incoming requests and who delivered them.
    mapping(bytes32 => address) private _requestReceipts;

    // commitment of all incoming responses and who delivered them.
    // maps the request commitment to a receipt object
    mapping(bytes32 => ResponseReceipt) private _responseReceipts;

    // mapping of state machine identifier to latest known height to state commitment
    // (stateMachineId => (blockHeight => StateCommitment))
    mapping(uint256 => mapping(uint256 => StateCommitment)) private _stateCommitments;

    // mapping of state machine identifier to latest known height to update time
    // (stateMachineId => (blockHeight => timestamp))
    mapping(uint256 => mapping(uint256 => uint256)) private _stateCommitmentsUpdateTime;

    // mapping of state machine identifier to latest known height
    // (stateMachineId => blockHeight)
    mapping(uint256 => uint256) internal _latestStateMachineHeight;
```

**File:** modules/ismp/state-machines/evm/src/presets.rs (L16-23)
```rust
//! EvmHost storage slot indices. Values must match `forge inspect EvmHost
//! storage`. Verified for `evm/src/core/EvmHost.sol` after PR #840 removed
//! `_responseCommitments` (which used to occupy slot 1).

/// Slot index for `_requestCommitments`.
pub const REQUEST_COMMITMENTS_SLOT: u64 = 0;
/// Slot index for `_requestReceipts`.
pub const REQUEST_RECEIPTS_SLOT: u64 = 1;
```

**File:** sdk/packages/sdk/src/chains/evm.ts (L984-1007)
```typescript
/**
 * Slot for storing request commitments.
 */
export const REQUEST_COMMITMENTS_SLOT = 0n

/**
 * Slot index for response commitments map
 */
export const RESPONSE_COMMITMENTS_SLOT = 1n

/**
 * Slot index for requests receipts map
 */
export const REQUEST_RECEIPTS_SLOT = 2n

/**
 * Slot index for response receipts map
 */
export const RESPONSE_RECEIPTS_SLOT = 3n

/**
 * Slot index for state commitment map
 */
export const STATE_COMMITMENTS_SLOT = 5n
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L214-251)
```rust
// keccak256(uint256(4009) . keccak256(uint256(200_000_000) . uint256(STATE_COMMITMENT_SLOT)))
pub fn state_comitment_key(state_machine_id: U256, block_height: U256) -> (H256, H256, H256) {
	use polkadot_sdk::sp_io::hashing::keccak_256;

	const STATE_COMMITMENT_SLOT: u64 = 5;

	// Parent map key
	let slot = U256::from(STATE_COMMITMENT_SLOT).to_big_endian();

	let state_id = state_machine_id.to_big_endian();
	let mut key = state_id.to_vec();
	key.extend_from_slice(&slot);
	let parent_map_key = keccak_256(&key);

	// Commitment key
	let mut commitment_key = block_height.to_big_endian().to_vec();
	commitment_key.extend_from_slice(&parent_map_key);

	let slot_hash = keccak_256(&commitment_key);

	// Timestamp is at offset 0

	// overlay root is at offset 1

	let overlay_root_slot = {
		let slot = U256::from_big_endian(&slot_hash) + U256::one();
		H256::from_slice(&slot.to_big_endian())
	};

	// state root is at offset 2

	let state_root_key = {
		let slot = U256::from_big_endian(&slot_hash) + U256::one() + U256::one();
		H256::from_slice(&slot.to_big_endian())
	};

	(slot_hash.into(), overlay_root_slot, state_root_key)
}
```

**File:** sdk/packages/sdk/src/chains/polkadotHub.ts (L248-261)
```typescript
	async queryProof(message: IMessage, _counterparty: string, at?: bigint): Promise<HexString> {
		if (at === undefined) {
			throw new Error("PolkadotHubChain.queryProof requires an explicit block height `at`")
		}
		const host = this.hostAddress20()
		const storageKeys =
			"Requests" in message
				? message.Requests.map((c) => storageKeyForSlot(hexToBytes(requestCommitmentKey(c).slot1)))
				: message.Responses.map((c) => storageKeyForSlot(hexToBytes(responseCommitmentKey(c))))

		const q = new Map<Uint8Array, Uint8Array[]>()
		q.set(host, storageKeys)
		return this.fetchCombinedProof(at, q)
	}
```
