Based on my investigation, the Tron deployment of `IntentGatewayV2` contains an unpatched reentrancy path that mirrors the exact bug class in the Sumer Money incident.

### Title
Reentrancy in Tron `IntentGatewayV2.withdraw` allows draining escrowed order funds via external call before state update - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron-specific fork of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) still contains the pre-fix `withdraw` pattern that the main EVM codebase already patched for checks-effects-interactions (CEI). It performs the beneficiary/native/ERC-20 transfer for each escrowed input token *before* decrementing `_orders[body.commitment][token]`, and this function is reachable through `onAccept`/`onGetResponse` — both externally triggerable message-delivery paths.

### Finding Description
`withdraw` in the Tron contract sets `_filled[body.commitment] = beneficiary` up front, but then for each token entry it executes the external transfer first and only decrements the escrow accounting afterward: [1](#0-0) 

Specifically:
```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    ...
}
_orders[body.commitment][token] -= amount;
``` [2](#0-1) 

If `beneficiary` is a contract (native-token case) or a malicious ERC-20/receiver (token case), the external call's callback can re-enter `withdraw` (via `onAccept`/`onGetResponse` reprocessing the same `WithdrawalRequest`, or via re-triggering another code path that reaches `withdraw` for the same commitment) before `_orders[body.commitment][token]` is decremented, allowing the escrow check `if (_orders[body.commitment][token] == 0) revert UnknownOrder();` to pass again and the same escrowed balance to be paid out multiple times.

This is precisely the bug class the main `evm/src` code was hardened against: the sibling function `IntentsBase._withdraw` in the primary EVM package decrements the escrow (`_orders[body.commitment][token] = escrowed - amount;`) *before* making the external transfer: [3](#0-2) 

and the `IntrinsicIntents`/`ExtrinsicIntents` fill paths were likewise hardened with a documented CEI fix and dedicated regression tests (`IntrinsicIntentsReentrancyTest.sol`), confirming this exact bug class was previously found and fixed elsewhere in the codebase: [4](#0-3) 

The Tron fork, however, was not updated to match — no `nonReentrant`/`ReentrancyGuard` usage exists anywhere under `evm/tron/`, and `withdraw` there still calls out before updating storage.

### Impact Explanation
An attacker can register a malicious beneficiary/ERC-20 contract as the order beneficiary. When a `RedeemEscrow`/`RefundEscrow` message (or a GET-response cancellation) is delivered and `withdraw` is invoked, the attacker's `receive()`/`transfer` callback re-enters before the escrow decrement, allowing the same escrowed input tokens (and possibly the transaction-fee bucket, similarly ordered after the token loop but before finalization of some derived state) to be withdrawn more than once, directly draining the gateway's held funds — a concrete theft of escrowed user/solver funds, analogous to the Sumer Money reentrancy exploit.

### Likelihood Explanation
The entry points into `withdraw` — `onAccept` (for `RedeemEscrow`/`RefundEscrow`) and `onGetResponse` — are reachable by any relayer delivering a legitimately proven cross-chain message for an order whose beneficiary the attacker controls (e.g., the attacker is the solver on `RedeemEscrow`, or the user on `RefundEscrow`). No privileged role is required beyond crafting the order/beneficiary and having a validly proven message delivered, which is the standard, permissionless intents flow. This makes the likelihood high once the attacker crafts a malicious beneficiary contract.

### Recommendation
Apply the same CEI fix already used in `evm/src/apps/intentsv2/IntentsBase.sol` to the Tron `withdraw` function: decrement `_orders[body.commitment][token]` before performing the native/ERC-20 transfer, and consider adding a reentrancy guard consistent with `IntentGatewayV2.sol`'s reliance elsewhere on `ReentrancyGuard`. Backport the `_filled`-first / CEI hardening and add regression tests mirroring `IntrinsicIntentsReentrancyTest.sol` for the Tron contract.

### Proof of Concept
1. Attacker places (or is selected as the beneficiary of) an order whose `output.beneficiary`/refund beneficiary is a malicious contract with a `receive()`/token callback that re-enters `IntentGatewayV2.onAccept`/`onGetResponse` with the same `WithdrawalRequest` commitment.
2. Once a legitimate proof for a `RedeemEscrow`/`RefundEscrow` (or GET-response cancellation) is delivered, `withdraw` executes `beneficiary.call{value: amount}("")` (or the ERC-20 `transfer` call) at [5](#0-4)  while `_orders[body.commitment][token]` is still non-zero.
3. The malicious callback re-enters and calls `withdraw` again for the same commitment/token before `_orders[body.commitment][token] -= amount;` executes, passing the `if (_orders[body.commitment][token] == 0) revert UnknownOrder();` check a second time and draining the escrow twice (or more, bounded by available gas/re-entry depth).

**Note on incomplete verification**: I could not fully trace every external call path that can independently reach `withdraw` for the same commitment (e.g., whether `onGetResponse`/`onAccept` themselves guard against re-entrant dispatch at the host level for the Tron deployment specifically), since the full Tron contract body and its `fillOrder`/`onAccept` wiring were only partially retrieved due to index size limits. I recommend a Devin session with full repository access to confirm the exact re-entry trigger and validate the fix against the complete Tron contract before finalizing severity.

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
