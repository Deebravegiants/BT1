### Title
Fee-on-transfer tokens break escrow accounting in `IntentGatewayV2.placeOrder` (Tron variant), causing under-collateralized escrow and stuck payouts - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.placeOrder` credits escrow using the *requested* input amount rather than the *actually received* balance, unlike the hardened mainline EVM implementation which explicitly measures balances before/after every `transferFrom` to defend against fee-on-transfer (FOT) tokens.

### Finding Description
In the mainline `evm/src/apps/IntentGatewayV2.sol`, `placeOrder` was hardened specifically against FOT tokens: it snapshots `balanceOf` before and after every `safeTransferFrom` (both in the direct path and the predispatch/sweep path) and mutates `order.inputs[i].amount` to the actually-received amount before computing the commitment and crediting escrow: [1](#0-0) 

The Tron variant, however, still uses the naive pattern that the mainline code explicitly moved away from. In its non-predispatch path it does: [2](#0-1) 

Here, `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` is called with the user-requested amount, but the escrow ledger is then credited with `reducedInputs[i].amount` — which is derived from `order.inputs[i].amount` (the pre-transfer, pre-fee amount) minus only the protocol fee, computed earlier at lines 359-374, not from the tokens actually held by the contract: [3](#0-2) 

The same flaw exists in the predispatch/sweep branch, which sweeps `balance = IERC20(token).balanceOf(dispatcher)` from the call-dispatcher to the gateway via a `transfer()` call, but still credits `_orders[commitment][token] += reducedInputs[i].amount` (the pre-fee accounting) instead of the amount actually landing in the gateway after that second `transfer()`: [4](#0-3) 

For any fee-on-transfer ERC20 registered as an intent input, the gateway's actual token balance after `placeOrder` will be strictly less than the sum of `_orders[commitment][token]` recorded for it. This is the same root cause reported for `Allo.sol#_fundPool`: accounting is based on the nominal transfer amount instead of the measured balance delta.

### Impact Explanation
Because `withdraw()` (called both for solver settlement via `RedeemEscrow` and for cancellations via `RefundEscrow`) unconditionally attempts `token.call(transfer.selector, beneficiary, amount)` for the full escrowed `amount` recorded in `_orders[commitment][token]`: [5](#0-4) 

the contract will hold insufficient actual token balance to honor the recorded escrow once a FOT token has been used in one or more orders. This creates a system-wide insolvency: later legitimate solvers or users attempting to withdraw/redeem escrow for *other* orders sharing the same token can be blocked (their `transfer()` call reverts or under-delivers) because the ledger overstates what the contract actually holds — a permanent freezing-of-funds condition for a subset of order participants, reachable by any single user submitting an order with a fee-on-transfer input token via `placeOrder`, an unprivileged, single-transaction entry point.

### Likelihood Explanation
Likelihood is moderate-to-high: any FOT token accepted as an order input (this is not gated by an allowlist in `placeOrder`) triggers the mismatch on every single order — no adversarial coordination or edge case timing is needed, just placing one order with such a token. The project's own mainline contract and its extensive fee-on-transfer test suite (`testPlaceOrder_FeeOnTransferToken_*`) demonstrate this is a recognized, in-scope class of token the protocol intends to support safely; the Tron deployment simply lacks the fix that was applied elsewhere in the codebase.

### Recommendation
Apply the same balance-delta pattern used in `evm/src/apps/IntentGatewayV2.sol` to the Tron variant: snapshot `IERC20(token).balanceOf(address(this))` before and after each `safeTransferFrom`/sweep `transfer()`, use the measured delta (not `order.inputs[i].amount`) to compute `reducedInputs`/protocol fees, and credit `_orders[commitment][token]` with the actual received amount, mutating `order.inputs` accordingly before computing the commitment hash — mirroring lines 291-329 of the mainline contract.

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 (e.g. 1% fee, as in the existing `FeeOnTransferToken` test helper at `evm/tests/foundry/IntentGatewayV2SameChainTest.sol:2690-2735`) and register it as an intent input token on the Tron `IntentGatewayV2`.
2. User A calls `placeOrder` with `inputs[0] = {token: FOT, amount: 1000e18}`. `safeTransferFrom` moves `1000e18` requested, but the gateway only receives `990e18` (1% burned by the token). The contract nonetheless sets `_orders[commitment_A][FOT] = 1000e18` (minus protocol fee if any), i.e. 10e18 more than it actually holds.
3. User B similarly places a separate order using the same FOT token, also over-crediting the ledger.
4. When solvers fill and redeem via `withdraw()` for order A, `token.call(transfer.selector, beneficiary, 1000e18-ish)` will fail or drain tokens belonging to order B's escrow, since the gateway's real FOT balance is short by the accumulated transfer-fee amounts across all orders — causing order B's later withdrawal to revert/fail with insufficient balance, permanently freezing B's expected proceeds.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L319-323)
```text
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-385)
```text
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
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-468)
```text
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

                unchecked {
                    ++i;
                }
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
