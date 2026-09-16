## Finding

Based on my investigation, the codebase shows a clear, deliberate pattern of protections against the exact bug class Opyn suffered (external state/asset transfer executed before the internal accounting is finalized, allowing reuse). Across `modules/ismp/core/src/handlers/*.rs`, `evm/src/core/EvmHost.sol`, and `evm/src/apps/intentsv2/IntentsBase.sol`, receipts/`_filled` markers are written **before** the external callback/transfer (checks-effects-interactions), and there are even regression tests (`evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`) documenting a prior CEI bug that was fixed by moving `_filled[commitment] = msg.sender` to the top of `_fillSameChain`/`_withdraw`.

However, that fix was not carried over to the Tron deployment of the same contract.

### Title
CEI violation in Tron `IntentGatewayV2.withdraw()` transfers escrow before decrementing accounting - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`withdraw()` in the Tron build of `IntentGatewayV2` performs the native/ERC20 transfer of escrowed funds to the beneficiary **before** decrementing `_orders[commitment][token]`, the opposite ordering of the already-patched EVM/mainnet `IntentsBase.sol::_withdraw()`. [1](#0-0) 

### Finding Description
`withdraw()` sets `_filled[body.commitment] = beneficiary` up front (mirroring the fix applied to the main EVM contract for the same-chain fee/escrow reentrancy bug documented in `IntrinsicIntentsReentrancyTest.sol`), but the per-token loop checks `_orders[body.commitment][token] == 0` and then makes the external transfer (`beneficiary.call{value: amount}("")` for native, or `token.call(...transfer...)` for ERC20) **before** updating `_orders[body.commitment][token] -= amount`: [1](#0-0) 

Compare this to the fixed, correct ordering in the primary EVM contract, where the escrow balance is decremented *before* the external transfer: [2](#0-1) 

This is precisely the class of bug in the Opyn incident: the contract performs the value-releasing action (transfer) without first finalizing/verifying the internal state that is supposed to prevent reuse, so an external call that regains control during the transfer sees stale accounting. `withdraw()` is reachable only from `onAccept()`/`onGetResponse()`, both gated by `onlyHost` — i.e., only the `EvmHost`/`HandlerV2` dispatch path can invoke it, and that dispatch path is itself permissionless for any relayer who supplies a valid consensus/state proof (`HandlerV2.handlePostRequests`, `EvmHost.dispatchIncoming`). Because `order.inputs` token addresses are chosen freely by the user at `placeOrder()` time, an attacker can escrow a malicious ERC20 whose `transfer()` implementation executes arbitrary code when called by the gateway. [3](#0-2) 

### Impact Explanation
If the malicious token's `transfer()` hook can reach any other state-mutating entry point on the gateway for the same `commitment`/token before `_orders[...] -= amount` executes, an attacker could redeem escrowed funds more than once, or drain accounting for a token whose balance hasn't yet been marked spent — a concrete theft of escrowed funds, matching the "concrete theft" impact bar in the validation rules.

### Likelihood Explanation
Medium-to-low confidence on exploitability: I could not find a same-chain, permissionless `fillOrder`/intrinsic-fill path in this Tron contract that also calls `withdraw()` (the enum only exposes `RedeemEscrow`/`RefundEscrow`/governance kinds, both routed only through `onAccept`/`onGetResponse`, which are `onlyHost`-gated). This constrains the reentrancy surface compared to the main EVM contract's now-patched same-chain fill bug, since a malicious token's callback cannot directly call `onAccept` again (it isn't the host). I was not able to fully verify, within the available tool budget, whether any other unguarded function on this Tron contract or its inherited `HyperApp` base could be reached from a malicious token's `transfer()`/native-receive hook to exploit the pre-decrement window. This uncertainty should be resolved by a full manual/dynamic review of the Tron contract's complete external interface before treating this as confirmed-exploitable.

### Recommendation
Apply the same CEI fix used in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw()` to the Tron `withdraw()`: decrement `_orders[body.commitment][token]` (and delete `TRANSACTION_FEES`) **before** making the external native/ERC20 transfer call, for every token in the loop.

### Proof of Concept
Not independently verified end-to-end due to the `onlyHost` gating on both call sites (`onAccept`, `onGetResponse`); a concrete PoC would need to identify a reachable reentrant call target on the Tron deployment (e.g., another externally callable function that reads/writes `_orders[commitment][token]` for the same commitment) invocable from within a malicious ERC20's `transfer()` execution, which I could not confirm exists in the code reviewed.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
