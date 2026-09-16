### Title
CEI violation in `IntentGatewayV2.withdraw` allows escrow re-draining via reentrant native/ERC20 transfer callback - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The internal `withdraw()` function in the Tron `IntentGatewayV2` releases escrowed funds to a beneficiary via a raw `.call` (for native value transfers) and a low-level `token.call(transfer)` (for ERC20s) *before* decrementing the corresponding `_orders[commitment][token]` escrow accounting and *before* deleting the accumulated `TRANSACTION_FEES` entry. This is the same class of bug described in the external report: an external call is made prior to the effects (state deletion/decrement) that are supposed to prevent double-spending.

### Finding Description
In `withdraw()`: [1](#0-0) 

The function sets `_filled[body.commitment] = beneficiary` up front (a CEI-correct pattern for the "already filled" guard), but the actual escrow-releasing state changes are ordered incorrectly:
- For each token in the withdrawal, it performs `beneficiary.call{value: amount}("")` or `token.call(transfer(...))` and only afterwards executes `_orders[body.commitment][token] -= amount;`.
- For the transaction-fee sweep, it calls `feeToken.call(transfer(...))` and only afterwards `delete _orders[body.commitment][TRANSACTION_FEES];`.

Because `beneficiary` is attacker-controlled (an order's declared beneficiary address, or in the native-asset branch, any address that can receive a callback via `receive()`/`fallback()`), and ERC777-style or otherwise callback-bearing tokens (or a future alternate token/vault integration) can trigger a reentrant call back into the gateway during the transfer, an attacker beneficiary could reenter `withdraw()` (via `onGetResponse` -> `withdraw` or other entrypoints that reach `withdraw`) before `_orders[commitment][token]` is decremented, and drain the same escrow entry multiple times — precisely the "order of operations" bug pattern the external report flags for `cancelLock`.

This mirrors an issue the team has already fixed elsewhere in the same codebase: `IntentsBase._withdraw` (the EVM-mainline sibling implementation) already decrements the escrow balance (`_orders[body.commitment][token] = escrowed - amount;`) *before* performing the transfer: [2](#0-1) 
and the repository's own reentrancy tests explicitly document the CEI remediation pattern (set state before the external call) for the sibling `_fillSameChain`/`_fillCrossChain` functions: [3](#0-2) 

The Tron `IntentGatewayV2.withdraw` function was not brought in line with this same CEI discipline for the per-token escrow decrement and the fee-sweep delete.

### Impact Explanation
If reachable with a callback-capable beneficiary or token, this allows an attacker (as the order beneficiary) to drain more from `_orders[commitment][token]` than was escrowed, i.e., theft of other users'/protocol's escrowed funds — a concrete theft-of-funds vulnerability, consistent with a Medium/High-severity CEI violation. Impact is Medium given it requires a callback-triggering token or native-value beneficiary contract (standard non-callback ERC20 transfers alone do not enable reentrancy).

### Likelihood Explanation
Likelihood is Medium: exploitation requires either (a) a beneficiary contract receiving the native-asset leg via `.call{value}` and reentering during its `receive()`/`fallback()`, or (b) an ERC20/ERC777-style token with transfer hooks. The native-asset case is always reachable by any order that pays out native value to an attacker-chosen beneficiary address, since `.call{value}(...)` unconditionally forwards gas and permits arbitrary reentrant execution — this does not require anything exotic like ERC777, unlike the escrow-token leg.

### Recommendation
Reorder `withdraw()` to follow Checks-Effects-Interactions: decrement `_orders[body.commitment][token]` (and `delete _orders[body.commitment][TRANSACTION_FEES]`) before making the native `.call` / `token.call(transfer)` external calls, mirroring the pattern already used in `IntentsBase._withdraw`.

### Proof of Concept
Conceptual PoC (mirrors the pattern in the repo's own `IntrinsicIntentsReentrancyTest.sol` reentrancy harness):
1. Attacker places/becomes beneficiary of an order whose output includes native value (`token == address(0)`).
2. When `withdraw()` reaches the native-asset branch, `beneficiary.call{value: amount}("")` invokes the attacker contract's `receive()`.
3. Since `_orders[body.commitment][address(0)] -= amount` has not yet executed, the attacker's `receive()` reenters a path that eventually calls `withdraw()` again for the same commitment/token, observing `_orders[body.commitment][token]` still at its pre-decrement value and receiving another payout of `amount` before the outer call finally decrements it once.
4. Repeated reentrant calls (bounded only by gas) drain more than the escrowed `amount`. [4](#0-3)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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
