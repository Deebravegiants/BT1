### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw` allows escrow to be drained via reentrancy on multi-token orders - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` performs external token/native transfers to the beneficiary **before** decrementing the corresponding `_orders[commitment][token]` escrow balance, the same root-cause pattern as the reported `DIAWhitelistedStaking.unstake` bug (state not zeroed/decremented before the transfer). This is a stale, unpatched copy: the mainline EVM contract (`evm/src/apps/intentsv2/IntentsBase.sol`) already fixes the ordering by decrementing escrow before calling out, but the Tron fork was not updated to match.

### Finding Description
In `withdraw()`: [1](#0-0) 

the function iterates escrowed tokens, performs the external transfer (native `.call{value:amount}` or ERC20 `.transfer` low-level call) first, and only afterwards executes `_orders[body.commitment][token] -= amount;`. The same pattern repeats for transaction fees, which are transferred and only then `delete`d.

Compare this to the corrected mainline implementation, which decrements the escrow balance **before** making the external call: [2](#0-1) 

The mainline repo also contains a dedicated reentrancy regression test suite (`IntrinsicIntentsReentrancyTest.sol`) documenting that this exact class of bug ("malicious beneficiary could re-enter during the ETH transfer... trigger `_withdraw(finalize=true)`, and steal the entire input[1] escrow") was previously exploitable and was fixed via CEI reordering plus setting `_filled[commitment]` before the loop: [3](#0-2) 

The Tron contract does set `_filled[body.commitment] = beneficiary` before the loop (blocking replay of `withdraw` for the *same* commitment), but this does not protect against reentrancy that reaches a *different* pending message for the *same* commitment (e.g., a separate valid ISMP-delivered `RedeemEscrow`/`RefundEscrow` post or a GET response for cancellation) that targets a different token in a multi-token order whose `_orders[commitment][token]` balance has not yet been decremented by the in-progress loop. No `nonReentrant` guard exists anywhere in the Tron contract (`onAccept`, `onGetResponse`, `withdraw`), unlike protections generally expected for this pattern.

### Impact Explanation
For any multi-token order (e.g., native ETH + ERC20 output, or ETH + fee token) settled on the Tron IntentGatewayV2, a malicious beneficiary contract can reenter during the native-token `.call` before the escrow accounting for the remaining tokens/fees is decremented, allowing a second in-flight ISMP delivery for the same commitment to drain the not-yet-decremented balances a second time. This results in direct theft of escrowed user/solver funds from the gateway contract — a concrete loss of funds analogous to the `currentStore.principal` double-withdrawal in the source report.

### Likelihood Explanation
Reachable by any solver/relayer that can get two independent, validly-proven ISMP messages targeting the same order commitment delivered to Hyperbridge (a normal, permissionless action for relayers/solvers), combined with a malicious beneficiary contract controlling the native-token leg of a multi-token order. No privileged role is required — this is reachable via the standard token-bridge mint/burn-equivalent settlement path (`onAccept`/`onGetResponse` → `withdraw`), which is explicitly in scope. The mainline contract needed a full CEI rewrite to fix this exact issue, indicating it is a realistic, previously-confirmed exploit pattern; the Tron contract simply never received that fix.

### Recommendation
Apply the same fix used in `evm/src/apps/intentsv2/IntentsBase.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`: decrement `_orders[body.commitment][token]` (and `delete` the fee entry) **before** performing the external transfer for each token in the loop, and add a `nonReentrant` guard to `onAccept`/`onGetResponse` (or `withdraw`) as defense in depth.

### Proof of Concept
Not independently executable from static analysis alone — the index does not give visibility into the Tron test suite or `EvmHost`/dispatcher reentrancy semantics for that fork, so the exact call-path for triggering a second in-flight delivery mid-loop could not be fully confirmed against Tron's ISMP host implementation. This should be validated with a Foundry/Tron reproduction analogous to `IntrinsicIntentsReentrancyTest.sol::testReentrancy_EscrowTheft_MultiOutput`, adapted to call `IntentGatewayV2.withdraw` (Tron) with a two-token order (native ETH + ERC20) and a malicious beneficiary whose `receive()`/fallback triggers delivery of a second valid message for the same commitment before the first call's loop completes.

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
