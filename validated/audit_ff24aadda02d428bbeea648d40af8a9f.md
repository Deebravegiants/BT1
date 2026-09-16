### Title
Unchecked ERC20 `transfer` return value in Tron `IntentGatewayV2` can permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed ERC20/TRC20 tokens (in `withdraw`, the `SweepDust` handler, and fee redemption) using a raw low-level `.call` with `abi.encodeWithSelector(IERC20.transfer.selector, ...)`, checking only that the call did not revert (`success`) but never decoding/verifying the returned boolean. This is the same defect class described in the referenced Index Coop finding: tokens that signal transfer failure by returning `false` instead of reverting will pass this check even though no tokens moved, while the protocol's internal escrow accounting is unconditionally decremented as if the transfer succeeded.

### Finding Description
In `withdraw()`, `_orders[body.commitment][token]` is decremented for each token before/without validating that the ERC20 transfer actually moved value: [1](#0-0) 

The same unchecked pattern for the "success but returned false" case exists in `onAccept`'s `SweepDust` branch: [2](#0-1) 

By contrast, the reference EVM implementation in `IntentsBase.sol` (shared by the non-Tron `IntentGatewayV2`) correctly uses `SafeERC20.safeTransfer`, which properly handles both non-reverting tokens that omit a return value and tokens that return `false` on failure: [3](#0-2) [4](#0-3) 

The Tron `IntentGatewayV2` diverges from this safe pattern and only guards against calls that outright revert, not calls that return `success = true` with `returndata` decoding to `false` — exactly the "failure to handle ERC20 transfers" bug class from the referenced report.

### Impact Explanation
`withdraw()` is the escrow release path invoked both for `RedeemEscrow`/`RefundEscrow` after a relayed cross-chain Hyperbridge message (`onAccept`) and for cancellation via `onGetResponse`. If the escrowed token is a TRC20/ERC20 implementation that returns `false` on failed transfer (rather than reverting) — e.g., due to a paused/blacklisted state, insufficient allowance-like internal restriction, or any custom token logic — the `success` flag from the low-level `.call` will still be `true` (the call executed, it just returned `false`), so `TransferFailed` is never raised. The function proceeds to decrement `_orders[body.commitment][token]` and mark the order filled/finalized, even though the beneficiary received nothing. The escrowed tokens remain stuck in the contract with no accounting record left to reclaim them, and the intended recipient (solver or user) never receives their funds — a permanent freezing/loss-of-funds condition. The same issue applies to protocol dust sweeps and fee token redemption in the same function.

### Likelihood Explanation
This path is reachable by any solver filling/redeeming an order or any user cancelling/refunding an order on the Tron deployment — both are core, permissionless flows (`placeOrder`, solver fill, `RedeemEscrow`/`RefundEscrow` triggered by a relayed proof). It only requires that at least one supported input/output token on the Tron `IntentGateway` deployment be a TRC20 token that returns `false` rather than reverting on failure — a common trait for non-standard token implementations, which the protocol cannot control since arbitrary tokens can be used as intent inputs/outputs.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check in `withdraw()` and the `SweepDust` handler of `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the pattern already used in `IntentsBase.sol`. If `SafeERC20` cannot be used due to Tron/TVM compatibility constraints, decode and require the boolean return value when `returndata.length > 0` in addition to checking `success`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a TRC20 token whose `transfer` implementation returns `false` on failure instead of reverting (e.g., because of an internal pause/allow-list check).
2. Place and fill/redeem an order with this token escrowed via `placeOrder`/solver flow.
3. Trigger the token's failure condition (e.g., pause the token) before `withdraw()` is invoked via `RedeemEscrow`.
4. Observe `token.call(...)` returns `success = true` with `returndata` decoding to `false`; `withdraw()` does not revert, decrements `_orders[commitment][token]`, and marks the order filled — the beneficiary never receives tokens, and the escrow accounting can no longer be used to recover them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-723)
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
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L463-470)
```text

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L639-656)
```text
    function _sweepDust(SweepDust memory req) internal {
        uint256 outputsLen = req.outputs.length;
        for (uint256 i; i < outputsLen;) {
            TokenInfo memory info = req.outputs[i];
            address token = address(uint160(uint256(info.token)));
            uint256 amount = info.amount;

            if (token == address(0)) {
                _sendValue(req.beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(req.beneficiary, amount);
            }
            unchecked {
                ++i;
            }
            emit DustSwept(token, amount, req.beneficiary);
        }
    }
```
