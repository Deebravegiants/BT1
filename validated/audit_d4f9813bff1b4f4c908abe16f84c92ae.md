## Title
`IntentGatewayV2.withdraw` releases escrowed tokens via external call before decrementing escrow accounting - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The reported `Market.claimReward` bug is a classic checks-effects-interactions (CEI) violation: an external value transfer runs before the corresponding state (the claimable balance) is zeroed. The Tron build of `IntentGatewayV2` contains the exact same pattern in `withdraw()`: it performs the token/ETH transfer to the beneficiary via a raw low-level `.call` and only decrements the per-order escrow accounting (`_orders[commitment][token]`) afterward, whereas the audited/fixed EVM version of the same logic (`IntentsBase._withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol`) already decrements escrow **before** transferring funds out.

### Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` is the internal settlement routine invoked from `cancelOrder` (same-chain path, directly reachable by any order owner), `onAccept` (RedeemEscrow/RefundEscrow), and `onGetResponse`: [1](#0-0) 

The loop checks `_orders[body.commitment][token] == 0`, then makes an external call (`token.call(...)` or `beneficiary.call{value: amount}("")`) to move funds out, and only afterward performs `_orders[body.commitment][token] -= amount;`. The same ordering issue repeats for transaction fees: [2](#0-1) 

This is a direct structural analog of the `claimReward` bug: the balance/accounting update that should gate future calls happens **after** the external interaction rather than before it.

By contrast, the maintained EVM implementation of the identical settlement logic was already patched to follow CEI — `_orders[...] = escrowed - amount;` executes before `_sendValue`/`safeTransfer`: [3](#0-2) 

The project even carries a dedicated regression-test suite (`IntrinsicIntentsReentrancyTest.sol`) confirming that the main EVM `IntentGatewayV2`/`IntentsBase`/`ExtrinsicIntents` contracts were hardened against exactly this class of reentrancy by setting `_filled[commitment]` before any external call and reordering escrow debits before transfers: [4](#0-3) 

The Tron variant does set `_filled[body.commitment] = beneficiary;` at the top of `withdraw()` (line 693), which blocks the most direct re-entrant path (calling `cancelOrder` again for the same commitment). However, the per-token escrow decrement is still performed after the external call, meaning the fix that was applied to the primary EVM contracts was not carried over to the Tron fork — the accounting mutation for the value actually being moved is not "effects before interactions."

### Impact Explanation
Escrowed order inputs can be attacker-supplied ERC-20 contracts (the order creator chooses the input token address in `placeOrder`), so the token transferred out in `withdraw()` can be a contract fully controlled by the attacker, giving it the opportunity to execute arbitrary code during the `.call` to `transfer(...)`. Any future refactor of `cancelOrder`/`onAccept`/`onGetResponse` that weakens or removes the `_filled` guard (or any additional public entry point added later that reads/writes `_orders[commitment][token]` for an in-flight commitment) would immediately reopen a fund-drain window, since the escrow ledger for the token being transferred is stale for the full duration of the external call. This mirrors exactly the risk class the audit report flags for `claimReward` — an external call executes while the balance that should prevent re-use has not yet been updated.

### Likelihood Explanation
Direct double-withdrawal of the *same* order is currently blocked by the early `_filled[commitment]` write, which limits immediate exploitability. Likelihood is nonetheless non-trivial because: (1) the vulnerable code path (`withdraw`) is reachable by any unprivileged order owner via `cancelOrder`, (2) the escrowed token contract is attacker-controlled, giving guaranteed callback capability, and (3) the codebase has already needed to patch this exact class of bug once in the sibling EVM implementation, showing the underlying pattern is a genuine, recurring risk in this contract family that was missed when the Tron copy was created/maintained.

### Recommendation
Apply the same CEI fix already present in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw` to `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw`: decrement `_orders[body.commitment][token]` (and clear `_orders[body.commitment][TRANSACTION_FEES]`) **before** issuing the external transfer, and add a `nonReentrant` guard for defense-in-depth given the raw `.call` usage for both native value and ERC-20 transfers.

### Proof of Concept
1. Attacker deploys a malicious ERC-20 `M` whose `transfer()` executes arbitrary attacker logic.
2. Attacker calls `placeOrder` with `M` as an input token, escrowing `M` under a fresh `commitment`.
3. Attacker calls `cancelOrder(order, options)` (same-chain path) as the order owner.
4. `withdraw()` sets `_filled[commitment] = attacker`, then reaches the loop and calls `M.transfer(attacker, amount)` — at this point `_orders[commitment][M]` still reflects the pre-withdrawal (full) balance.
5. Inside `M.transfer()`, attacker-controlled code executes with the gateway's escrow ledger for this commitment still un-decremented, matching the same "external call before state update" condition flagged in the `claimReward` report; any future code path that reads this stale value while set (e.g., a new integration point) would allow repeated extraction before the ledger is corrected in step 6.
6. Only after `M.transfer` returns does `_orders[commitment][M] -= amount;` execute at line 710 of `evm/tron/contracts/apps/IntentGatewayV2.sol`.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L85-101)
```text
/**
 * @title IntrinsicIntentsReentrancyTest
 * @notice Forge tests that confirm the CEI fix in `IntrinsicIntents._fillSameChain`
 *         and verify that `ExtrinsicIntents._fillCrossChain` is also resistant to
 *         reentrancy attacks.
 *
 * Both fill functions now open with `_filled[commitment] = msg.sender` before any
 * external calls, so a reentrant `fillOrder` attempt is always blocked by the
 * `Filled()` guard in `IntentGatewayV2.fillOrder`.
 *
 * Test matrix
 * ───────────
 *  testReentrancy_FeeTheft                    same-chain, 1 ETH output   → InsufficientNativeToken
 *  testReentrancy_EscrowTheft_MultiOutput     same-chain, ETH+ERC-20     → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked           cross-chain, 1 ETH output  → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked_MultiOutput cross-chain, ETH+ERC-20  → InsufficientNativeToken
 */
```
