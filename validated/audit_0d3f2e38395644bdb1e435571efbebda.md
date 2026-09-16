Based on my investigation, the strongest analog is a genuine CEI-ordering violation in the Tron `IntentGatewayV2.withdraw()` function, but it appears not to be exploitable as a drain vector because of an upfront `_filled` guard — however, it is still a real deviation from the fixed pattern used on the mainline EVM contracts and is worth flagging.

### Title
Tron `IntentGatewayV2.withdraw` updates escrow accounting after external token transfer, violating Checks-Effects-Interactions (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2` performs the escrow debit (`_orders[body.commitment][token] -= amount`) *after* the external token/native transfer inside `withdraw()`, unlike the mainline (non-Tron) `IntentsBase._withdraw`, which decrements escrow *before* transferring. This reintroduces the exact reentrancy pattern (external call before state finalization) called out in the reference report.

### Finding Description
In `withdraw()`, for each token being released, the code checks the escrow, performs a low-level `.call` to transfer funds to the beneficiary, and only afterward decrements `_orders[body.commitment][token]`: [1](#0-0) 

Compare this with the mainline `IntentsBase._withdraw`, which decrements the escrow mapping *before* the transfer (correct CEI ordering): [2](#0-1) 

The Tron `withdraw()` does set `_filled[body.commitment] = beneficiary` at its very top, before the loop: [3](#0-2) 

This guard blocks a reentrant call from re-triggering the only reachable entry points into `withdraw()` — `cancelOrder` (same-chain path) checks `_filled[commitment] != address(0)` at its start, and `onAccept`/`onGetResponse` are gated to the trusted host, so a malicious ERC-20's transfer callback re-entering these paths for the *same* commitment is blocked before it can reach `withdraw()` again. [4](#0-3) 

The mainline codebase also has a dedicated Foundry test suite (`IntrinsicIntentsReentrancyTest.sol`) confirming this exact class of reentrancy was previously exploitable and was fixed by moving the `_filled` write to the top of the fill/withdraw flow — the Tron file mirrors that fix for the `_filled` write, but not for the escrow-decrement/transfer ordering. [5](#0-4) 

### Impact Explanation
Given the `_filled` guard is set before the loop and all reachable external entry points into `withdraw()` check `_filled` (or are host-only), I could not construct a path where a reentrant call during the transfer actually double-spends escrow for the same commitment. The CEI violation is real and matches the reported bug class structurally, but its exploitability depends on there being some other reachable function that reads/mutates `_orders[commitment][token]` without checking `_filled` first — I did not find one in the code I reviewed. Because of this, I cannot confirm concrete theft or fund freezing resulting from this specific ordering issue.

### Likelihood Explanation
Low-to-uncertain: the vulnerable ordering exists in production Tron contract code, but the guard architecture appears to prevent reentrant exploitation through all currently reachable paths (`cancelOrder`, `onAccept`, `onGetResponse`). Exploitability would require either a code path that reads `_orders` for this commitment without the `_filled` check, or a future change that removes/reorders the `_filled` write relative to the loop — which is exactly the class of regression the reference report warns about.

### Recommendation
Reorder `withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to decrement `_orders[body.commitment][token]` before performing the external transfer, matching the CEI pattern already used in `IntentsBase._withdraw`, so that the code is robust against reentrancy regardless of future changes to guard ordering elsewhere in the file.

### Proof of Concept
Not constructed — I was unable to identify an unprivileged reachable call path that bypasses the `_filled` guard to exploit the mis-ordered decrement in `withdraw()`. This is a code-quality/defense-in-depth finding based on structural comparison with the fixed mainline contract and the reference report's bug class, not a proven, currently-exploitable path.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-521)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-695)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L696-714)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-470)
```text
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L37-49)
```text
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
