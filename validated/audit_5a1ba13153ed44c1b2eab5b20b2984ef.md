Based on my investigation, I found a valid analog. The Intent Gateway (`ExtrinsicIntents.sol` / `IntentGatewayV2.sol`) implements an app-level "authorized relayer" gate that restricts which relayer address may deliver the ISMP messages that release escrowed user/solver funds. This mirrors the "malicious Rebalancer" pattern: a narrowly-scoped operational role, once designated, becomes the sole gatekeeper for fund release, with no permissionless fallback if it goes rogue or unresponsive.

### Title
Single-relayer gate on `onAccept`/`onGetResponse` lets a designated relayer permanently freeze escrowed order funds - (File: `evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`IntentsBase` stores a single `_relayer` address that, once set (non-zero), becomes the only address whose ISMP message delivery `onAccept`/`onGetResponse` will honor for `RedeemEscrow`, `RefundEscrow`, and governance actions [1](#0-0) . This is analogous to the reported `Rebalancer` pattern: a distinct, narrowly-scoped operational role (not the core admin) whose inaction can permanently block fund redemption for unprivileged users (order placers and solvers), because there is no fallback path once the gate is armed.

### Finding Description
`onAccept` on the destination/source gateway checks `_checkRelayer(incoming.relayer)` before processing `RedeemEscrow` or `RefundEscrow` bodies that release escrowed tokens to a solver or refund a user [2](#0-1) . Tests confirm that once a relayer is configured, deliveries by any other relayer address revert with `Unauthorized`, and only the exact configured relayer's delivery is accepted [3](#0-2) . By contrast, when `_relayer == address(0)` the gate is "open" and any relayer can deliver [4](#0-3) .

At the core protocol level (`EvmHost`/`HandlerV2`), ISMP message delivery is permissionless — any relayer can submit a proof and deliver a request. The app-layer `_relayer` gate in the Intent Gateway overrides this permissionless design by requiring one specific address for the actual fund-releasing calls. Just as the Rebalancer in the original report is a distinct role from the protocol owner/admin whose day-to-day inaction (not calling `requestWithdrawal`) can block redemption even though the admin cannot be blamed for malicious governance per se, here the designated `_relayer` is a distinct operational identity from Hyperbridge governance itself: governance only rotates it via the `Execute`/`setRelayer` path, but once rotated to a given address, that address's own behavior (going offline, being compromised, or refusing to relay) is what actually determines whether `RedeemEscrow`/`RefundEscrow` messages ever land.

### Impact Explanation
If the configured relayer becomes unavailable, is compromised, or simply refuses to submit the specific `RedeemEscrow`/`RefundEscrow` delivery transactions, solvers can never collect the input tokens they are owed for filling cross-chain orders, and users can never receive refunds from cancelled cross-chain orders — even though the underlying Hyperbridge message has already been finalized and is otherwise deliverable by any of the many independent relayers in the network. This is a permanent freezing of escrowed funds analogous to PT/YT holders being unable to redeem because the Rebalancer withholds `requestWithdrawal`.

### Likelihood Explanation
This requires governance to have configured a non-zero `_relayer` (an expected operational configuration, not a misconfiguration) and for that specific relayer to become unresponsive or malicious. Given that a single relayer address is a chokepoint with no automatic recovery/permissionless fallback (unlike the destination-side order cancellation which explicitly becomes permissionless after the deadline), this is a plausible operational risk once the intended relayer restriction is active in production.

### Recommendation
Add a timeout/fallback mechanism so that after a grace period, delivery of `RedeemEscrow`/`RefundEscrow` messages becomes permissionless (similar to how `_cancelFromDest` already allows "anyone" to trigger cancellation after the order deadline). Alternatively, support multiple authorized relayers or an emergency governance path to reopen the gate (`setRelayer(address(0))`) without requiring the compromised/unresponsive relayer's cooperation, ensuring escrowed funds are never wholly dependent on a single relayer's liveness.

### Proof of Concept
1. Governance configures `_relayer` to address `R` via the `Execute`/`setRelayer` path (host-only, reachable only through Hyperbridge governance dispatch) — see `RequestKind.Execute` comment describing `setRelayer` reachability [5](#0-4) .
2. A user places a cross-chain order and a solver fills it on the destination chain; the destination gateway dispatches a `RedeemEscrow` POST back to the source chain.
3. The message is finalized on Hyperbridge and deliverable by any relayer at the ISMP-core level, but `onAccept`'s `_checkRelayer(incoming.relayer)` (as exercised in `testOnAcceptRejectsUnlistedRelayer`) reverts with `Unauthorized` for every relayer except `R` [3](#0-2) .
4. If `R` refuses (or is unable) to submit the delivery transaction, the escrowed input tokens remain locked in `_orders[commitment][token]` indefinitely, and the solver can never claim payment — mirroring the "Rebalancer never calls `requestWithdrawal`" freeze pattern from the original report.

**Note on uncertainty:** I could not locate the exact `_checkRelayer` implementation body or the `setRelayer` function definition within the indexed context (only references/usages were surfaced), so I cannot fully confirm whether there is any additional recovery mechanism (e.g., a timeout) built into `_checkRelayer` itself. If the user wants full verification of `_checkRelayer`'s logic and any built-in recovery path, a Devin session with full repository access should inspect `evm/src/apps/intentsv2/ExtrinsicIntents.sol` and `evm/src/apps/IntentGatewayV2.sol` in full.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L112-119)
```text
        /**
         * @dev Delegatecall the current implementation with the rest of the body as calldata, the
         * host still `msg.sender`. Governance's one door to the host-only functions:
         * `upgradeToAndCall` for upgrades, `setRelayer` for rotations. Same discriminator as the
         * `UpgradeContract` action of earlier implementations, whose `(address, bytes)` body
         * selects no function here and reverts.
         */
        Execute
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L168-173)
```text
    /**
     * @dev Once set, the only relayer whose deliveries `onAccept` and `onGetResponse` accept.
     * Read through `relayer()`; an auto-generated getter on top of that would not fit under
     * EIP-170.
     */
    address internal _relayer;
```

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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4447-4459)
```text
    function testSetRelayerToZeroReopensTheGate() public {
        (PostRequest memory request,, uint256 amount) = _escrowedRedeemRequest();
        vm.prank(address(host));
        intentGateway.setRelayer(address(0));
        assertEq(intentGateway.relayer(), address(0));
        assertEq(intentGateway.version(), 2, "reopening the gate is not a migration either");

        // With no relayer set the gate is open, so a delivery from anyone lands.
        uint256 before = usdc.balanceOf(filler);
        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: request}));
        assertEq(usdc.balanceOf(filler) - before, amount, "open gate releases escrow");
    }
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
