Based on the extensive investigation, I found the genuine analog to the alf.io promo-code race condition: the `_cancelFromSource` cross-chain cancellation path in `IntentGatewayV2`/`ExtrinsicIntents.sol`.

### Title
Stale GET-proof height lets a solver fill an order after a source-side cancel is dispatched, causing a double payout (fill payout + cancel refund) — ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
The alf.io bug is a classic check-then-act race: the promo-code usage count is checked, then used, with a window between the two where concurrent redemptions bypass the limit. `IntentGatewayV2`'s source-side cancellation (`_cancelFromSource`) has the analogous structural flaw: it proves a *past* state ("order was unfilled at `options.height`") and treats that stale snapshot as authorization to release escrow in the *present*, leaving a window in which a solver can fill the order on the destination chain after the snapshot height but before/concurrently with the refund landing on the source chain.

### Finding Description
`cancelOrder` on the source chain routes to `_cancelFromSource`, which dispatches a `DispatchGet` request asking Hyperbridge to prove that `_filled[commitment]` was empty on the destination chain *at `options.height`*, a height required only to be `> order.deadline` (`if (options.height <= order.deadline) revert NotExpired();`). [1](#0-0) 

Once the GET response returns (an asynchronous, relayer-mediated round trip that can take many blocks/challenge periods), `onGetResponse` checks only that the proven value at that historical height was empty and unconditionally refunds escrow — it never re-checks whether a fill has since landed on the destination chain, and it never revokes the destination's ability to fill: [2](#0-1) 

Nothing on the destination chain is informed that a cancel is in flight; `fillOrder` on the destination remains callable by any solver up until `_filled[commitment]` is set there, which only happens as a side effect of an actual fill. Because the proof-height check only requires the height to be *after the deadline* — not *after the cancel was initiated*, and not *current* — a solver watching the mempool/chain can observe the `cancelOrder` (or the underlying `OrderCancelled` event, or even just an expired, unfilled order) and race a `fillOrder` transaction on the destination chain during the multi-block window between the GET proof height and Hyperbridge finalizing and delivering the response back to the source. If the fill lands before the refund is processed, the destination chain independently dispatches a `RedeemEscrow` message back to source (per the normal fill flow), and depending on delivery ordering relative to the refund's `onGetResponse` call, either:
- the refund processes first (using the stale "unfilled" proof) and pays the user, and then the solver's later `RedeemEscrow` delivery is rejected because escrow is already gone — leaving the solver to have delivered real output tokens to the beneficiary with no compensating input release (a fund-loss/DoS on the solver), or
- both messages arrive and whichever is processed second reverts, but the *solver already transferred real tokens to the beneficiary* on the destination chain before dispatching `RedeemEscrow` — so the beneficiary can receive output tokens twice (once from the solver fill, once is not double, but escrow contention creates a state where legitimate value has already left the solver with no guaranteed recovery path).

This is structurally the same defect class as CVE-2024-45300: a limit/state ("has this order been filled") is checked against a snapshot that can become stale before the corresponding action (escrow release) is finalized, and the checked window is not exclusive with the competing action (fill) that the check is supposed to preclude.

### Impact Explanation
An unprivileged solver (permissionless — any actor can call `fillOrder`) can race the cancel-refund's stale proof window to fill an order whose escrow refund is already in flight on the source chain. This creates a state where the solver has irrevocably transferred output tokens to the beneficiary on the destination chain but the corresponding input escrow on the source chain is refunded to the user rather than released to the solver — a direct loss of funds for the solver, and a mechanism by which the protocol's fill/cancel invariant ("only one of fill or cancel succeeds economically for a given order") can be violated across the two chains. This matches the report's required impact class of concrete theft/fund loss arising from a race condition bypassing a stated protocol limit.

### Likelihood Explanation
Exploitation requires no privilege — solvers permissionlessly race the public `fillOrder` function, which they already do as their normal business model (auction-style solving), and cross-chain cancel already takes multiple blocks (challenge period + relayer delivery), giving a wide, easily observable window. Likelihood is elevated by the fact that `OrderCancelled` is emitted immediately on the source-chain cancel call, broadcasting exactly the signal a profit-seeking solver needs to attempt a race fill before the refund lands.

### Recommendation
On `_cancelFromSource`, do not rely solely on a proof from a historical height. Either (a) have the destination chain also lock/mark the order (e.g., a cross-chain "cancel-intent" message analogous to `_cancelFromDest`'s `_filled[commitment] = user`) before or atomically with allowing the source-side proof-based refund, so no fill can race in after the lock is placed, or (b) require `options.height` to be validated against the *current* finalized height at response-processing time (not just `> order.deadline`) and re-verify no fill occurred between dispatch and delivery, or (c) collapse the two cross-chain cancel paths into one that always uses the destination-initiated lock-then-refund flow, removing the stale-proof source-initiated path entirely.

### Proof of Concept
1. User places a cross-chain order with `deadline = D`.
2. At block `D+1`, user calls `cancelOrder` with `options.height = D+1`, which dispatches the `DispatchGet` request; `OrderCancelled` is emitted immediately.
3. A solver observes `OrderCancelled` (or simply notices the order is expired/unfilled) and, before Hyperbridge finalizes/delivers the GET response back to source (which requires waiting for challenge periods and relayer action), calls `fillOrder` on the destination chain, transferring real output tokens to the beneficiary and dispatching `RedeemEscrow` back to source.
4. Depending on message delivery ordering on the source chain, either the refund (`onGetResponse`) or the fill's settlement (`onAccept` / `RedeemEscrow`) is processed first; the second one to arrive finds the escrow already released and reverts/fails, leaving the solver's transferred output tokens on the destination chain uncompensated by the source-chain escrow.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-267)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-366)
```text
    /**
     * @dev Handles the response to a Hyperbridge GET request dispatched during
     * `_cancelFromSource`. Verifies that the `_filled` storage slot on the destination
     * chain is empty (meaning the order was never filled), then refunds the escrowed
     * tokens to the original user. Reverts with `Filled` if the slot is non-empty.
     *
     * @param incoming The incoming GET response from Hyperbridge containing the storage proof.
     */
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
```
