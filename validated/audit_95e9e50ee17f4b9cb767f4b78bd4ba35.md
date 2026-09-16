### Title
Checks-Effects-Interactions violation in `IntentGatewayV2.withdraw()` (Tron) — state cleared after external token transfer - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` contains the exact bug class described in the referenced Sherlock finding: `withdraw()` performs external token transfers and *then* mutates the escrow-accounting state that guards those transfers, instead of updating state first. This is the same pattern later fixed in the canonical EVM implementation (`IntentsBase.sol::_withdraw`), but the Tron fork was never updated to match.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::withdraw()`: [1](#0-0) 

each escrowed token is transferred to the beneficiary via a raw `.call` **before** `_orders[body.commitment][token]` is decremented:
```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    ...
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    ...
}
_orders[body.commitment][token] -= amount;   // effect happens AFTER the external interaction
```

The transaction-fee payout has the identical ordering problem: [2](#0-1) 

```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];   // deleted AFTER the transfer, same as `delete sherRewards_[_id]` after `sher.safeTransfer` in the reference report
```

This is the precise anti-pattern named in the reference report: an external transfer occurs, then the corresponding accounting entry is cleared/decremented. Compare this to the audited, CEI-compliant sibling implementation in the main EVM contract, `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`, which was hardened to decrement/delete state *before* transferring: [3](#0-2) 

The `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol` suite documents that this exact class of bug ("beneficiary re-enters during token transfer") was previously present and fixed on the mainline EVM `IntentGatewayV2` by moving `_filled[commitment] = msg.sender` before any external call. The Tron variant's `withdraw()` does set `_filled[body.commitment] = beneficiary` before the per-token loop, which blocks reentry through the only other unauthenticated public entry point that checks `_filled` (`cancelOrder`), but it does **not** carry the fix through to the escrow (`_orders[...][token]`) and fee (`_orders[...][TRANSACTION_FEES]`) accounting itself — those remain mutated only after the external calls complete.

### Impact Explanation
For a same-chain order, the order creator fully controls which ERC-20 contracts are escrowed as `order.inputs[i].token`. A malicious/hookable token (e.g., one with an ERC-777-style `tokensReceived` callback registered by the beneficiary) can reenter the gateway mid-transfer. Because state mutation trails the transfer, any code path that is added, forgotten, or that fails to check `_filled` before touching `_orders[commitment][...]` would allow the same escrow slot to be paid out more than once. Notably, `onAccept`'s dispatch of `RedeemEscrow`/`RefundEscrow` calls `withdraw()` directly without checking `_filled[commitment]` first (only `cancelOrder` does), so the invariant that prevents double-payment currently rests entirely on the ordering of a single loop rather than on an explicit state guard — a fragile, easily broken protection compared to the CEI-safe mainline contract.

### Likelihood Explanation
Currently, the only unauthenticated entry point that could be used to reenter the vulnerable window (`cancelOrder`) is blocked because `_filled[commitment]` is set before the loop begins, and the other entry points (`onAccept`, `onGetResponse`) are `onlyHost`-gated, with the host itself following checks-effects-interactions by writing the request receipt before invoking `onAccept`. This limits practical exploitability today, but the code is a direct, unmitigated regression of a bug class the team has already identified and fixed once (per `IntrinsicIntentsReentrancyTest.sol`) — the safety property depends on incidental ordering rather than an explicit invariant, so any future change to `onAccept`, addition of a new caller of `withdraw()`, or use of a non-standard escrowed/fee token creates direct exposure to fund drainage.

### Recommendation
Apply the same checks-effects-interactions fix used in `IntentsBase.sol::_withdraw` to the Tron `IntentGatewayV2.withdraw()`: decrement `_orders[body.commitment][token]` and `delete _orders[body.commitment][TRANSACTION_FEES]` *before* performing the corresponding external transfer, for both the per-token loop and the fee payout.

### Proof of Concept
1. Attacker deploys a malicious ERC-20 with a transfer hook that calls back into the attacker's own logic on `transfer()`.
2. Attacker calls `placeOrder()` for a same-chain order using the malicious token as an input, plus one legitimate token, escrowing both.
3. Attacker calls `cancelOrder()` (permitted — they are `order.user`), which invokes `withdraw(body, true)`.
4. During the loop, the malicious token's `transfer()` triggers attacker-controlled code before `_orders[commitment][token] -= amount` executes.
5. Today, the attacker's reentrant call into `cancelOrder` for the same commitment reverts (`_filled` already set), and `onAccept`/`onGetResponse` cannot be called directly (`onlyHost`) — demonstrating the bug is latent rather than actively drainable through any presently-reachable path, but confirming the missing effects-before-interactions ordering that the reference report flags as the root cause.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-477)
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

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```
