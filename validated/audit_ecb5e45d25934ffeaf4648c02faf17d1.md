### Title
Fixed wall-clock POST request timeouts do not account for L2 sequencer downtime, causing valid messages to become permanently undeliverable - (File: evm/src/core/HandlerV2.sol)

### Summary
`handlePostRequests` on the destination `EvmHost` rejects any inbound POST request whose `timeout()` has already passed, measured against the destination chain's own `block.timestamp` at delivery time. Hyperbridge is deployed to Optimism/Arbitrum-style L2 destinations that rely on a centralized sequencer. If that sequencer stalls (as has happened historically for hours), no new destination blocks are produced while wall-clock time keeps advancing on L1/off-chain. Once the sequencer resumes and posts a block whose timestamp catches up to real time, in-flight messages whose fixed `timeoutTimestamp` has been overtaken by the resumed clock become permanently undeliverable — `handlePostRequests` reverts with `MessageTimedOut()` for every relayer attempt, exactly as in the reported analog where a fixed-expiry token became unusable during option-Teller/OTLM downtime.

### Finding Description
`EvmHost.dispatch` computes a fixed absolute deadline at dispatch time using the *source* chain clock: `timeoutTimestamp = block.timestamp + post.timeout` [1](#0-0)  Delivery on the destination enforces this deadline purely against the destination's own `block.timestamp`, with no allowance for periods when the destination could not process transactions:

```
uint256 timestamp = block.timestamp;
...
if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
``` [2](#0-1) 

This is the same root cause pattern as the referenced report: an expiry that is wall-clock/timestamp based, checked at the moment of the state-changing action, with no mechanism to detect or compensate for periods where the underlying chain (an L2 with a centralized sequencer) could not process transactions. The protocol explicitly targets Optimism/Arbitrum-class L2s as destinations, whose consensus clients this codebase implements and tracks (`op-host`, Arbitrum Orbit client, L2 oracle verification) [3](#0-2)  yet no Chainlink-style sequencer-uptime check or grace-period extension exists anywhere in the timeout path for POST or GET requests on EVM destinations. Documentation confirms the check is purely timestamp-based and permanently rejects delivery once crossed: "When a POST request times out ... The request will be rejected on the destination if delivery is attempted." [4](#0-3) 

Because relayers cannot submit `handlePostRequests` to the destination at all while the sequencer is down, any request whose `timeoutTimestamp` falls within (or shortly after) the downtime window is never delivered before its expiry check trips — it is unconditionally converted into a timeout, regardless of relayer diligence or fee funding.

### Impact Explanation
This qualifies as "a route unable to deliver messages": the destination `IsmpModule::onAccept` callback that the app depends on for cross-chain state changes (e.g. minting, escrow release, governance execution) never fires for the affected request — the message is force-routed into the timeout/refund path instead of normal delivery, with no way for a relayer to complete it once the deadline has been overtaken by the resumed sequencer's catch-up timestamp. For any app or gateway whose business logic assumes eventual delivery (rather than eventual timeout) — and for any request configured with a short timeout — this can strand cross-chain application state on the source chain in a pending, only-refundable state during the exact window operators most need reliable delivery (chain outages/upgrades).

### Likelihood Explanation
Likelihood is directly tied to sequencer reliability of the configured destination L2s (Arbitrum, Optimism), both of which have had multi-hour outages historically. Any relayer, or the app itself if self-relaying, can trigger/observe this by simply attempting delivery after such an outage — no privileged access is required, and it is entirely a function of normal operation combined with the timeout parameter chosen by the dispatching app.

### Recommendation
Integrate a sequencer-uptime feed (e.g., Chainlink's L2 sequencer uptime oracle) into `EvmHost`/`HandlerV2`, and extend the effective timeout deadline by the observed downtime duration (with a grace period after the sequencer comes back up) before enforcing `MessageTimedOut()`, mirroring the mitigation suggested in the referenced report.

### Proof of Concept
1. App dispatches a POST request from chain A to an Arbitrum/Optimism destination with `timeout = T` seconds; `timeoutTimestamp = block.timestamp_A + T` is committed [1](#0-0) .
2. The destination L2 sequencer halts for a period ≥ remaining time-to-expiry (historically observed: multi-hour Arbitrum/Optimism outages).
3. No relayer can call `handlePostRequests` during the outage since the sequencer accepts no transactions.
4. Sequencer resumes and posts a block whose `block.timestamp` has caught up to real wall-clock time, which now exceeds `leaf.request.timeout()`.
5. Any relayer's subsequent `handlePostRequests` call reverts with `MessageTimedOut()` [5](#0-4) , permanently preventing delivery; the request can only be resolved via the timeout/refund path.

### Citations

**File:** evm/src/core/EvmHost.sol (L934-944)
```text
        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });
```

**File:** evm/src/core/HandlerV2.sol (L181-196)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
```

**File:** tesseract/consensus/sync-committee/src/host.rs (L221-250)
```rust
		for (state_machine, l2_host) in self.l2_clients.clone() {
			match l2_host {
				L2Host::ArbitrumOrbit(host) => {
					rollup_core_address.insert(host.state_machine, host.host.rollup_core);
					let number = host.arb_execution_client.get_block_number().await?;
					let block = host
						.arb_execution_client
						.get_block(BlockId::number(number))
						.await?
						.ok_or_else(|| {
							anyhow!(
								"Didn't find block with number {number} on {:?}",
								host.state_machine
							)
						})?;
					state_machine_commitments.push((
						StateMachineId {
							state_id: state_machine,
							consensus_state_id: self.consensus_state_id.clone(),
						},
						StateCommitmentHeight {
							commitment: StateCommitment {
								timestamp: block.header.timestamp,
								overlay_root: None,
								state_root: block.header.state_root.0.into(),
							},
							height: number,
						},
					));
				},
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L291-308)
```text
## Timeouts

When a POST request times out (exceeds its specified `timeout` period), The request will be **rejected on the destination** if delivery is attempted.

```solidity lineNumbers=159 title="hyperbridge/evm/src/core/HandlerV2.sol"
for (uint256 i = 0; i < requestsLen; ++i) {
    PostRequestLeaf memory leaf = request.requests[i];
    // check destination
    if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
    // check time-out
    if (timestamp >= leaf.request.timeout()) revert MessageTimedOut(); // [!code hl]
    // duplicate request?
    bytes32 commitment = leaf.request.hash();
    if (host.requestReceipts(commitment) != address(0)) revert DuplicateMessage();

    leaves[i] = MmrLeaf(leaf.kIndex, leaf.index, commitment);
}
```
```
