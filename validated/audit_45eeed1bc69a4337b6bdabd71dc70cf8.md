## Analog Found: Blacklisted/reverting beneficiary permanently locks an entire order's escrow in `IntentGateway`

### Title
Single failing token transfer to a fixed, non-substitutable beneficiary permanently locks all escrowed assets of an order - (`evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2`'s escrow settlement/refund path (`_withdraw`, called from `RedeemEscrow`/`RefundEscrow` `onAccept` handling, `onGetResponse`, and `_cancelSameChain`) transfers every escrowed token for an order commitment to a single, fixed beneficiary in one atomic loop. If the beneficiary is or becomes unable to receive even one of the tokens (e.g., a USDC blacklist, or any ERC-20 with transfer restrictions/reverting hooks), the whole withdrawal reverts, and since the beneficiary address baked into the order/commitment cannot be changed, every subsequent retry fails identically — permanently freezing the entire escrow, including unrelated tokens.

### Finding Description
`_withdraw` iterates over `body.tokens` and unconditionally calls `IERC20(token).safeTransfer(beneficiary, amount)` (or `_sendValue` for native) for each token, all within one atomic call: [1](#0-0) 

This function is the terminal step for both settlement and refund paths:
- Cross-chain fill settlement (`RedeemEscrow`, beneficiary = the solver who filled the order) and cross-chain cancellation (`RefundEscrow`, beneficiary = `order.user`) both route through it from `onAccept`: [2](#0-1) 
- Source-side cancellation via `onGetResponse` also calls it after verifying the destination proof: [3](#0-2) 
- Same-chain cancellation (`_cancelSameChain`) calls it directly, refunding *all* remaining escrowed tokens for the commitment in one call: [4](#0-3) 

In every case the beneficiary is fixed by the order/commitment (`order.user` for refunds, or the filler's address captured at fill time for redemptions) and cannot be redirected. If any single token in `body.tokens` reverts on transfer to that beneficiary — most plausibly because the beneficiary is blacklisted on a compliance-gated token like USDC — the entire `_withdraw` call reverts. Because the loop is atomic, this also blocks release of every *other*, unaffected token escrowed under the same commitment (an order can escrow multiple `TokenInfo` entries).

`EvmHost.dispatchIncoming` does delete the request receipt on a failed `onAccept`/`onGetResponse` call so the message "can be retried" by a relayer: [5](#0-4)  — but retrying re-delivers the identical `WithdrawalRequest` with the same fixed beneficiary, so a *permanent* condition (an irreversible blacklist) causes every retry to fail identically forever. There is no per-token independent redemption path, and no rescue mechanism that lets the order's principal be redirected to a different address; the only sweep functionality in the codebase (`SweepDust`/`_sweepDust`) is scoped to protocol-collected dust/fees, not order escrow.

This is the direct analog of the Stream.sol issue: a single reverting transfer to one party, embedded in a combined atomic settlement, blocks recovery of funds that rightfully belong to (or should be releasable for) other, unaffected parties/tokens, with no independent recovery path.

### Impact Explanation
Any order escrowing a compliance-gated token (e.g. USDC) where the beneficiary (user on refund, or solver on redemption) is or becomes blacklisted permanently traps that order's entire escrow — including any other, non-blacklisted tokens bundled in the same order — inside `IntentGatewayV2`/`IntentsBase`. Neither the user, the solver, nor governance has any way to redirect the stuck beneficiary or redeem the unaffected legs separately. This is a permanent freezing of user/solver funds, which is High severity given intent-gateway orders can escrow significant value across multiple tokens per commitment.

### Likelihood Explanation
Reachable by any user placing a cross-chain or same-chain order with a multi-token input, or any solver filling one, without any privileged action required. USDC blacklisting is a real, exercised mechanism (Tornado Cash sanctions precedent), and a malicious actor (either the order's own user seeking to grief a solver, or a solver griefing a user) could deliberately get their own beneficiary address blacklisted after escrow is created but before settlement/refund, guaranteeing the revert path is hit. Likelihood is moderate-to-high given it requires an external blacklist event, but the attack is realistic and has historical precedent, and once triggered the lock is unconditional and irreversible via existing contract logic.

### Recommendation
Change `_withdraw` to not perform a single all-or-nothing atomic transfer over the full token list to one fixed beneficiary. Options:
- Track per-token, per-commitment claimable balances and expose a separate `claim(commitment, token)` function so a single blocked token cannot block redemption of the others.
- Wrap each individual token transfer in a try/catch; on failure, retain the escrow accounting for that token (do not decrement it) and let it be reclaimed by an alternate mechanism (e.g., a permissioned re-route to a different address, or a pull-based claim by the intended beneficiary once unblocked), while still releasing the unaffected tokens and finalizing the rest of the order state.
- Allow governance or the original beneficiary to designate a substitute payout address if the primary one becomes permanently unable to receive a specific token.

### Proof of Concept
1. User places a same-chain order escrowing both USDC and DAI as `inputs` (a single commitment can hold multiple `TokenInfo` entries).
2. Before the order is filled or cancelled, the user's own address (or the solver who later fills it) is added to the USDC blacklist (e.g., by interacting with a sanctioned contract).
3. User calls `cancelOrder` → `_cancelSameChain` → `_withdraw` (`evm/src/apps/intentsv2/IntrinsicIntents.sol:159-180`, `evm/src/apps/intentsv2/IntentsBase.sol:451-470`): the loop reaches the USDC leg, `IERC20(usdc).safeTransfer(beneficiary, amount)` reverts because the beneficiary is blacklisted, and the entire `_withdraw` call reverts — including the DAI leg that would otherwise have succeeded.
4. Every subsequent `cancelOrder` call fails identically since the beneficiary (`order.user`) is fixed and permanently blacklisted; both the USDC and DAI escrow remain locked in the gateway with no alternate recovery function.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L352-360)
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

**File:** evm/src/core/EvmHost.sol (L811-818)
```text

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```
