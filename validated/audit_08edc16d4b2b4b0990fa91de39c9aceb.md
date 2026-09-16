Found a valid analog. The bug class in the report — a delivery path that fails to recheck an authorization/security gate that the primary delivery path enforces — has a direct parallel in `HyperbridgeLzEndpoint`'s retained-payload retry mechanism.

### Title
`retryPayload` bypasses the `Pausable` gate, delivering retained cross-chain messages while the endpoint is paused - ([File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol])

### Summary
`HyperbridgeLzEndpoint.onAccept`, the primary inbound delivery path, is gated by `whenNotPaused` [1](#0-0) , matching `send`'s outbound gate [2](#0-1) . However `retryPayload`, the recovery path that redelivers a previously-stored/retained inbound payload to the destination OApp, carries no `whenNotPaused` check at all [3](#0-2) .

### Finding Description
The pause mechanism is documented as halting "all cross-chain operations (send and receive)" [4](#0-3) . When an inbound `lzReceive` call reverts in `onAccept`, the payload hash is retained in `_inboundPayloadHashes` for later replay [5](#0-4) . That retained/"stored" payload is exactly analogous to a NATS "retained message" or QoS1+ durable-replay entry: a piece of already-authorized data whose delivery is deferred and later replayed through a **second** code path.

`retryPayload` is that second path. It is permissionless — callable by anyone — and only rechecks that the supplied `(guid, message)` hashes to the value stored for `(receiver, srcEid, sender, nonce)` before calling `lzReceive` directly on the destination OApp [3](#0-2) . It does not recheck the `whenNotPaused` invariant that `onAccept` enforces for every fresh delivery. So once the owner calls `pause()` (e.g., in response to a discovered issue with a source chain, a bad EID mapping, or a compromised sender), any already-queued retained payload can still be pushed through to the OApp, and `lzCompose` has the same gap for queued compose messages [6](#0-5) .

This mirrors the JLSEC-2026-1146 root cause precisely: the "fast path"/primary check (deny rule / `whenNotPaused`) is enforced at initial dispatch, but a secondary delivery/replay path re-derives delivery from cached state without rechecking that same gate.

### Impact Explanation
`pause()` is the operator's emergency stop for this bridge adapter — its entire purpose is to prevent any further message delivery to OApps during an incident. `retryPayload` (and `lzCompose`) silently defeats that control for any payload that failed and was retained before the pause. Since retained payloads can originate from a source chain/state-machine mapping the owner is actively trying to shut off, this allows unauthorized delivery of cross-chain messages to OApps during a period the protocol explicitly intended to be frozen, undermining the "unauthorized app action" / "route unable to be halted" guarantee the pause primitive is relied upon for. It is reachable by any unprivileged caller with no special permissions.

### Likelihood Explanation
Likelihood is moderate to high: it only requires (1) at least one inbound `lzReceive` call to have reverted at some point (recorded as retained), and (2) the owner subsequently calling `pause()`. Both are ordinary operational conditions — reverts on `lzReceive` are explicitly anticipated and handled by the retry design itself, and pausing is the documented incident-response action. No special privileges are needed to trigger the bypass; the caller of `retryPayload` needs only knowledge of the original `(guid, message)`, which is emitted on-chain via `InboundPayloadStored`.

### Recommendation
Add the `whenNotPaused` modifier to `retryPayload` (and to `lzCompose`, for consistency with the "pauses all cross-chain operations" contract), so that pausing the endpoint reliably halts all delivery paths, not just the primary `onAccept` path.

### Proof of Concept
1. An OApp `X` has `lzReceive` temporarily reverting (e.g., due to a transient failure or a malicious payload it wants to reject at a given moment). A message is delivered via `onAccept`, `lzReceive` reverts, and the payload hash is stored under `_inboundPayloadHashes[X][srcEid][sender][nonce]` [7](#0-6) .
2. The owner detects a problem (e.g., a compromised source state machine or a bug in the payload) and calls `pause()` [8](#0-7) , expecting no further deliveries to occur.
3. Any address calls `retryPayload(X, origin, guid, message)` with the exact stored payload. Since `retryPayload` has no `whenNotPaused` check, the call succeeds and `lzReceive` executes on `X` despite the pause [3](#0-2) .
4. The message is delivered to the OApp even though the protocol operator explicitly paused "all cross-chain operations (send and receive)."

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L262-265)
```text
    function send(
        MessagingParams calldata _params,
        address /* _refundAddress */
    ) external payable override whenNotPaused returns (MessagingReceipt memory) {
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L355-355)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-395)
```text
        // Deliver to the OApp. Isolate the external call so a deterministic revert (zero
        // recipient, over-cap mint, blocklisted recipient, malformed payload, paused OApp, etc.)
        // does not revert `onAccept`. On failure the payload is retained for later retry/recovery
        // via retryPayload/clear/skip/nilify/burn.
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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L643-659)
```text
    function lzCompose(
        address _from,
        address _to,
        bytes32 _guid,
        uint16 _index,
        bytes calldata _message,
        bytes calldata _extraData
    ) external payable override {
        bytes32 key = keccak256(abi.encodePacked(_from, _to, _guid, _index));
        bytes32 expectedHash = _composeQueue[key];
        if (expectedHash == bytes32(0) || expectedHash != keccak256(_message)) revert InvalidCompose();

        delete _composeQueue[key];

        ILayerZeroComposer(_to).lzCompose{value: msg.value}(_from, _guid, _message, msg.sender, _extraData);
        emit ComposeDelivered(_from, _to, _guid, _index);
    }
```
