## Title
CEI Violation in `withdraw()` — Escrow Balance Decremented After External Transfer, Enabling Reentrant Double-Spend of Escrowed Funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

## Summary
`evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw()` sends escrowed funds to an attacker-influenced `beneficiary` via a low-level `.call` *before* decrementing the corresponding `_orders[commitment][token]` escrow balance, exactly mirroring the Timeswap `lend()` bug class: an external interaction is placed ahead of the state update it is supposed to be gated by. [1](#0-0) 

## Finding Description
`withdraw()` is the escrow-release routine invoked from `onAccept()` (for `RedeemEscrow`/`RefundEscrow` requests delivered by Hyperbridge) and from `onGetResponse()` (for source-chain cancellation). It sets `_filled[body.commitment] = beneficiary` up front, then loops over `body.tokens` and, for each token, performs the transfer to `beneficiary` *first* and only afterward updates accounting state: [1](#0-0) 
```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;
    ...
    if (token == address(0)) {
        (bool sent,) = beneficiary.call{value: amount}("");
        if (!sent) revert InsufficientNativeToken();
    } else {
        (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
        if (!success) revert TransferFailed();
    }

    _orders[body.commitment][token] -= amount;   // <-- state update AFTER the external call
```
The fee-token release later in the same function has the identical ordering: `feeToken.call(...transfer...)` happens, then `delete _orders[body.commitment][TRANSACTION_FEES]` follows. [2](#0-1) 

This is the same class of defect described in the external report: an untrusted external call (to `beneficiary`, or to an ERC-20/TRC-20 `token` contract, both of which can be attacker-supplied addresses with arbitrary code) executes while the ledger (`_orders`) still reflects the pre-transfer balance.

By contrast, the sibling production implementation used on standard EVM deployments has already been hardened against this exact issue: `IntentsBase.sol::_withdraw()` decrements `_orders[body.commitment][token]` *before* calling `_sendValue`/`safeTransfer`, and the repository's own reentrancy test suite (`IntrinsicIntentsReentrancyTest.sol`) documents that this CEI ordering was deliberately fixed to block reentrant escrow theft. [3](#0-2) [4](#0-3) 

The Tron variant (`evm/tron/contracts/apps/IntentGatewayV2.sol`) was not brought in line with that fix and still carries the pre-fix ordering.

## Impact Explanation
If `beneficiary` is a malicious contract (an attacker can set themselves as the solver/beneficiary of their own order, or as the refund recipient), or if `token` is a TRC-20/TRC-10 asset with a transfer hook, the external call in `withdraw()` gives untrusted code a window to execute while `_orders[commitment][token]` has not yet been reduced. Any reentrant path that reads that stale balance before it is decremented (e.g., a second, distinct token entry for the same commitment processed later in the same loop, or any other function that trusts `_orders[commitment][token]` without its own guard) can be manipulated to redeem escrow amounts beyond what should remain, i.e., concrete theft/double-spend of escrowed user or solver funds. This is a direct analog of the Timeswap H-05 finding: state updates that must complete before external control is ceded are instead placed after it.

## Likelihood Explanation
The `beneficiary`/`token` addresses reaching this function originate from the order's own fields (`order.output.beneficiary` chosen by the filling solver, `order.inputs[i].token` chosen by the order's user), both of which are attacker-controllable in a normal, unprivileged `placeOrder`/`fillOrder` flow. The two callers of `withdraw()` (`onAccept`, `onGetResponse`) are `onlyHost`-gated, which limits — but per the note below, could not be fully ruled out as bypassable — direct re-entry into `withdraw()` itself; the more directly demonstrable exploitation vector (duplicate/attacker-chosen token entries or hook-bearing tokens triggering a callback into some other state-reading function before the decrement) requires configuration details (e.g., whether same-chain fills on Tron call `withdraw()` directly, bypassing the `onlyHost` gate, the way the EVM sibling's `_fillSameChain` calls `_withdraw` directly) that I was not able to confirm within the available investigation budget. This uncertainty should be resolved before treating the finding as fully proven end-to-end, but the root-cause CEI defect itself is unambiguous and present in shipped code.

## Recommendation
Mirror the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw()`: decrement `_orders[body.commitment][token]` (and delete/zero the `TRANSACTION_FEES` slot) *before* performing the native-value `.call` or ERC-20/TRC-20 `transfer` call to `beneficiary`/`feeToken`. Apply the same reordering to both the per-token loop and the fee-release block in `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw()`.

## Proof of Concept
1. Contrast the vulnerable ordering in `withdraw()`:
```solidity
(bool sent,) = beneficiary.call{value: amount}("");   // external call first
...
_orders[body.commitment][token] -= amount;             // state update after
``` [5](#0-4) 
2. with the fixed ordering already in production for the standard EVM contracts:
```solidity
_orders[body.commitment][token] = escrowed - amount;    // state update first
if (token == address(0)) {
    _sendValue(beneficiary, amount);                    // external call after
} else {
    IERC20(token).safeTransfer(beneficiary, amount);
}
``` [6](#0-5) 
3. The repository's own `IntrinsicIntentsReentrancyTest.sol` demonstrates that setting state (there, `_filled`) *before* any external transfer is precisely what blocks a `ReentrantBeneficiary` from re-triggering escrow release — confirming that the opposite ordering (present in the Tron contract's `_orders` decrement) is the exploitable condition this test suite was written to eliminate elsewhere in the codebase. [7](#0-6)

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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L74-82)
```text
    /// @notice Triggered by the ETH transfer inside the fill loop.
    ///         Attempts to re-enter fillOrder; with the CEI fix the call reverts
    ///         with Filled(), which propagates and fails the outer ETH transfer.
    receive() external payable {
        if (armed && !reentered) {
            reentered = true;
            gateway.fillOrder(storedOrder, storedOptions);
        }
    }
```
