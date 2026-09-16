### Title
Cross-chain order cancellation/redemption permanently reverts when a per-token escrow amount rounds to zero after protocol-fee deduction - (File: `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
`ExtrinsicIntents._cancelFromSource()` and `IntentsBase._withdraw()` both assume that every token listed in an order's `inputs` array has a non-zero, individually-addressable escrow balance in `_orders[commitment][token]`. Neither function distinguishes between "this token was never escrowed" and "this token's escrowed amount rounded down to zero during fee reduction at `placeOrder` time." As in the reported LP-vault bug, a legitimate but very small position for one token in a multi-token order can end up with a stored value of `0`, and the subsequent code that blindly asserts non-zero-for-all (or non-zero-for-the-nonzero-request-amount) reverts the entire operation for the whole order, not just the affected token.

### Finding Description
`placeOrder` escrows a **fee-reduced** amount per input token: [1](#0-0) 
`_orders[commitment][token] += reducedInputs[i].amount;` — while only the *raw* `order.inputs[i].amount` is checked to be non-zero at placement time, not the fee-reduced amount that is actually escrowed. For a token with small decimals or a small order amount combined with a non-zero `protocolFeeBps`, integer division in the fee computation can legitimately produce `reducedInputs[i].amount == 0` while `order.inputs[i].amount != 0`.

Two downstream code paths then blindly rely on that per-token entry being non-zero for every input, without first checking whether the entry legitimately exists as zero:

1. `_cancelFromSource` iterates over **every** input token and reverts the whole cancellation if any single token's stored escrow is zero: [2](#0-1) 

2. `_withdraw`, which is invoked both for `RedeemEscrow` (solver claiming the input tokens after a cross-chain fill) and `RefundEscrow`, uses `body.tokens[i].amount` — which is the **raw**, un-reduced `order.inputs` amount forwarded verbatim by `_fillCrossChain`/`_cancelFromDest`'s `_body(...)` call — to decide whether to skip a token, but checks the **reduced, possibly-zero** escrow balance to authorize the transfer: [3](#0-2) 
Because `amount` (the raw input amount) is non-zero, the `if (amount == 0) continue;` guard does not trigger, so the function falls through to `if (escrowed == 0) revert UnknownOrder();` and reverts — even though this is the expected, benign state for that token, not evidence of tampering. This is structurally identical to `BaseLPLib.getWithdrawRequestValue()` reverting via `require(hasRequest)` for a token whose withdrawal request was legitimately never created because its computed value rounded to zero.

The cross-chain fill path confirms `order.inputs` (raw amounts) — not the reduced escrow amounts — are what gets forwarded in the `RedeemEscrow` message body: [4](#0-3) 

### Impact Explanation
If any input token in a multi-token order has its fee-reduced escrow round to zero:
- The order can never be cancelled from the source chain (`_cancelFromSource` reverts with `UnknownOrder` for every attempt, since the loop is unconditional over all input tokens).
- Worse, once a solver fills the order on the destination chain and the `RedeemEscrow` message is relayed back, `onAccept` → `_withdraw` also reverts on the same token, meaning the solver can never redeem the input escrow they are owed either.
- The result is that the *entire* order's escrowed value across all input tokens (not just the affected dust token) becomes permanently unrecoverable — a genuine loss/freezing of funds — reachable by any user placing a normal, unprivileged cross-chain order with a per-destination protocol fee configured and a favorable dust rounding on one leg.

### Likelihood Explanation
Triggering requires only a standard user-submitted `placeOrder` transaction with a multi-input order where at least one input token's amount, decimals and the destination-specific `protocolFeeBps` combine (via integer division) to round the escrowed amount down to zero, while the raw declared amount is non-zero and thus passes the `InvalidInput` check at placement. This requires no admin, governance, or privileged role — any user or solver interacting normally with the gateway can hit it, particularly for low-decimal tokens or dust-sized legs of an order. Likelihood is therefore realistic but conditioned on fee configuration and token decimal choices, similar to the original report's caveat that it needs specific numeric conditions.

### Recommendation
- In `_cancelFromSource`, do not require every input token's escrow to be non-zero; only require that at least one token has non-zero escrow (mirroring the pattern already used correctly in `IntrinsicIntents._cancelSameChain`, see `hasEscrow` at [5](#0-4) ), and pass along the token's *actual* stored (possibly zero) escrow rather than assuming it matches the raw order amount.
- In `_withdraw`, the zero-skip check should be based on whether the token has any escrow at all recorded for the commitment (or by checking the stored `_orders[commitment][token]` value up front) rather than on the caller-supplied `amount`, so that a token whose fee-reduced escrow is legitimately zero is treated as "no-op transfer" rather than "unknown order."
- Ensure `placeOrder` validates the fee-reduced amount (not just the raw input amount) is non-zero before escrowing, or explicitly special-cases zero-value legs consistently across `placeOrder`, `_cancelFromSource`, `_cancelSameChain`, and `_withdraw`.

### Proof of Concept
1. Configure a destination-specific protocol fee (`_destinationProtocolFees[stateMachineId]` or the global `protocolFeeBps`) to a non-zero value.
2. User calls `placeOrder` with a cross-chain order containing two input tokens: token A with a large amount, and token B with a very small amount/low decimals such that `reducedInputs[B].amount = amount * (10000 - feeBps) / 10000` truncates to `0`, while `order.inputs[B].amount != 0` (passes the `InvalidInput` check in placeOrder, see [6](#0-5) ).
3. After the deadline passes without a fill, the user calls `cancelOrder` → `_cancelFromSource`. The loop at [2](#0-1)  hits `_orders[commitment][tokenB] == 0` and reverts with `UnknownOrder()`, blocking cancellation of the entire order (including token A's real escrow).
4. Alternatively, if a solver fills the order before the deadline, the `RedeemEscrow` message delivered to `onAccept` → `_withdraw` ( [3](#0-2) ) also reverts on token B for the same reason, so the solver cannot redeem the escrowed token A input either, freezing both tokens' escrow permanently.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-463)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L207-212)
```text
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L245-252)
```text
        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-464)
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
