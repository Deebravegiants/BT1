### Title
Permanent loss of bridged principal when destination `lzReceive` delivery fails forever — no cancel/refund path exists for `HyperbridgeLzEndpoint` messages - (File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol)

### Summary
`HyperbridgeLzEndpoint` routes LayerZero V2 OApp messages (including OFT token transfers) through Hyperbridge's ISMP protocol by dispatching a `PostRequest` with `timeout: 0`, and its `onPostRequestTimeout` callback is an intentional no-op. Because the request never times out, if the destination OApp's `lzReceive` deterministically and permanently reverts (e.g., the receiving OFT is paused, the recipient is blocklisted, or the receiving contract is bricked), the sender has no way to trigger a refund or cancellation on the source chain — mirroring exactly the Linea bug class: source-side funds are burned/locked, the destination call keeps failing, and there is no cancel/refund mechanism.

### Finding Description
`send()` builds a `DispatchPost` with a hard-coded `timeout: 0` and dispatches it through `IDispatcher(_host).dispatch(request)`: [1](#0-0) 

Per ISMP convention (and as confirmed by the maintainers' own comment), `timeout: 0` means the request never expires and is never eligible for the timeout path: [2](#0-1) 

On the destination side, `onAccept` isolates the `lzReceive` call in a `try/catch`; if it fails, the payload is merely retained for retry via `retryPayload`, and delivery is never marked successful: [3](#0-2) 

`retryPayload` is permissionless but still executes the exact same call to the OApp; if the underlying failure condition (e.g., a paused/blocklisted contract) is permanent, every retry reverts forever: [4](#0-3) 

By contrast, Hyperbridge's own first-party token bridges (`HyperFungibleToken`, `WrappedHyperFungibleToken`) dispatch with a real timeout and implement `onPostRequestTimeout` to refund the sender when delivery cannot be completed: [5](#0-4) 

The LZ endpoint adapter deliberately omits this path because "LZ messages don't have a timeout concept" — but this design choice removes the only mechanism (timeout → `onPostRequestTimeout` → refund) that the rest of the protocol relies on to guarantee recoverability of locked/burned value when destination delivery permanently fails. Any OFT (ERC-20/ERC-4626, etc.) that is reconfigured to use `HyperbridgeLzEndpoint` as its LayerZero endpoint inherits this gap: its own `_lzReceive`/mint logic on the destination chain is the thing that can revert forever (e.g., destination OFT paused, cap exceeded permanently, blocklisted recipient, or a bug in the receiving OApp), while its source-side burn/lock has already executed and cannot be undone or refunded through this adapter.

### Impact Explanation
An unprivileged user or any OApp routed through this endpoint can have its principal permanently and unrecoverably locked: the source-chain burn/lock (performed by the OFT itself before calling `send()`) is irreversible, and because the ISMP message underneath is dispatched with `timeout: 0`, there is no ISMP-level timeout event that could ever trigger a source-chain refund callback. The only recourse (`retryPayload`) operates on the destination side and requires the failure condition to eventually clear — if it never clears (permanent pause, permanent blocklist, permanently reverting receiver logic, or a receiver contract that is later destroyed/self-destructed), funds are frozen forever with no cancellation path. This is a direct analog of the reported Linea bug class: "loss of bridged funds due to inability to cancel/refund when destination delivery continually fails."

### Likelihood Explanation
This requires only a normal use of the adapter (any OFT integrator sending a cross-chain transfer) plus a destination-side condition that makes `lzReceive` revert permanently — which is a realistic and not-uncommon failure mode (pausable tokens, blocklists, cap limits, contract upgrades/removals, or bugs in the receiving OApp). No adversarial actor or privileged role is needed; a normal user's funds can become permanently stuck purely due to legitimate destination-chain conditions that happen to persist.

### Recommendation
Give `HyperbridgeLzEndpoint` a genuine timeout and refund path instead of `timeout: 0` + no-op `onPostRequestTimeout`:
- Allow `send()` callers/OApps to specify (or the endpoint to enforce) a non-zero timeout for the underlying ISMP `PostRequest`.
- Implement `onPostRequestTimeout` to notify/refund the OApp (or expose a callback so the OFT can re-mint/unlock on the source chain), mirroring the pattern used in `HyperFungibleToken.onPostRequestTimeout`.
- Alternatively, if LayerZero semantics require infinite retries, document prominently that OFTs integrating via this adapter must implement their own recovery/circuit-breaker to avoid depending on an ISMP timeout that will never fire, and provide a permissioned/DAO-level "force resolve" mechanism as a last resort for permanently stuck payloads.

### Proof of Concept
1. An OFT `X` is configured to use `HyperbridgeLzEndpoint` as its LayerZero endpoint on chain A (source) and chain B (destination).
2. User calls `X.send(...)` on chain A; `X` burns/locks the user's tokens and calls `HyperbridgeLzEndpoint.send()`, which dispatches a `PostRequest` with `timeout: 0` (`sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol:287-306`).
3. On chain B, the relayer submits the message; `onAccept` calls `ILayerZeroReceiver(X).lzReceive(...)`. Suppose `X` on chain B is paused (or its receive logic permanently reverts for this recipient).
4. The call reverts, is caught, and the payload hash is stored for retry (`onAccept`, lines 384-396). No tokens are minted on chain B.
5. Anyone calls `retryPayload` repeatedly — every call reverts because the underlying condition (pause/blocklist/bug) is permanent.
6. Because the original ISMP request was dispatched with `timeout: 0`, it can never be timed out via `dispatchTimeOut`/`handlePostRequestTimeouts` on chain A, and `onPostRequestTimeout` is a no-op anyway (`HyperbridgeLzEndpoint.sol:403`), so there is no way to recover the burned/locked tokens on chain A. The user's principal is permanently lost.

### Citations

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L287-306)
```text
        DispatchPost memory request = DispatchPost({
            dest: dest,
            to: abi.encodePacked(address(this)),
            body: body,
            timeout: 0,
            fee: relayerFee(_params.dstEid),
            payer: address(this)
        });

        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L384-396)
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
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L398-403)
```text
    /**
     * @notice Handles ISMP request timeouts
     * @dev LZ messages don't have a timeout concept — messages are retried, not expired.
     * This is a no-op since we dispatch with timeout=0 (no expiry).
     */
    function onPostRequestTimeout(PostRequestTimeout memory) external override onlyHost {}
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L315-326)
```text
    /**
     * @notice Handles timeout of a previously dispatched cross-chain transfer
     * @dev Called by the ISMP host when a sent message times out without being delivered.
     * Re-mints the burned tokens back to the original sender as a refund.
     * @param incoming The timed-out POST request and the relayer that submitted the timeout proof
     */
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
