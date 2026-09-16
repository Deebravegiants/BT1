Confirmed: `retryPayload` at `HyperbridgeLzEndpoint.sol#L416-433` lacks the `whenNotPaused` modifier, while `onAccept` (the primary inbound entrypoint) is guarded by it at line 355. This is the same bug class as the report: a pause-guarded primary delivery path has a permissionless secondary path (`retryPayload`, analogous to `retryMessage`/`_nonblockingLzReceive`) that performs the equivalent sensitive action (calling `lzReceive` on the destination OApp, which mints tokens or executes arbitrary calldata depending on the OApp) without re-checking the pause state.

### Title
Owner pause of `HyperbridgeLzEndpoint` can be bypassed via `retryPayload`, allowing inbound message delivery while paused - (File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol)

### Summary
`HyperbridgeLzEndpoint.onAccept` is gated by `whenNotPaused` so that when the owner pauses the endpoint, no new inbound LZ messages are delivered to destination OApps. However, `retryPayload`, the permissionless recovery function that redelivers a previously failed inbound payload, has no `whenNotPaused` check.

### Finding Description
`onAccept` decodes an inbound ISMP `PostRequest` into an LZ-style message and calls `lzReceive` on the destination OApp; it is protected by `onlyHost whenNotPaused` [1](#0-0) . If the OApp's `lzReceive` reverts, the payload hash is stored in `_inboundPayloadHashes` for later recovery [2](#0-1) .

`retryPayload` is the designated mechanism to redeliver such a stored payload, and it performs the exact same sensitive action — calling `lzReceive` on the destination OApp — but is declared without `whenNotPaused`: [3](#0-2) 

Because `retryPayload` is explicitly permissionless ("anyone may push a stuck payload through"), any address can call it while the contract is paused, as long as a matching failed payload was previously stored via `onAccept` before the pause (or is stored by any prior failed delivery). This defeats the purpose of `pause()`, which is documented as pausing "all cross-chain operations (send and receive)" [4](#0-3) .

This mirrors the reported bug class exactly: the owner-facing pause guard is placed on the "front door" entrypoint (`onAccept`/`_blockingLzReceive`), but the retry/replay entrypoint (`retryPayload`/`retryMessage`) that performs the equivalent state-changing delivery omits the same guard, so a paused contract can still process/execute an inbound cross-chain message.

### Impact Explanation
If the owner pauses `HyperbridgeLzEndpoint` (e.g., in response to a detected exploit, a compromised source-chain OApp, or an emergency at the ISMP/consensus layer), inbound message delivery to arbitrary destination OApps can still be forced through via `retryPayload` for any payload that failed and was stored prior to (or is stored at any point during) the pause. Depending on the destination OApp's `lzReceive` logic (e.g., LayerZero OFTs relaying mint/unlock operations), this can result in unauthorized minting/unlocking of tokens or execution of arbitrary OApp logic while the operator believes the channel is fully halted — undermining the incident-response guarantee that `pause()` is meant to provide.

### Likelihood Explanation
The precondition is simply that at least one inbound delivery has previously failed and been stored (a routine occurrence, since `onAccept` explicitly isolates and stores failures from any deterministically-reverting `lzReceive`, e.g., "over-cap mint, blocklisted recipient, malformed payload, paused OApp" per the code's own comment). Once such a stored payload exists, any unprivileged account can call `retryPayload` regardless of the endpoint's pause state — no special privileges, timing races, or complex preconditions are required.

### Recommendation
Add the `whenNotPaused` modifier to `retryPayload` (matching `onAccept`), consistent with the report's recommendation to guard the actual delivery/execution path rather than only the initial entrypoint. Since `retryPayload` performs the same OApp delivery action as `onAccept`, pausing the endpoint should block both.

### Proof of Concept
1. Owner calls `HyperbridgeLzEndpoint.setEidMapping(...)` and configures the endpoint normally.
2. A malicious or malformed inbound message causes `onAccept` to store a failed payload hash in `_inboundPayloadHashes` (this is the designed failure-isolation path) [5](#0-4) .
3. Owner calls `pause()`, expecting all inbound/outbound operations to halt [6](#0-5) .
4. Any unprivileged account calls `retryPayload(receiver, origin, guid, message)` with the matching stored payload; since `retryPayload` has no `whenNotPaused` check, it succeeds and calls `lzReceive` on the destination OApp, delivering the message despite the pause [7](#0-6) .
5. `onAccept` for genuinely new inbound messages remains blocked, but any previously-failed payload can still be forced through, demonstrating the inconsistent pause enforcement.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L243-249)
```text
    /**
     * @notice Pauses all cross-chain operations (send and receive)
     * @dev Only callable by the contract owner
     */
    function pause() external onlyOwner {
        _pause();
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L355-356)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L388-395)
```text
        Origin memory origin = Origin({srcEid: srcEid, sender: sender, nonce: nonce});
        try ILayerZeroReceiver(receiverAddr).lzReceive(origin, guid, message, address(0), "") {
            // delivered successfully
        } catch {
            bytes32 payloadHash = keccak256(abi.encode(guid, message));
            _inboundPayloadHashes[receiverAddr][srcEid][sender][nonce] = payloadHash;
            emit InboundPayloadStored(receiverAddr, srcEid, sender, nonce, payloadHash);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L416-433)
```text
    function retryPayload(
        address receiver,
        Origin calldata origin,
        bytes32 guid,
        bytes calldata message
    ) external payable {
        bytes32 stored = _inboundPayloadHashes[receiver][origin.srcEid][origin.sender][origin.nonce];
        if (stored == bytes32(0) || stored == NIL_PAYLOAD_HASH || stored != keccak256(abi.encode(guid, message))) {
            revert InvalidPayloadHash();
        }

        // Clear first; if the retry reverts, this deletion rolls back with the rest of the tx and
        // the payload remains recoverable.
        delete _inboundPayloadHashes[receiver][origin.srcEid][origin.sender][origin.nonce];

        ILayerZeroReceiver(receiver).lzReceive{value: msg.value}(origin, guid, message, msg.sender, "");
        emit InboundPayloadResolved(receiver, origin.srcEid, origin.sender, origin.nonce);
    }
```
