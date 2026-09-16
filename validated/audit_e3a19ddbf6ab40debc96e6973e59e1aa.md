## Title
Paused or blacklisted collateral tokens permanently block order cancellation/refund in the Intent Gateway - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase._withdraw`, the single internal function used by every escrow-release path in the Intent Gateway (same-chain cancel, cross-chain source-side cancel via GET response, cross-chain destination-side cancel via `RefundEscrow`, and normal fill settlement via `RedeemEscrow`), performs an unguarded `IERC20(token).safeTransfer(beneficiary, amount)` with no fallback or claim mechanism. If the escrowed input token reverts on transfer to the beneficiary (e.g. it is a pausable stablecoin like USDC that is globally paused, or the beneficiary address is blacklisted), the entire withdrawal reverts, and there is no alternate code path to ever release the escrowed funds to that beneficiary.

### Finding Description
`_withdraw` is the common escrow-release routine: [1](#0-0) 

It is called by:
- `_cancelSameChain` for same-chain cancellations, in the same transaction as the cancel [2](#0-1) 
- `onAccept` handling `RefundEscrow` after a destination-initiated cross-chain cancel, and `RedeemEscrow` after a normal fill settlement [3](#0-2) 
- `onGetResponse` for source-initiated cross-chain cancellations, once Hyperbridge proves the order was unfilled

Critically, for the destination-initiated cross-chain cancel route, `_cancelFromDest` **irrevocably marks the order settled on the destination chain before the refund is guaranteed to succeed on the source chain**: [4](#0-3) 

Once `_filled[commitment]` is set on the destination, the order can never be filled by a solver again, and the *only* remaining path to release the user's escrowed input is the `RefundEscrow` message hitting `_withdraw` on the source chain. If `order.user`'s token transfer reverts there (paused token, or a blacklisted `order.user` address in the case of USDC-style tokens), the message delivery reverts and can never succeed — because the beneficiary is hardcoded to `order.user` and cannot be redirected:

> "The caller pays the dispatch cost, but cannot change `WithdrawalRequest.beneficiary`: the refund always goes to `order.user`." (`docs/content/developers/evm/intent-gateway/cancelling-orders.mdx`)

The same unconditional-transfer pattern also blocks the same-chain cancel path (`_cancelSameChain`) and the source-side proof-based cancel path (`onGetResponse`), and even normal escrow release to a solver (`RedeemEscrow`) if the solver's/beneficiary's receiving address is frozen by the token issuer.

This directly mirrors the GMX finding: canceling/refunding an order requires successfully sending back the underlying collateral token in the same call that finalizes the cancellation, with no separate "claim" mechanism to fall back on if that transfer reverts.

### Impact Explanation
Unlike the GMX case (temporary price-look-ahead griefing), the consequence here is stronger: **permanent freezing of user funds**. For the destination-initiated cross-chain cancel, once the destination chain commits to cancelling the order (`_filled[commitment] = user`), there is no other code path that can ever release the escrowed input tokens if the source-side transfer to `order.user` keeps reverting (blacklist is typically permanent, and even a temporary pause could last long enough to matter, but blacklist specifically cannot self-resolve). The user's escrow is stuck in the source-chain gateway contract indefinitely, since:
- The order cannot be filled anymore (already marked settled on destination).
- The refund can never complete (the beneficiary token transfer always reverts).
- No governance or "claim" function exists to redirect the stuck balance.

Even for the same-chain and source-proof cancel paths, funds remain locked in escrow for as long as the token remains paused (or forever if the transfer is blocked by a durable cause), with no ability to recover them via an alternate address.

### Likelihood Explanation
Pausable/blacklistable stablecoins (e.g., USDC, USDT) are explicitly expected input assets for this protocol per its own tests (`usdc` is the primary test token throughout `IntentGatewayV2Test.sol`/`IntentGatewayV2SameChainTest.sol`). A user's own address being blacklisted by the token issuer (for reasons unrelated to this protocol) is a realistic, externally-triggerable event, and a global token pause is a standard incident-response mechanism these tokens' issuers actually use. No attacker action is even required — an ordinary compliance event on the token side is sufficient to trigger permanent fund lock for any user with an order in flight, particularly on the destination-initiated cancel route where the point of no return is crossed before the refund is confirmed.

### Recommendation
Do not perform the final token transfer to the beneficiary as an atomic, blocking part of order settlement/cancellation finalization. Options:
- Decouple "mark order settled/cancelled" from "transfer tokens": credit an internal claimable balance for the beneficiary and expose a separate `claim()`/`withdrawable()` function that can be retried independently and does not block state transitions of the order itself.
- At minimum, wrap `_withdraw`'s external token transfer in a try/catch (or use a pull-based escrow, e.g. an internal balance mapping) so that a reverting transfer degrades to "funds claimable later" instead of reverting the whole settlement, especially for the `_cancelFromDest` → `RefundEscrow` path where the destination-side state change (`_filled[commitment] = user`) is already irreversible.

### Proof of Concept
1. User places a same-chain (or cross-chain) order using USDC as `order.inputs[0].token`, escrowing funds in the Intent Gateway (`IntrinsicIntents`/`ExtrinsicIntents`).
2. Circle blacklists `order.user`'s address (or pauses USDC globally) before the order is filled.
3. User (or, after the deadline, any relayer) calls `cancelOrder`:
   - Same-chain: `_cancelSameChain` → `_withdraw` → `IERC20(usdc).safeTransfer(user, amount)` reverts because `user` is blacklisted; the whole cancel transaction reverts, and there is no other way to retrieve the escrow.
   - Cross-chain from destination: `_cancelFromDest` sets `_filled[commitment] = user` on the destination chain and dispatches `RefundEscrow` to the source chain. The order can no longer be filled. When the `RefundEscrow` message is delivered on the source chain, `onAccept` → `_withdraw` → `safeTransfer(user, amount)` reverts every time it is retried, because the beneficiary is hardcoded to the blacklisted `order.user`. The escrowed USDC is now permanently stuck in the `IntentGatewayV2` contract on the source chain with no recovery path. [1](#0-0) [4](#0-3)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L309-330)
```text
    /**
     * @dev Handles incoming cross-chain post requests dispatched via Hyperbridge.
     * The first byte of the request body encodes the `RequestKind`, which determines
     * the action to take:
     *
     * - RedeemEscrow: Releases escrowed tokens to the solver who filled the order
     *   on the destination chain. Authenticated against the registered gateway instance.
     * - RefundEscrow: Refunds escrowed tokens to the original user after a successful
     *   cancellation from the destination chain. Authenticated against the registered gateway.
     * - NewDeployment: Registers a new gateway instance for a state machine. Only
     *   Hyperbridge itself may dispatch this request.
     * - UpdateParams: Updates the gateway's configuration parameters and per-destination
     *   protocol fees. Only Hyperbridge may dispatch this request.
     * - SweepDust: Transfers accumulated protocol dust to a specified beneficiary.
     *   Only Hyperbridge may dispatch this request.
     * - Execute: Delegatecalls the current implementation with the rest of the body, the host
     *   still `msg.sender`, so the host-only functions (`upgradeToAndCall`, `setRelayer`) are
     *   reachable. Reverts bubble up unchanged. Only Hyperbridge may dispatch this request.
     *
     * @param incoming The incoming post request from Hyperbridge.
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
```
