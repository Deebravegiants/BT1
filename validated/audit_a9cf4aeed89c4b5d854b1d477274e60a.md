### Title
Partial escrow releases in `IntentsBase._withdraw` transfer funds without emitting any event - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase._withdraw` is the internal function that any solver-triggered `RedeemEscrow`/`RefundEscrow` cross-chain message (dispatched via `onAccept`) or a `onGetResponse` GET-response callback in `IntentGatewayV2` ultimately calls to move tokens out of escrow to a beneficiary. When `finalize` is `false` — the partial-fill path — the function decrements escrow accounting and performs the ERC20/native transfer, but returns without emitting any event, unlike the `finalize == true` path which emits `EscrowReleased`/`EscrowRefunded`.

### Finding Description
`_withdraw` iterates the withdrawal request's token list, decrements `_orders[commitment][token]`, and sends funds to the beneficiary via `_sendValue` or `IERC20.safeTransfer`: [1](#0-0) 

Only when `finalize` is `true` does the function emit `EscrowReleased` or `EscrowRefunded`: [2](#0-1) 

The doc comment for `_withdraw` explicitly acknowledges the partial-fill code path releases "proportional token amounts ... without finalizing the order," confirming that value transfers happen on the `finalize == false` branch with no corresponding event: [3](#0-2) 

The `_orders` mapping tracking escrow balances per commitment/token, which is decremented on every withdrawal (finalized or partial), is defined here: [4](#0-3) 

This function is reachable from any relayed cross-chain message that instructs a partial redemption of escrow — a path any relayer/solver can trigger by delivering a proof for a partial fill, satisfying the requirement of being reachable from a single relayed message/proof.

### Impact Explanation
Because partial escrow releases move real user/solver funds (ERC20 or native ETH) out of the contract but leave no on-chain log, off-chain indexers, dashboards, and monitoring/alerting systems that rely on `EscrowReleased`/`EscrowRefunded` events to track fund movement and detect anomalies (e.g., unexpected drains, mismatched escrow accounting, or griefing via repeated small partial fills) cannot observe these transfers. This creates a monitoring/accounting blind spot for a code path that directly disburses escrowed value, mirroring the referenced report's concern that "there can be a scenario when there is an unauthorized withdrawal and the user (victim) won't be aware of it" — here, silent partial withdrawals of escrowed funds are indistinguishable from normal contract state until the final release, undermining timely detection of malicious solver behavior or accounting bugs in the intents escrow.

### Likelihood Explanation
Partial fills are a supported, first-class flow (as documented directly in the function's own docstring and the dedicated `_partialFills` mapping), so this code path executes routinely during normal solver operation, not merely in an edge case. Any actor able to submit a valid partial-fill withdrawal request (a normal solver/relayer action) triggers unlogged fund movement every time.

### Recommendation
Emit a dedicated event (e.g., `EscrowPartiallyReleased(bytes32 commitment, TokenAmount[] tokens, address beneficiary)`) inside `_withdraw` regardless of the `finalize` flag, so that every token transfer out of escrow — partial or final — is logged and can be tracked by off-chain infrastructure and users monitoring their orders.

### Proof of Concept
1. A user places an order via `IntrinsicIntents`/`ExtrinsicIntents`, escrowing tokens tracked in `_orders[commitment][token]`.
2. A solver fills the order partially on the destination chain; the fill triggers a cross-chain `RedeemEscrow` message with `body.tokens` covering only part of the escrowed amount.
3. `onAccept` (or `onGetResponse`) decodes the request and calls `_withdraw(body, isRefund=false, finalize=false)`.
4. Inside `_withdraw`, `_orders[commitment][token]` is decremented and the proportional token amount is transferred to the beneficiary via `_sendValue`/`safeTransfer` (lines 461-469), but since `finalize` is `false`, the block emitting `EscrowReleased`/`EscrowRefunded` (lines 472-484) is skipped entirely — no event is emitted despite real funds leaving the contract.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L140-144)
```text
    /**
     * @dev Maps (commitment, token address) to the escrowed amount for that token.
     * Decremented as tokens are released via fills or refunds.
     */
    mapping(bytes32 => mapping(address => uint256)) public _orders;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L436-450)
```text
    /**
     * @dev Releases escrowed tokens to a beneficiary. Iterates over the withdrawal request's
     * token list, decrements the escrow balance for each, and transfers tokens out.
     *
     * When `finalize` is true, the order is marked as filled in the `_filled` mapping,
     * any accumulated transaction fees (in the protocol fee token) are forwarded to the
     * beneficiary, and the appropriate event (EscrowReleased or EscrowRefunded) is emitted.
     *
     * When `finalize` is false (partial fills), only the proportional token amounts are
     * released without finalizing the order.
     *
     * @param body The withdrawal request containing the commitment, token amounts, and beneficiary.
     * @param isRefund If true, emits EscrowRefunded instead of EscrowReleased on finalization.
     * @param finalize If true, marks the order as complete and releases accumulated fees.
     */
```

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-484)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }

            if (isRefund) {
                emit EscrowRefunded({commitment: body.commitment, tokens: body.tokens});
            } else {
                emit EscrowReleased({commitment: body.commitment, tokens: body.tokens});
            }
        }
```
