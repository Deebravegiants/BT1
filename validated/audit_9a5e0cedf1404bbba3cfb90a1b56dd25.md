### Title
Recovery delegate presence not enforced in `HyperbridgeLzEndpoint`, risking permanent freezing of stuck inbound messages - (File: `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol`)

### Summary
`HyperbridgeLzEndpoint` retains a reverted inbound LayerZero payload for later recovery via `retryPayload`, `clear`, `skip`, `nilify`, and `burn`. `clear`, `skip`, `nilify`, and `burn` are gated by `onlyOAppOrDelegate`, which only allows the OApp contract itself (as `msg.sender`) or a delegate registered through `setDelegate` to act. Nothing in the contract enforces that an OApp ever calls `setDelegate`, and a normal OApp contract can never itself be `msg.sender` of an externally submitted transaction unless it explicitly exposes an owner-gated pass-through function for this purpose. If a deterministically-reverting message gets stuck and no delegate was configured, the strict, sequential inbound-nonce check permanently blocks that entire `(receiver, srcEid, sender)` channel.

### Finding Description
`onAccept` advances the inbound nonce unconditionally, then attempts delivery via `try/catch`; on failure it stores the payload hash for later recovery instead of reverting the whole transaction: [1](#0-0) 

Because the nonce is committed independently of delivery success, all later nonces for that `(receiver, srcEid, sender)` tuple are blocked (`InvalidNonce`) until the stuck slot is resolved, exactly as the code comment states: [2](#0-1) 

Resolution paths are:
- `retryPayload` — permissionless, but only succeeds if `lzReceive` no longer reverts on the exact same payload: [3](#0-2) 

- `clear` / `skip` / `nilify` / `burn` — gated by `onlyOAppOrDelegate`, which requires `msg.sender == oapp` or `msg.sender == _delegates[oapp]`: [4](#0-3) [5](#0-4) 

`setDelegate` only records whatever the caller supplies; nothing checks that a delegate is ever configured, nowhere in `send`, `onAccept`, or elsewhere: [6](#0-5) 

If a message causes a deterministic revert in the destination OApp's `lzReceive` (e.g. a malformed/edge-case payload, a recipient that always fails to accept, an amount that trips an internal guard, or a temporarily/permanently paused/incompatible receiver), and:
1. the receiving OApp is a smart contract that has no built-in function to call `skip`/`clear`/`nilify`/`burn` on this specific adapter (this is a purpose-built Hyperbridge-to-LZ adapter, not the canonical LayerZero endpoint, so existing OApps were not written with this adapter's recovery interface in mind), and
2. no delegate was ever registered for that OApp (nothing requires or checks this),

then the `(receiver, srcEid, sender)` channel is permanently stuck: `retryPayload` will keep reverting on the same payload, and no account has authorization to call `skip`/`clear`/`nilify`/`burn` to move past it.

### Impact Explanation
Every subsequent legitimate message from that same `sender` to that `receiver` OApp over that `srcEid` becomes permanently undeliverable, since inbound nonces must be strictly sequential. For an OFT/OApp bridging value through this adapter, in-flight and future transfers routed on that channel are frozen indefinitely with no on-chain recourse — matching the "funds could get lost" risk in the analog report, since there is no enforced fallback actor and no documented requirement that one exist.

### Likelihood Explanation
Reachable by any unprivileged account: any sender can dispatch an LZ-style message through `send()`, and delivery is triggered by any relayer completing the ISMP proof flow into `onAccept`, which is a standard permissionless-relaying step. No privileged role is required to create the stuck condition — only a message whose destination-side execution deterministically fails and a destination OApp/delegate configuration that lacks a working recovery caller, which is entirely plausible given the adapter is unfamiliar to existing OApp implementations.

### Recommendation
Either (a) enforce that OApps register a delegate (or expose a recovery hook) before allowing messages to be routed to them through this adapter, or (b) add an endpoint-owner (or otherwise permissionless-but-safe) escape hatch to `skip`/`nilify`/`burn` a stuck payload when no delegate is configured, and document explicitly that OApps integrating with `HyperbridgeLzEndpoint` must call `setDelegate` or otherwise arrange for a caller that can satisfy `onlyOAppOrDelegate`.

### Proof of Concept
1. Deploy an OFT/OApp `Victim` that never calls `setDelegate` on `HyperbridgeLzEndpoint`, and whose `lzReceive` reverts for a certain crafted payload (e.g., an amount that trips a downstream overflow/blocklist check, or a message shape it cannot parse).
2. From the source chain, have `sender` call `send()` targeting `Victim` with the crafted payload; a relayer finalizes it through ISMP into `onAccept`, which advances `_inboundNonce[Victim][srcEid][sender]` to `1` and stores the payload hash after `lzReceive` reverts (`sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol:375-396`).
3. Call `retryPayload` — it reverts again since the payload content is unchanged (`sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol:416-433`).
4. Attempt `skip`/`clear`/`nilify`/`burn` from any account — all revert with `UnauthorizedRecovery` because `msg.sender` is neither `Victim` (a contract, unable to originate the call itself) nor `_delegates[Victim]` (unset, defaults to `address(0)`).
5. Any further legitimate message from `sender` to `Victim` on `srcEid` now permanently reverts with `InvalidNonce`, since nonce `1` can never be resolved.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L142-146)
```text
    /// @notice Restricts inbound-payload recovery to the target OApp or its configured delegate
    modifier onlyOAppOrDelegate(address oapp) {
        if (msg.sender != oapp && msg.sender != _delegates[oapp]) revert UnauthorizedRecovery();
        _;
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L375-396)
```text
        // Validate and advance the nonce. The nonce is committed BEFORE (and independently of)
        // OApp execution: a reverting `lzReceive` must not roll back this write. Otherwise the
        // message would be retried forever at the same nonce and every later nonce would be
        // permanently rejected, bricking the (receiver, srcEid, sender) channel.
        address receiverAddr = address(uint160(uint256(receiver)));
        uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
        if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
        _inboundNonce[receiverAddr][srcEid][sender] = nonce;

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L498-503)
```text
    /// @inheritdoc ILayerZeroEndpointV2
    /// @notice Authorizes a delegate to perform inbound-payload recovery on the caller OApp's behalf.
    function setDelegate(address _delegate) external override {
        _delegates[msg.sender] = _delegate;
        emit RecoveryDelegateSet(msg.sender, _delegate);
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L513-524)
```text
    function skip(
        address _oapp,
        uint32 _srcEid,
        bytes32 _sender,
        uint64 _nonce
    ) external override onlyOAppOrDelegate(_oapp) {
        uint64 expected = _inboundNonce[_oapp][_srcEid][_sender] + 1;
        if (_nonce != expected) revert InvalidNonce(expected, _nonce);
        _inboundNonce[_oapp][_srcEid][_sender] = _nonce;
        delete _inboundPayloadHashes[_oapp][_srcEid][_sender][_nonce];
        emit InboundNonceSkippedBy(_oapp, _srcEid, _sender, _nonce);
    }
```
