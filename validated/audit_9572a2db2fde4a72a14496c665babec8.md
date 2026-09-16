### Title
Unchecked low-level ERC20 transfers in Tron `IntentGatewayV2.withdraw`/`SweepDust` can silently fail, permanently freezing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron fork of `IntentGatewayV2` imports and uses `SafeERC20` for inbound token pulls (`safeTransferFrom`) but reverts to raw, unchecked low-level `.call()` invocations of `IERC20.transfer` for outbound payouts in `withdraw()` and the `SweepDust` handler, instead of using `SafeERC20.safeTransfer`.

### Finding Description
In `withdraw()`, escrow release to the beneficiary and fee redemption use a manual low-level call pattern that only checks that the call did not revert, not that the token's return value indicates success: [1](#0-0) 

The `SweepDust` request handler follows the same unchecked pattern: [2](#0-1) 

This differs from the canonical (non-Tron) `IntentsBase._withdraw`, which correctly uses `SafeERC20.safeTransfer`: [3](#0-2) 

`SafeERC20.safeTransfer` protects against two classes of non-standard ERC20 behavior that the manual `token.call(...); require(success)` pattern does not:
1. Tokens that return `false` on failure instead of reverting — the raw `call` succeeds (no revert) even though the transfer did not move any tokens, so `success` is `true` and the code proceeds as if payment was made.
2. Tokens that don't return any data at all are handled correctly by both patterns, so this isn't the concern here — the concern is specifically tokens that *do* return a `bool` and can return `false`.

In `withdraw()`, before the transfer, escrow accounting is already mutated irreversibly: `_filled[body.commitment] = beneficiary;` is set unconditionally at the top of the function, and `_orders[body.commitment][token] -= amount;` is decremented right after the unchecked transfer, regardless of whether the token actually delivered value to the beneficiary. Since `_filled` is a one-time state transition gate for the order (checked elsewhere to prevent re-processing), a beneficiary or fee token that returns `false` on a failed transfer causes the escrowed balance accounting to be wiped out and the order marked as finalized, while the tokens never reach the beneficiary and remain unrecoverable/stuck in the contract.

### Impact Explanation
This is a "vault"-style analog to the original report: production escrow logic transfers ERC20 tokens without validating the boolean return value (the essence of the SafeERC20 fix), on the code path that pays out user/solver funds. Because the escrow bookkeeping (`_orders`, `_filled`) is updated unconditionally alongside the unchecked transfer, a false-returning ERC20 causes the intent gateway to believe payout succeeded and permanently forfeits/locks the underlying escrowed tokens (they stay in the contract balance but the accounting no longer references them, and the order can't be retried since `_filled` is already set). This satisfies the "permanent freezing of funds" impact bar.

### Likelihood Explanation
This path is reachable by any user/solver whose configured input/output/fee token exhibits non-reverting failure semantics (returns `false` instead of reverting), triggered through the normal relayed cross-chain `withdraw` flow (`onAccept`/`onGetResponse` → `withdraw`) or the `SweepDust` administrative request handled via ISMP delivery — i.e., reachable from a single relayed/dispatched message, matching the in-scope reachability requirement (message dispatcher / token bridger paths). It requires a non-standard token configured for the gateway, which is plausible on Tron given TRC20 token heterogeneity, which is exactly why the contract was likely written this way in the first place (to tolerate TRC20 quirks) — but doing so via manual `success`-only checks removes the safety net `SafeERC20` would otherwise provide.

### Recommendation
Replace the manual `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` handler with `IERC20(token).safeTransfer(beneficiary, amount)` (the contract already has `using SafeERC20 for IERC20;` and uses it correctly for inbound transfers), so return-value semantics are enforced consistently for both inbound and outbound transfers.

### Proof of Concept
1. Configure an ERC20/TRC20 token as an input/output/fee token for the Tron `IntentGatewayV2` whose `transfer` function returns `false` on failure (e.g., insufficient balance/blacklist) rather than reverting.
2. Place and fill an order (or trigger `SweepDust`) such that the withdraw/sweep path attempts to pay this token to a beneficiary under a failure condition (e.g., beneficiary is blacklisted by the token, or contract's internal balance tracking diverges).
3. The `token.call(...)` succeeds at the EVM level (no revert) since the token function executes and merely returns `false`; `success` is `true`, so execution proceeds.
4. `_orders[body.commitment][token] -= amount;` and `_filled[body.commitment] = beneficiary;` are committed, finalizing the order with no actual token movement to the beneficiary — the escrowed tokens are now stranded in the contract with no accounting path to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
```text
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-477)
```text
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
