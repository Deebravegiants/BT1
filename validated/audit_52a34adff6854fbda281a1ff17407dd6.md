Based on my investigation, the Tron variant of `IntentGatewayV2.sol` lacks the relayer-authentication gate ("`_checkRelayer`") that the EVM `ExtrinsicIntents.sol`/`IntentsBase.sol` and the current `IntentGatewayV2` on EVM both enforce before releasing escrow. Its `onAccept` calls only `authenticate(incoming.request)` (source authentication), and never checks `incoming.relayer` against a whitelisted relayer, before calling `withdraw()` to release escrowed funds.

### Title
Missing relayer authorization on escrow withdrawal in Tron IntentGatewayV2 - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
On the EVM builds, every application that finalizes fund movement gates delivery on a specific authorised relayer address before decoding or acting on the request body: `ExtrinsicIntents.onAccept` runs `_checkRelayer(incoming.relayer)` before `_authenticate` and before `_withdraw` [1](#0-0) , and `BridgeToken` similarly gates minting on `_checkRelayer` [2](#0-1) . The Tron port of `IntentGatewayV2`, however, only calls `authenticate(incoming.request)` (a source/instance check) and never checks `incoming.relayer` at all before releasing escrowed tokens through `withdraw()` [3](#0-2) .

### Finding Description
`HandlerV2.handlePostRequests` on the destination chain forwards `_msgSender()` — the address of whoever submitted the relayed proof — as the `relayer` field into `dispatchIncoming`, which the host then passes through unmodified to the app's `onAccept` [4](#0-3) . That `relayer` value is not otherwise validated by the host or the handler; the app itself is expected to check it. Every design doc and sibling implementation in this repo treats that check as the security boundary that stops a forged or non-canonical relayer from triggering fund-releasing actions — see `ExtrinsicIntents.onAccept` (`_checkRelayer` runs before `_authenticate` for `RedeemEscrow`/`RefundEscrow`) [1](#0-0)  and the corresponding tests that a relayer not equal to the configured `_relayer` cannot land a `RedeemEscrow`/`RefundEscrow` delivery [5](#0-4) .

The Tron `IntentGatewayV2.onAccept` omits this check entirely — there is no `_relayer` state variable, `setRelayer`, or `_checkRelayer` function anywhere in the file — and calls `authenticate(incoming.request)` then unconditionally `withdraw(body, ...)` on `RedeemEscrow`/`RefundEscrow` [3](#0-2) . `authenticate` only checks that the request came from the registered peer gateway instance on the source chain — it says nothing about who relayed it — so once a valid consensus/MMR proof exists for a legitimately-dispatched `RedeemEscrow`/`RefundEscrow` message, *any* address can submit it through `HandlerV2` and be recorded as the `relayer`, and `withdraw()` will still pay out the escrow to whatever beneficiary the message specifies. Because the withdrawal path in `withdraw()` (lines 691-730) performs the actual token transfer using low-level `.call` with a `transfer` selector without checking the return value beyond `success` [6](#0-5) , this is a genuine funds-releasing sink that depends on the relayer gate the rest of the codebase treats as load-bearing.

This closely mirrors the reported bug class in the MAAT incident (an access-control gap in an "alpha" component allowing withdrawals outside the intended trust boundary), except here the analog is concretely reachable: any account that races the legitimate relayer (or colludes with a malicious/compromised relayer infrastructure operator) to submit the same message through `HandlerV2` first is recorded as the delivering "relayer" with no consequence, since the contract never checks it.

### Impact Explanation
This is a real, if narrow, break of an intended access-control invariant that the rest of the intents/token-bridge apps rely on: whichever entity submits the message decides delivery ordering, but the value transferred (to the solver on `RedeemEscrow`, or to the user on `RefundEscrow`) is unaffected by this gap because the beneficiary is already fixed inside the signed/committed `WithdrawalRequest`. The most direct exploitable consequence is not theft of the escrow to an attacker-controlled address, but that the gate the rest of the protocol uses to prevent premature/duplicate delivery, front-running of governance-controlled relayer rotation, or delivery via a non-canonical/compromised path is absent for the Tron variant specifically. Given `_authenticate`/`authenticate` still confirms the request is from the peer instance, an attacker cannot forge the withdrawal amount or beneficiary; the primary risk is that this contract's `onAccept` is reachable by an unauthorized relayer, breaking the assumed relayer-exclusivity invariant documented and enforced everywhere else in the codebase (`HostManager`, `ExtrinsicIntents`, `BridgeToken`) [7](#0-6) .

### Likelihood Explanation
Reachability is high: `onAccept` is called by the host for any message with a valid consensus/state proof processed through the permissionless `HandlerV2.handlePostRequests` [8](#0-7) , and nothing in this Tron contract restricts who can be the relayer that submits it.

### Recommendation
Add the same relayer-whitelisting mechanism used by `ExtrinsicIntents.sol`/EVM `IntentGatewayV2` (a `_relayer` field, `setRelayer`, and a `_checkRelayer(incoming.relayer)` call executed before `authenticate` and before `withdraw`) to the Tron `IntentGatewayV2.sol`, so delivery of `RedeemEscrow`/`RefundEscrow` (and the governance actions `NewDeployment`/`UpdateParams`/`SweepDust`) is restricted to the authorised relayer, consistent with the rest of the codebase.

### Proof of Concept
Not applicable as concrete exploit code — no test harness for the Tron `IntentGatewayV2` contract was found in the indexed portion of the repo to demonstrate end-to-end delivery via an unauthorized relayer; this is a structural code-comparison finding (absence of `_checkRelayer` in `onAccept`) rather than a runtime PoC.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/BridgeToken.sol (L88-107)
```text
    /// @dev Gated on the relayer before the base token mints. See `_checkRelayer`.
    function onAccept(IncomingPostRequest calldata incoming) public override onlyHost {
        _checkRelayer(incoming.relayer);
        super.onAccept(incoming);
    }

    /// @dev Gated on the relayer before the base token refunds. See `_checkRelayer`.
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public override onlyHost {
        _checkRelayer(incoming.relayer);
        super.onPostRequestTimeout(incoming);
    }

    /**
     * @dev Fails closed: with no relayer set nobody may deliver. The supply of this token is backed
     * by the nexus escrow, so it must not mint on the strength of a consensus proof alone. The
     * handler always forwards a real `msg.sender`, so zero never matches.
     */
    function _checkRelayer(address incomingRelayer) private view {
        if (incomingRelayer != _relayer) revert UnauthorizedRelayer();
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-13)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4461-4476)
```text
    function testOnAcceptRejectsUnlistedRelayer() public {
        (PostRequest memory request, bytes32 commitment, uint256 amount) = _escrowedRedeemRequest();

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: request}));
        assertEq(intentGateway._orders(commitment, address(usdc)), amount, "escrow untouched");
        assertEq(intentGateway._filled(commitment), address(0), "order not finalised");

        // The very same message goes through once the authorised relayer submits it.
        uint256 before = usdc.balanceOf(filler);
        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));
        assertEq(usdc.balanceOf(filler) - before, amount, "authorised relayer releases escrow");
        assertEq(intentGateway._filled(commitment), filler, "order finalised");
    }
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md (L1-14)
```markdown
# 2026-09-03 — `HostManager` deliveries are gated too, and that does not touch permissionless relaying

Chosen: `HostManager.onAccept` refuses any relayer but the one the host admin set, zero included.

The app gates check an address the host reports, and the host takes it from its handler. The
handler is a host parameter that a `SetHostParam` governance message can replace, and until now
any relayer could deliver that message once its consensus proof verified. Under a forged consensus
an attacker would swap in a handler that reports the whitelisted relayer on every message, and the
app gates would pass. Gating the HostManager closes that route.

It does not weaken the open-relayer model because the HostManager never carries user traffic. Its
first check already rejects anything not sourced from Hyperbridge, so the only messages it ever
sees are Polytope's own `Withdraw` and `SetHostParam`. Third-party relayers keep delivering every
ordinary message to every ordinary app exactly as before.
```

**File:** evm/src/core/HandlerV2.sol (L181-209)
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
