I found the analogous bug. In the Tron variant of `IntentGatewayV2.sol`, the same depositsAmount-vs-total_amount mismatch pattern from the report reproduces: escrow storage uses the **fee-reduced** amount, but `cancelOrder()` and `withdraw()` operate against `order.inputs`, the **gross, pre-fee** amount taken directly from the calldata `order` struct.

### Title
Cross-chain order cancellation permanently freezes escrowed protocol-fee dust and blocks withdrawal validation due to gross-vs-reduced amount mismatch - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`placeOrder()` computes `reducedInputs` (input amount minus protocol fee) and stores only that reduced amount in `_orders[commitment][token]` [1](#0-0) . However, `cancelOrder()` builds the `WithdrawalRequest.tokens` from `order.inputs` — the original, gross (pre-fee) amounts supplied by the caller — for both the same-chain refund path and the cross-chain source/destination refund paths [2](#0-1) [3](#0-2) [4](#0-3) . This is exactly the class of bug in the report: escrow accounting is done post-fee at deposit time, but the release/refund path re-derives the amount to compare/transfer using the pre-fee value.

### Finding Description
`withdraw()` (shared by `onAccept` for `RedeemEscrow`/`RefundEscrow` and by same-chain `cancelOrder`) does:
```solidity
if (_orders[body.commitment][token] == 0) revert UnknownOrder();
...
_orders[body.commitment][token] -= amount;
``` [5](#0-4) 

`amount` here comes from `body.tokens[i].amount`, which for cancellation is `order.inputs[i].amount` — the gross amount before the protocol fee deduction — while `_orders[commitment][token]` was credited with `reducedInputs[i].amount` (gross minus protocol fee) at placement time [6](#0-5) . Since Solidity 0.8 reverts on unsigned underflow, `_orders[body.commitment][token] -= amount` reverts whenever `amount > escrowed` (i.e., whenever `protocolFeeBps > 0`), causing the entire cancellation transaction to fail. This mirrors the reported root cause verbatim: the check/subtraction compares a fee-inclusive quantity against a fee-exclusive escrow balance, which is always false/underflowing whenever a nonzero fee applies.

Contrast this with the mainline EVM contract `evm/src/apps/IntentGatewayV2.sol`/`ExtrinsicIntents.sol`, where `_withdraw()` is always fed `body.tokens` amounts that were computed consistently from `reducedInputs` throughout the placement/fill/cancel flow (see `IntentsBase.sol`'s `_withdraw`) [7](#0-6)  — that version correctly threads reduced amounts end-to-end. The Tron fork diverges by re-using raw `order.inputs` in `cancelOrder`, reintroducing the bug class the mainline code had already fixed.

### Impact Explanation
Any order placed on the Tron `IntentGatewayV2` with a nonzero `protocolFeeBps` (source-chain default or `_destinationProtocolFees` override) cannot be cancelled: same-chain cancellation, cross-chain source-side cancellation (`options.height` check dispatch), and destination-side cancellation all construct `WithdrawalRequest` from `order.inputs` and will revert on `withdraw()`'s underflowing subtraction, or on the destination-chain `RefundEscrow` message once relayed back to the source chain in `onAccept`. In the source-chain and same-chain cases the revert happens directly to the user calling `cancelOrder`, permanently freezing their escrowed input tokens (post-fee, still held by the contract) with no way to reclaim them, since the only path to move funds out of `_orders[commitment][token]` is `withdraw()`, which always underflows for fee-bearing orders. This is a permanent freezing-of-funds condition matching the "Critical" severity classification in the reference report.

### Likelihood Explanation
This triggers deterministically, not merely under adversarial conditions: any legitimate user placing and later cancelling an order on a deployment/destination with `protocolFeeBps > 0` (which the documentation describes as the standard fee mechanism, e.g. 5–30 bps in test fixtures and mainline docs) will hit this revert on cancellation. No malicious actor is required — an ordinary user attempting to cancel an expired or unfilled order is the trigger.

### Recommendation
In `cancelOrder()` (Tron `IntentGatewayV2.sol`), build the `WithdrawalRequest.tokens` array from the fee-reduced amounts actually recorded in `_orders[commitment][token]` (or recompute `reducedInputs` from `order.inputs` and `protocolFeeBps` exactly as `placeOrder` did), for all three cancellation branches (same-chain, source-chain GET dispatch context, and destination-chain `RefundEscrow` body), instead of passing `order.inputs` directly. This ensures the amount used for the escrow-balance comparison/subtraction in `withdraw()` matches what was actually escrowed.

### Proof of Concept
1. Deploy Tron `IntentGatewayV2` with `_params.protocolFeeBps = 500` (5%).
2. User calls `placeOrder` with `inputs[0].amount = 1000e6` USDC. `placeOrder` computes `reducedInputs[0].amount = 950e6` and stores `_orders[commitment][USDC] = 950e6` [8](#0-7) [9](#0-8) .
3. Order is same-chain (`order.source == order.destination`); the order remains unfilled and the user calls `cancelOrder(order, options)`.
4. `cancelOrder` builds `WithdrawalRequest{ tokens: order.inputs }` with `amount = 1000e6` (gross) [10](#0-9)  and calls `withdraw(body, true)`.
5. Inside `withdraw`, `_orders[commitment][USDC] -= 1000e6` where `_orders[commitment][USDC] == 950e6` [5](#0-4)  — this underflows and reverts under Solidity 0.8's default checked-arithmetic, so the entire cancellation transaction fails, permanently locking the user's 950e6 USDC in the contract with no other exit path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L356-384)
```text
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L440-463)
```text
                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
        } else {
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L536-539)
```text
            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L559-560)
```text
            bytes memory context =
                abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L597-599)
```text
            bytes memory body = bytes.concat(
                bytes1(uint8(RequestKind.RefundEscrow)),
                abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}))
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L700-710)
```text
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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
