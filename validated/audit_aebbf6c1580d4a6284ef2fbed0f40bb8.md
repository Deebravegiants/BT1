### Title
Strict inbound-nonce enforcement in `HyperbridgeLzEndpoint.onAccept` causes permanent head-of-line-blocking (freezing) of all subsequent cross-chain messages in a channel - (File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol)

### Summary
`HyperbridgeLzEndpoint` enforces strict sequential inbound-nonce ordering per `(receiver, srcEid, sender)` channel in `onAccept`. Because the underlying ISMP protocol (via `EvmHost`/`HandlerV2`) provides no guarantee that requests are relayed or finalized in the order they were dispatched, and any relayer may independently and permissionlessly submit any individual request's proof whenever it becomes available, a single message whose delivery is delayed, censored, or withheld by relayers permanently blocks delivery of every later-nonce message queued behind it on that channel — even though those later messages are otherwise fully valid and provable on-chain.

### Finding Description
`onAccept` decodes the LZ envelope from the ISMP `PostRequest.body` and enforces: [1](#0-0) 

```solidity
address receiverAddr = address(uint160(uint256(receiver)));
uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
_inboundNonce[receiverAddr][srcEid][sender] = nonce;
```

This mirrors LayerZero's own "message ordering" feature but is applied on top of a transport (Hyperbridge/ISMP) whose delivery guarantees are fundamentally different from LayerZero's native DVN pipeline. In ISMP, each `PostRequest` is committed independently by `EvmHost.dispatch` at the source: [2](#0-1)  and can subsequently be delivered to the destination at any later time by any relayer via `HandlerV2.handlePostRequests`, which verifies each leaf's own MMR membership proof and dispatches independently per request: [3](#0-2) . There is no requirement that request `N` be delivered before request `N+1`; a relayer choosing to submit only the proof for nonce `N+1` (whether by omission, censorship, fee-prioritization, or because request `N`'s proof/consensus update is delayed) will cause `dispatchIncoming` to call `onAccept`, which will revert with `InvalidNonce`. Because `EvmHost.dispatchIncoming` catches this failure and simply returns early without persisting a receipt: [4](#0-3) , request `N+1` (and every subsequent nonce) can never be delivered until request `N` is delivered — even though `N+1..N+k` are independently valid, proven, and non-expired (the LZ endpoint dispatches with `timeout: 0`, i.e., no expiry: [5](#0-4) ).

If request `N` is permanently unable to complete — e.g. its ISMP request was dispatched but the relayer serving that lane refuses/fails to ever submit its inclusion proof, or the source chain's state root/consensus for that specific block is never finalized/observed by the configured consensus client for that state machine — nonce `N` never advances, and the channel is bricked forever for all higher nonces. This is functionally the same "lack of message ordering" root cause described in the external report (cross-chain messages are not guaranteed to be finalized/delivered in send order), except here the endpoint's own strict-ordering enforcement converts a delivery-timing anomaly into a **permanent liveness/fund-freezing failure** for the entire channel, rather than merely a transient failed transaction.

This directly affects OFT/token-bridge traffic routed through this adapter (its stated purpose: "Existing OFTs can point to this contract as their LayerZero endpoint... to use Hyperbridge for cross-chain transport"): [6](#0-5) . Locked/burned tokens on the source chain corresponding to nonces `N+1..N+k` can become permanently unmintable/undeliverable on the destination if nonce `N` never resolves, since `lzReceive` for `N+1` can never be invoked while the nonce gate blocks it.

The contract does provide a `skip()` recovery function to advance past a stuck nonce, but it is restricted to the OApp itself or its `_delegates` (`onlyOAppOrDelegate`): [7](#0-6) . This only mitigates the case where the *OApp owner* proactively notices and calls `skip`; it does not help when the OApp is an unmodified, unaware, immutable, or ownerless integrator (as the adapter is explicitly designed to be plugged into "existing OFTs... without code changes"), and it does nothing to recover the message itself — it only discards it, which is a loss of the cross-chain call/transfer, not a fix.

### Impact Explanation
Any relayer (an untrusted, permissionless actor per Hyperbridge's threat model) can withhold or delay relaying a single request in a channel to permanently freeze delivery of every subsequent message to that `(receiver, srcEid, sender)` tuple. For OFT-style token bridges built on top of this adapter, this can permanently freeze bridged funds represented by all pending nonces behind the stuck one, since the mint/credit logic on the destination OApp can only ever be invoked in strict nonce order. This qualifies as permanent freezing of funds / an inability to deliver messages for a valid, deployed cross-chain application, satisfying a valid Medium/High-severity impact.

### Likelihood Explanation
No attacker capability beyond "relayer chooses not to relay (or is unable to relay) one specific request" is required — this is inherent to any permissionless relayer network. Because Hyperbridge relaying is explicitly open/permissionless and requests have no expiry (`timeout: 0`) in this adapter, an adversarial or merely negligent/economically-disincentivized relayer, or unlucky consensus-client sync gap for the specific block containing request `N`, is sufficient to trigger the freeze. The condition can also occur non-maliciously simply from relayers processing requests out of arrival order under normal network conditions, matching the exact scenario described in the referenced report.

### Recommendation
- Do not enforce strict FIFO nonce ordering for delivery on a transport (ISMP) that provides no ordering guarantee, or make it a per-OApp opt-in with a well-defined bounded reordering window/timeout so that stuck slots can expire and be auto-skipped rather than block forever.
- Decouple correctness from delivery order: track received nonces in an out-of-order-safe structure (e.g., a bitmap/set of delivered nonces) and deliver each message independently, while surfacing ordering information to the OApp only as metadata rather than gating execution on it.
- If ordering must be preserved, allow permissionless/any-party recovery (not only OApp/delegate) after a configurable grace period, so a censored or lost lower nonce cannot indefinitely brick unrelated higher-nonce messages funded by other users.

### Proof of Concept
1. OApp `A` on chain `S` sends two ordered LZ messages via `HyperbridgeLzEndpoint.send` to receiver `R` on chain `D`: message 1 (nonce 1) and message 2 (nonce 2). Both dispatch independent ISMP `PostRequest`s via `EvmHost.dispatch` (`sdk/.../HyperbridgeLzEndpoint.sol:296-306`, `evm/src/core/EvmHost.sol:921-959`).
2. A relayer submits only the proof/leaf for message 2's request to `HandlerV2.handlePostRequests` on chain `D` (`evm/src/core/HandlerV2.sol:181-209`); this is fully valid per ISMP rules since each leaf is verified independently.
3. `EvmHost.dispatchIncoming` calls `HyperbridgeLzEndpoint.onAccept` for message 2 (`evm/src/core/EvmHost.sol:794-818`).
4. In `onAccept`, `_inboundNonce[R][S][A] == 0`, so `expectedNonce = 1`, but `nonce == 2` → reverts `InvalidNonce(1, 2)` (`sdk/.../HyperbridgeLzEndpoint.sol:375-382`).
5. `dispatchIncoming` catches the revert, deletes the receipt, and silently returns — message 2 is never delivered.
6. If message 1's request is never subsequently relayed (relayer withholds it, or its consensus proof never becomes available for that specific block), `_inboundNonce[R][S][A]` never advances past 0, and message 2 (and any further messages 3, 4, ...) can never be delivered to `R`, regardless of how many times step 2 is retried — permanently freezing all funds/state associated with those messages unless the OApp's owner/delegate proactively calls `skip()`.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L41-48)
```text
 * @author Polytope Labs (hello@polytope.technology)
 * @notice A LayerZero V2 endpoint adapter that routes messages through Hyperbridge's ISMP
 * protocol. Existing OFTs can point to this contract as their LayerZero endpoint to use
 * Hyperbridge for cross-chain transport without code changes.
 *
 * @dev Implements `ILayerZeroEndpointV2` for OApp compatibility and `HyperApp` for ISMP
 * message handling. Assumes the same contract address on all chains (CREATE2 deployment).
 *
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L287-294)
```text
        DispatchPost memory request = DispatchPost({
            dest: dest,
            to: abi.encodePacked(address(this)),
            body: body,
            timeout: 0,
            fee: relayerFee(_params.dstEid),
            payer: address(this)
        });
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L375-382)
```text
        // Validate and advance the nonce. The nonce is committed BEFORE (and independently of)
        // OApp execution: a reverting `lzReceive` must not roll back this write. Otherwise the
        // message would be retried forever at the same nonce and every later nonce would be
        // permanently rejected, bricking the (receiver, srcEid, sender) channel.
        address receiverAddr = address(uint160(uint256(receiver)));
        uint64 expectedNonce = _inboundNonce[receiverAddr][srcEid][sender] + 1;
        if (nonce != expectedNonce) revert InvalidNonce(expectedNonce, nonce);
        _inboundNonce[receiverAddr][srcEid][sender] = nonce;
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

**File:** evm/src/core/EvmHost.sol (L805-818)
```text
        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L936-948)
```text
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
```

**File:** evm/src/core/HandlerV2.sol (L190-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```
