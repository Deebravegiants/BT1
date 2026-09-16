### Title
Reentrancy in `withdraw()` via unchecked low-level token transfer before escrow decrement, enabling escrow drain to persist across a reverted/retried delivery - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` in the Tron variant of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol:691-730`) performs the raw token/ETH transfer to the beneficiary via a low-level `.call()` *before* decrementing `_orders[body.commitment][token]`, violating Checks-Effects-Interactions. This is the same bug class as the external report ("state changes after external calls"/reentrancy in a settlement-finalizing function), and it is reachable from `onAccept()`/`onGetResponse()`, which are the ISMP settlement callbacks invoked when a cross-chain `RedeemEscrow`/`RefundEscrow` message or a cancellation GET-response is delivered by any relayer.

### Finding Description
```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

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

        _orders[body.commitment][token] -= amount;   // <-- effect happens AFTER the external interaction
        unchecked { ++i; }
    }
    ...
}
``` [1](#0-0) 

Contrast this with the already-hardened sibling implementation in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`, which decrements the escrow *before* transferring: `_orders[body.commitment][token] = escrowed - amount;` followed by `_sendValue`/`safeTransfer`. [2](#0-1) 

`withdraw` is called from the settlement/callback path (`onAccept` for `RedeemEscrow`/`RefundEscrow`, `onGetResponse` for source-chain cancellation), both of which are reached by any relayer delivering a valid ISMP proof — the message content (beneficiary, token list, amounts) is attacker-influenced to the extent the attacker is a solver/filler who fills an order and is named beneficiary, or a user cancelling their own order. Because the ETH path uses a low-level `.call{value: amount}("")` to an attacker-controlled beneficiary address, and ERC-20 transfers use a raw `.call` rather than `SafeERC20`, a malicious beneficiary contract (or a malicious/callback-enabled token) can re-enter during that external call. At the point of re-entry, `_orders[body.commitment][token]` has not yet been decremented for the *current* token in the loop, and for tokens later in the `body.tokens` array it hasn't been touched at all.

### Impact Explanation
If the beneficiary is a contract with a `receive()`/fallback hook (native-token payout branch) or the escrowed asset is an ERC-777/callback-token, the beneficiary can re-enter this same withdrawal path (e.g., via a second `onGetResponse`/`onAccept` delivery of a related message, or, more directly, by having the malicious contract call back into `withdraw`-reachable entry points that read `_orders[commitment][token]` before it's decremented) and drain the escrow for a commitment more than once, since the stale `_orders[...]` balance still reads non-zero at re-entry. This is a fund-theft/double-payout primitive on escrowed user funds held by the Intent Gateway, matching the "concrete theft ... of funds" acceptance bar. The blast radius is limited to escrow held under this specific Tron-variant contract, but that escrow directly backs settled user/solver funds.

### Likelihood Explanation
Medium-High: the vulnerable function is reached by the standard, permissionless settlement flow (any relayer can deliver the `RedeemEscrow`/`RefundEscrow` post or the cancellation get-response with a valid Hyperbridge proof) and the beneficiary address is fully attacker-controlled (it is the solver's own address on fill, or the user's own address on cancel) — an attacker only needs to designate a malicious contract as the fill beneficiary/solver address and include a native-token or malicious-token leg in the order to trigger the vulnerable branch. This mirrors exactly the pattern that was already identified and fixed (with dedicated regression tests) in the mainline `IntentsBase.sol`/`IntrinsicIntents.sol`/`ExtrinsicIntents.sol` implementations, but the fix was not carried over to this Tron-specific copy of the contract.

### Recommendation
Apply the same Checks-Effects-Interactions fix already used in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`: decrement `_orders[body.commitment][token]` (and delete/clear the `TRANSACTION_FEES` entry) *before* performing the native-token `.call` or ERC-20 transfer, and prefer `SafeERC20.safeTransfer` over raw low-level `.call` for the ERC-20 branch. Additionally consider adding a reentrancy guard around `withdraw`/`onAccept`/`onGetResponse` as the external report recommends, consistent with the CEI fix and tests already added for the mainline gateway (`evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`).

### Proof of Concept
1. Attacker places (or is selected as solver for) a cross-chain order whose output/refund beneficiary is a malicious contract with a `receive()` hook, and whose escrowed inputs include native ETH plus at least one other token.
2. A relayer delivers the settlement message (`RedeemEscrow`/`RefundEscrow`) with a valid proof; `onAccept` calls `withdraw(body, isRefund)`.
3. Inside `withdraw`'s loop, when the native-token branch executes `beneficiary.call{value: amount}("")`, control transfers to the malicious beneficiary's `receive()` before `_orders[body.commitment][token] -= amount` runs.
4. The malicious contract re-enters (directly or via a follow-up crafted message/GET-response reachable through the same commitment) while `_orders[commitment][token]` for that token (and any not-yet-processed token in the array) still reflects the pre-payout balance, allowing a second payout to be extracted for the same commitment before the loop's decrement takes effect — draining escrow beyond what was legitimately owed. [3](#0-2)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
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
