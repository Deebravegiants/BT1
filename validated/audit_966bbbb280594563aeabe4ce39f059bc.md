### Title
Checks-Effects-Interactions violation in Tron `IntentGatewayV2.withdraw` — escrow accounting mutated after external token transfer - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The CVE-2025-1934 bug class is "external/attacker-influenced execution interrupts processing before internal state is finalized, letting the interruption run with stale state." The Tron variant of `IntentGatewayV2.withdraw` reproduces exactly this class: it performs the external token transfer with a raw, unchecked `.call` before updating the escrow-accounting mappings that gate further calls, unlike the reference implementation in `IntentsBase.sol::_withdraw`, which decrements escrow before transferring (correct CEI order).

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the internal `withdraw` function (reached from `onAccept`/`onGetResponse` on `RedeemEscrow`/`RefundEscrow`) loops over `body.tokens`, checks only that `_orders[commitment][token] != 0`, then makes the external transfer, and only afterwards decrements the escrow: [1](#0-0) 

The same after-the-fact bookkeeping pattern applies to the protocol-fee sweep at the end of the function, where `feeToken.call(...)` executes before `delete _orders[body.commitment][TRANSACTION_FEES]`: [2](#0-1) 

By contrast, the shared/reference EVM implementation used by `IntrinsicIntents`/`ExtrinsicIntents` (`IntentsBase.sol::_withdraw`) explicitly decrements the escrow **before** sending value or calling `safeTransfer`, precisely to prevent a reentrant call from observing stale escrow state: [3](#0-2) 

The order's input tokens (`body.tokens[i].token`) originate from `order.inputs`, which is attacker-controlled at `placeOrder` time — a user can register an arbitrary ERC-20/malicious contract as an input asset. When that order is later refunded or redeemed, `withdraw()` calls this attacker-supplied contract via a raw `.call`, handing it execution control while `_orders[commitment][token]` (and the fee pool `_orders[commitment][TRANSACTION_FEES]`) still reflect pre-transfer balances for the remainder of the loop.

Additionally, this function uses raw low-level `.call` with the `IERC20.transfer` selector instead of `SafeERC20.safeTransfer` used elsewhere in the codebase, so non-standard return values are not validated with the same rigor as the primary EVM contracts.

### Impact Explanation
This is the same defect class the codebase has already identified and fixed elsewhere (see `IntrinsicIntentsReentrancyTest.sol`, which documents and tests the CEI fix for `_fillSameChain`/`_fillCrossChain`). The Tron deployment's `withdraw` was not brought in line with that fix: multi-token withdrawals and the fee sweep still mutate accounting *after* handing control to an attacker-influenced contract, which is the exact anti-pattern (state mutated on the far side of an externally-triggerable interruption) that the reference `_withdraw` implementation, and the reentrancy tests, were written to eliminate.

### Likelihood Explanation
`withdraw` is only invoked through `onAccept`/`onGetResponse`, which are gated `onlyHost`/require `authenticate()` against a registered counterpart gateway, so a fully permissionless direct attack is not immediately demonstrable without a compromised or malicious counterpart deployment. However, the underlying storage-ordering bug is present in shipped code, contradicts the pattern already fixed and regression-tested in the primary EVM `IntentGatewayV2`/`IntentsBase` contracts, and represents exactly the reachable-message-handler class in scope (token bridger / escrow release path).

### Recommendation
Bring `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw` in line with `IntentsBase.sol::_withdraw`: decrement `_orders[body.commitment][token]` (and delete/zero the `TRANSACTION_FEES` entry) before performing any external call, and replace the raw `.call` + selector pattern with `SafeERC20.safeTransfer` for consistent revert-on-failure semantics.

### Proof of Concept
1. Attacker calls `placeOrder` on the source chain with an `Order.inputs` entry pointing to a malicious ERC-20-like contract they control (`MaliciousToken`), alongside a second legitimate token, and lets the order proceed to a refund/redeem path (`RefundEscrow`/`RedeemEscrow`).
2. On delivery, `onAccept`/`onGetResponse` calls `withdraw(body, ...)`.
3. In the loop, `MaliciousToken.transfer(beneficiary, amount)` is invoked via `.call` before `_orders[commitment][MaliciousToken]` is decremented and before the second token / fee entries are touched.
4. `MaliciousToken.transfer` executes attacker logic while the escrow bookkeeping for the remaining loop entries is still stale, demonstrating the CEI violation contrasted with the fixed `_withdraw` in `IntentsBase.sol`.

### Citations

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L460-470)
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
