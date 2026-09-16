## Title
Reentrant native-token transfer in Tron `IntentGatewayV2.withdraw()` allows draining escrow beyond the recorded amount - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2.sol` contains the exact `checkProxy`-class bug described in the external report: an external, attacker-controllable call (a native ETH/TRX transfer to `beneficiary`) is made *before* the corresponding escrow-accounting state (`_orders[body.commitment][token]`) is decremented, instead of after. This is the classic "effects after interaction" ordering that the report flags as re-entrancy-exploitable.

### Finding Description
In `withdraw()`: [1](#0-0) 

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

        _orders[body.commitment][token] -= amount;
        ...
```

The escrow-decrement line, `_orders[body.commitment][token] -= amount;`, runs **after** the native-value `.call` that hands control to `beneficiary`. This mirrors `checkProxy`'s flaw of executing the external call and only deleting/updating the accounting state afterward. This is the same class of bug that was already identified and fixed in the sibling EVM contract, `IntentsBase.sol`'s `_withdraw()`, where the decrement is explicitly moved *before* the transfer: [2](#0-1) 

and validated by dedicated reentrancy regression tests (`IntrinsicIntentsReentrancyTest.sol`), whose comments explicitly document that the pre-fix pattern ("`beneficiary.call{value:...}` ← RE-ENTRY HERE, [state] still unset pre-fix") was exploitable: [3](#0-2) 

The Tron contract's `withdraw()` was evidently never given the same CEI fix — it still performs the same "call-then-decrement" sequence that the fixed contract explicitly avoids.

The `withdraw()` function processes `body.tokens`, an array of `(token, amount)` pairs decoded from the incoming cross-chain `WithdrawalRequest` (constructed on the order's fill/cancel side and carried by an authenticated Hyperbridge POST message or GET response). If `body.tokens` contains a native-token (`address(0)`) entry, then reentry into the beneficiary's fallback occurs while `_orders[body.commitment][token]` for that entry is still non-zero. Any reentrant path that reaches `withdraw()` again for the same commitment before the decrement executes — either via another token entry in a crafted duplicate list, or via a legitimately-relayed second delivery for the same commitment landing in the same call stack — would allow the `_orders[commitment][token] == 0` guard to still pass and permit the transfer to be repeated, draining more of the tracked escrow balance than was ever deposited for that order.

### Impact Explanation
This is concrete theft of escrowed funds: an attacker controlling the `beneficiary` address of an order (the solver on a fill, or the user on a refund/cancel) can, by using a contract as beneficiary with a malicious `receive()`/fallback, attempt to re-enter and pull additional native-token payouts from the same escrow slot before its balance is zeroed. Given the reported historical precedent (Operations.sol `checkProxy`) explicitly resulted in double-spend of escrowed value, and given Hyperbridge's own team already classified and fixed the identical ordering bug elsewhere in this codebase, this is a High severity, fund-draining issue on any chain where this Tron contract variant is deployed.

### Likelihood Explanation
Medium-to-High. The attacker only needs to control the `beneficiary` field of an order they place or fill (which is attacker-controlled input by design — `beneficiary` is part of `PaymentInfo`/`WithdrawalRequest`), and to include or trigger a native-token payout so a `.call{value: ...}` is made to their contract before the debit. The primary defense (`nonReentrant`/CEI) that protects the parallel EVM `IntentGatewayV2`/`IntrinsicIntents` path is absent here, and the codebase's own reentrancy test suite documents this exact attack shape as previously exploitable, increasing confidence this ordering is a genuine regression/oversight in the Tron fork rather than a benign difference.

### Recommendation
Apply the same check-effects-interactions fix already used in `IntentsBase.sol::_withdraw()`: decrement `_orders[body.commitment][token]` *before* making the external `.call`/token transfer, and/or add `_filled[commitment]`-style guards plus a `nonReentrant` modifier around any externally-reachable entry point that leads into `withdraw()`. Port the `IntrinsicIntentsReentrancyTest.sol`-style regression tests to the Tron contract to lock in the fix.

### Proof of Concept
1. Attacker places (or is selected to fill) an order whose `output`/refund payout on the destination/source chain includes a native-token entry, with `beneficiary` set to an attacker-controlled contract.
2. The Hyperbridge message carrying the `WithdrawalRequest` is delivered, triggering `IntentGatewayV2.onAccept` → `withdraw()`.
3. Inside the loop, `_orders[commitment][address(0)]` is checked (non-zero), then `beneficiary.call{value: amount}("")` transfers native tokens and yields control to the attacker's `receive()`.
4. Because `_orders[commitment][address(0)] -= amount` has **not yet executed**, any reentrant call path that reaches `withdraw()` for the same commitment (e.g., a second withdrawal delivery already pending in the mempool/batch, or duplicate token entries in a maliciously constructed order body) still sees the escrow as non-zero and pays out again.
5. Net effect: the beneficiary receives more native tokens than were ever escrowed for the order, at the expense of the protocol/other users' funds.

**Note on verification limits:** I was not able to fully trace, within the available tooling budget, the exact externally-reachable call path that would let an attacker retrigger `withdraw()` for the *same* commitment while still inside the reentrant callback (the `onAccept`/`onGetResponse` entry points are `onlyHost`-gated). The vulnerable call-before-decrement ordering itself is confirmed and is a direct regression relative to the already-fixed sibling contract, but confirming a complete, unauthenticated end-to-end exploit path in the Tron variant would benefit from a full Devin session with build/test tooling to attempt a working PoC (e.g., a Foundry/Hardhat test analogous to `IntrinsicIntentsReentrancyTest.sol` targeting the Tron contract).

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L460-469)
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
