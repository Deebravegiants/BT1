### Title
Missing contract-existence check on low-level token transfers in `withdraw`/`SweepDust` allows silent transfer failure and permanent loss of escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` replaces OpenZeppelin's `SafeERC20.safeTransfer` (used in the EVM implementation) with a raw low-level `.call()` to the token address, checking only the boolean `success` return value and never verifying that the token address actually contains contract code. A low-level `CALL` to an address with no code always returns `success == true` with empty return data, so a transfer to a destroyed or non-existent token contract appears to succeed while no tokens actually move.

### Finding Description
In `withdraw()`, escrowed token transfers are performed with: [1](#0-0) 

and fee-token redemption: [2](#0-1) 

as well as in the `SweepDust` branch of `onAccept`: [3](#0-2) 

None of these calls check `token.code.length` (or `EXTCODESIZE`) before or after the call. Contrast this with the same operations in the canonical EVM contracts (`evm/src/apps/intentsv2/IntentsBase.sol`), which use `IERC20(token).safeTransfer(...)`, and with `evm/src/utils/CallDispatcher.sol`'s `dispatch()`, which explicitly checks `extcodesize(to) == 0` and reverts with `NotContract` before executing arbitrary calls: [4](#0-3) 

`withdraw()` is reached from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests, which are Hyperbridge-relayed messages authenticated via `authenticate()` and then dispatched to `withdraw()`: [5](#0-4) 

Regardless of the call outcome, `withdraw()` unconditionally decrements the escrow accounting and marks the commitment as filled: [6](#0-5) 

### Impact Explanation
If the token contract associated with an escrowed order becomes a non-contract address at redemption time (e.g., the token self-destructs, or a token address is otherwise left with no code), the relayer-delivered `RedeemEscrow`/`RefundEscrow` message will succeed even though no TRC20 tokens were transferred to the beneficiary. Because `_orders[commitment][token]` is decremented and `_filled[commitment]` is set regardless, the escrowed balance retained by the contract becomes permanently unreachable — there is no remaining code path to re-trigger the transfer for that commitment once it is marked filled/refunded. This is a permanent freezing of escrowed user funds, and in the `SweepDust` case it silently drops swept dust that should have gone to the beneficiary.

### Likelihood Explanation
Reaching `withdraw()` requires only a legitimately relayed `RedeemEscrow`/`RefundEscrow` message (the normal, expected flow for filling/cancelling any cross-chain intent), so no privileged or malicious actor is needed to trigger the code path. The only precondition is that the escrowed token's contract has no code at redemption time (e.g., destroyed after order creation, or a griefing order created against a token address expected to later have no code). This is a plausible operational scenario for any long-lived escrow, matching the report's exploit scenario of a destroyed token contract.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`/`safeTransferFrom` (as already used in the canonical `evm/src/apps/intentsv2/IntentsBase.sol`), or explicitly check `token.code.length > 0` (mirroring the `extcodesize` check already used in `evm/src/utils/CallDispatcher.sol`) before treating the low-level call's success as valid.

### Proof of Concept
1. An order escrows TRC20 token `T` on the Tron `IntentGatewayV2`, recorded in `_orders[commitment][T]`.
2. Token `T`'s contract is later destroyed (e.g., via `selfdestruct` if the token implementation permits it, or the address otherwise ends up with zero code before redemption).
3. A relayer delivers a valid `RedeemEscrow` message; `authenticate()` passes and `withdraw()` is invoked.
4. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` targets code-less address `T`, which trivially returns `(true, "")`.
5. `success` is `true`, so no revert occurs; `_orders[commitment][T] -= amount` executes and `_filled[commitment] = beneficiary` is set.
6. No tokens were actually transferred to `beneficiary`, and the commitment is now permanently marked filled — the escrowed balance is stuck with no way to retry or reclaim it. [6](#0-5)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/utils/CallDispatcher.sol (L47-61)
```text
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
```
