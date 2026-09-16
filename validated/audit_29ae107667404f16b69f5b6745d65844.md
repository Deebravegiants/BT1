### Title
`retryPayload` in `HyperbridgeLzEndpoint` bypasses the `whenNotPaused` guard that protects inbound message delivery - ([File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol])

### Summary
`HyperbridgeLzEndpoint.onAccept`, the primary ISMP inbound-delivery path, is protected by `whenNotPaused`, but the permissionless recovery path `retryPayload`, which performs the exact same privileged action (calling `lzReceive` on an arbitrary destination OApp as the trusted endpoint), carries no such guard. Anyone can therefore keep delivering previously-stored failed payloads even while the contract owner has paused the endpoint.

### Finding Description
`onAccept` is the sole entry point through which the adapter is meant to push cross-chain messages into destination OApps, and it is explicitly gated: [1](#0-0) 

When `lzReceive` reverts inside `onAccept`, the payload hash is stored for later retry: [2](#0-1) 

The recovery function `retryPayload` reproduces this exact call to `ILayerZeroReceiver(receiver).lzReceive(...)`, is explicitly documented as mirroring `onAccept`'s direct call, is permissionless ("anyone may push a stuck payload"), and is declared `external payable` with no `whenNotPaused` modifier: [3](#0-2) 

This is structurally identical to the referenced GoGoPool finding: a "primary" state-changing entry point (`stakeGGP`/`withdrawGGP` ≈ `onAccept`) is paused, but a secondary function performing the same effect (`restakeGGP`/`claimAndRestake` ≈ `retryPayload`) is left unprotected, letting the effect continue to occur after the owner pauses the contract.

### Impact Explanation
`pause()` on this contract is documented and intended as an emergency stop for "all cross-chain operations (send and receive)". If the owner pauses the endpoint in response to a compromised or misbehaving message (e.g. a malicious/malformed LZ payload that was rejected once by the destination OApp and is sitting in `_inboundPayloadHashes`, or a bug discovered in an OApp's `lzReceive` handling), `retryPayload` still lets anyone force-execute that stored payload against the destination OApp. Since destination OApps trust `msg.sender == address(this)` (the endpoint) for authorization, this can drive unauthorized state changes/fund movement in downstream OApps during a period where the operator explicitly believed inbound delivery was halted, defeating the purpose of the pause and potentially causing loss of funds in affected OApps that assumed delivery was frozen.

### Likelihood Explanation
High: any relayer or arbitrary third party can call `retryPayload` at any time with no special privileges — the only precondition is that a stored `_inboundPayloadHashes` entry exists for a `(receiver, srcEid, sender, nonce)` tuple, which naturally arises whenever an OApp's `lzReceive` reverts even once under normal operation. No proof or attacker-controlled state is required beyond a pre-existing failed delivery.

### Recommendation
Add the `whenNotPaused` modifier to `retryPayload` (and audit other functions such as `clear`/`skip`/`nilify`/`burn`-style payload management functions for the same class of bypass), so that pausing the endpoint uniformly halts every path that can invoke `lzReceive` on downstream OApps, not just the primary `onAccept` path.

### Proof of Concept
1. Owner calls `pause()` on `HyperbridgeLzEndpoint` after detecting an issue.
2. A payload for some `(receiver, srcEid, sender, nonce)` was previously stored in `_inboundPayloadHashes` because the OApp's `lzReceive` reverted during an earlier `onAccept` call (see lines 384-395).
3. Any address calls `retryPayload(receiver, origin, guid, message)` with the matching stored payload.
4. The call succeeds because `retryPayload` has no `whenNotPaused` check, and `ILayerZeroReceiver(receiver).lzReceive(...)` is executed exactly as if the contract were unpaused, delivering the message to the destination OApp despite the pause.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L355-360)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        // Verify source is this adapter on another chain
        if (keccak256(request.from) != keccak256(abi.encodePacked(address(this)))) revert UnknownSource();

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L405-433)
```text
    /**
     * @notice Retries an inbound delivery whose OApp `lzReceive` previously reverted in {onAccept}.
     * @dev Mirrors {onAccept}'s direct call to the OApp (the adapter is the caller, so the OApp's
     * `onlyEndpoint` check still passes). Permissionless: anyone may push a stuck payload through
     * once it is executable again. On success the stored payload hash is cleared; if delivery
     * reverts again the whole call reverts and the payload remains recoverable.
     * @param receiver The destination OApp
     * @param origin The (srcEid, sender, nonce) of the stored payload
     * @param guid The original message guid
     * @param message The original message payload (must match the stored hash)
     */
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
