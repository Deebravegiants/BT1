### Title
Check-Effects-Interactions violation in `IntentGatewayV2.withdraw()` enables escrow double-spend via reentrancy - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` performs external token transfers (native ETH `.call` or raw ERC20 `.call`) inside `withdraw()` before decrementing the corresponding `_orders[commitment][token]` escrow balance. This is the exact reentrancy pattern that was identified and fixed in the mainline EVM contract's equivalent `_withdraw()` function, but the fix was not carried over to the Tron copy.

### Finding Description
In `withdraw()`, for each token in the withdrawal request the contract checks the escrow is non-zero, performs the external transfer, and only *then* decrements the escrow: [1](#0-0) 

Specifically, `beneficiary.call{value: amount}("")` or the raw `token.call(...transfer...)` executes before `_orders[body.commitment][token] -= amount;`. This is a Checks-Effects-Interactions violation: the external call can trigger a callback (in the native-ETH case, straight into the beneficiary's `receive`/fallback) before the escrow accounting is updated, in the same window where the stale (not-yet-decremented) `_orders[...]` value is still readable/usable by any re-entrant path into `withdraw`/`onAccept`/`onGetResponse`.

Contrast this with the hardened mainline contract, `IntentsBase.sol`, where the escrow is decremented *before* the external transfer: [2](#0-1) 

The project's own regression tests document that this exact class of bug was previously present and exploitable in the same-chain fill path (`_filled` not being set early enough, escrow decremented after external calls), and was fixed by moving state updates ahead of interactions: [3](#0-2) 

The Tron `withdraw()` implementation still exhibits the vulnerable ordering for the per-token escrow decrement (unlike `_filled`, which *is* set up-front at line 693, the per-token `_orders[...]` balances are not).

### Impact Explanation
`withdraw()` is reached from `onAccept` (RedeemEscrow/RefundEscrow messages) and `onGetResponse` (cancel-from-source flow) — both externally triggered by relayed ISMP messages that any relayer can deliver, and whose `beneficiary`/solver address is attacker-influenced (the solver who fills an order, or an order's configured beneficiary). If the beneficiary is a malicious contract, the native-token transfer branch hands it control before the escrow ledger is updated, creating a window for a double-withdrawal of escrowed input tokens — concrete theft/permanent freezing-adjacent loss of bridged funds.

### Likelihood Explanation
Exploitability depends on finding a re-entry path back into `withdraw` before the decrement executes (e.g., via a batched/multi-leaf handler call or another callback surface reachable from the beneficiary's fallback). The upstream host's request-receipt replay protection blocks a trivial "replay the same message" attack, so full exploitation requires chaining through a still-open external-call surface, but the code pattern itself is objectively a Checks-Effects-Interactions violation of the exact type the team already fixed elsewhere in the codebase, on a fund-custody path.

### Recommendation
Mirror the fix already applied in `IntentsBase.sol::_withdraw` — decrement `_orders[body.commitment][token]` before performing the native/ERC20 transfer — in the Tron `IntentGatewayV2.withdraw()` implementation, and add the same reentrancy regression coverage (`IntrinsicIntentsReentrancyTest.sol`-style tests) for the Tron contract.

### Proof of Concept
Not independently reproduced in this review; based on static comparison of `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw()` (interactions before effects) against the patched `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw()` (effects before interactions) and the project's own reentrancy regression tests documenting the prior vulnerable pattern.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
```text
            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L282-293)
```text
    /**
     * @dev Same-chain multi-output escrow theft is blocked by the CEI fix.
     *
     * Before the fix: on a two-output order (ETH + ERC-20), the malicious
     * beneficiary could re-enter during the ETH transfer, self-fill the ERC-20
     * output (net-zero cost), trigger `_withdraw(finalize=true)`, and steal the
     * entire input[1] escrow.
     *
     * After the fix: `_filled[commitment]` is set before the loop, so the
     * reentrant call reverts with `Filled()`. The whole transaction reverts with
     * `InsufficientNativeToken()` and no state is mutated.
     */
```
