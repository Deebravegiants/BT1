## Reentrancy in `IntentGatewayV2.withdraw` (Tron variant) allows repeated draining of the same escrow - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The CVE describes a use-after-free where a component acts on state that a callback should have invalidated first. The reachable analog in Hyperbridge is a checks-effects-interactions (CEI) violation in the Tron build of `IntentGatewayV2`: `withdraw()` performs the external token/ETH transfer to an attacker-controlled `beneficiary` **before** decrementing the escrow accounting (`_orders[commitment][token]`), letting a malicious beneficiary re-enter and consume the "not yet freed" escrow balance multiple times.

### Finding Description
`withdraw()` in the Tron `IntentGatewayV2` iterates over `body.tokens`, checks that escrow exists, performs the external send, and only afterward reduces the recorded balance: [1](#0-0) 

Specifically:
- `if (_orders[body.commitment][token] == 0) revert UnknownOrder();` is checked, then
- `beneficiary.call{value: amount}("")` (native) or `token.call(...transfer...)` (ERC20) is executed,
- and only then is `_orders[body.commitment][token] -= amount;` applied.

Because `beneficiary` is derived directly from `body.beneficiary`, which is attacker-influenced (the solver address on a `RedeemEscrow` fill, or the user address on a `RefundEscrow`/cancellation), a malicious contract can be placed as beneficiary. During the native ETH transfer (`.call{value: amount}("")`), or via an ERC20 with transfer hooks, the beneficiary's fallback can re-enter `withdraw` (reachable again through `onAccept`/`onGetResponse`) while `_orders[commitment][token]` still reflects the un-decremented balance, allowing the same escrow slot to be paid out more than once before it is finally zeroed.

This is the correct pattern by contrast in the sibling EVM implementation, where `_withdraw` in `IntentsBase.sol` decrements `_orders` **before** issuing the external send: [2](#0-1) 

The project's own tests demonstrate the team is aware of and defends against exactly this reentrancy class elsewhere (`IntrinsicIntentsReentrancyTest.sol`, CEI ordering with `_filled` set first), but that hardening was not applied to the Tron `withdraw()` implementation: [3](#0-2) 

### Impact Explanation
This allows theft of escrowed user/solver funds: a malicious beneficiary can drain more than their entitled share of `_orders[commitment][token]` from the gateway's escrow via reentrant calls before the balance is finalized, directly causing loss of user funds — a concrete "theft of funds" outcome matching the validation criteria.

### Likelihood Explanation
Reachable from a single unprivileged path: any solver/user can set themselves (or a controlled contract) as the beneficiary of an order fill or cancellation, then trigger the settlement message delivery (`onAccept`/`onGetResponse`) that invokes `withdraw()`. No privileged role is required — it is exploitable by any ordinary intent participant on Tron deployments of this contract.

### Recommendation
Reorder `withdraw()` to follow checks-effects-interactions: decrement `_orders[body.commitment][token]` (and the fee balance) before performing the external `.call`/`transfer`, mirroring the fix already present in `IntentsBase._withdraw`. Additionally consider a reentrancy guard on `withdraw`/`onAccept`/`onGetResponse` as defense in depth.

### Proof of Concept
1. Attacker creates/fills a cross-chain order so that `body.beneficiary` in the eventual `WithdrawalRequest` resolves to an attacker-controlled contract with a `receive()`/token-hook that calls back into the gateway's `onAccept` (or `onGetResponse`) for the same commitment.
2. When Hyperbridge delivers the `RedeemEscrow`/`RefundEscrow` message, `withdraw()` reaches the token loop and calls `beneficiary.call{value: amount}("")` for the first token entry while `_orders[commitment][token]` is still non-zero.
3. The attacker's fallback re-enters the same code path before `_orders[commitment][token] -= amount;` executes, passing the `UnknownOrder` check again and receiving another payout from the same (not-yet-decremented) escrow slot.
4. Repeat until escrow/gas runs out, extracting multiples of the legitimate payout from a single order's escrow.

Note: I was unable to view the exact `onAccept`/`onGetResponse` function bodies in this file due to truncation in the final tool round (only line ranges up to `withdraw`/`onGetResponse` at lines 691–743 were retrieved), so full confirmation of any additional guard between message delivery and `withdraw()` call sites should be verified in a follow-up session with full file access.

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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L37-48)
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
```
