This confirms the fee token is USDT on TRON mainnet, which is a known non-standard ERC20/TRC20 token whose `transfer` can return `false` on failure instead of reverting. The `IntentGatewayV2.sol` (Tron variant) `withdraw()` and `onAccept` (`SweepDust`) functions perform low-level `.call()` to `transfer`, checking only that the *external call* succeeded (`success`), not that the returned ABI-encoded boolean is `true`. This is the exact analog of the reported `AuctionHouse.vy` bug: the transfer's boolean return value is never inspected/decoded.

### Title
Unchecked ERC20/TRC20 `transfer` return value in escrow withdrawal permanently burns user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.sol` on the Tron deployment settles escrowed order funds and swept protocol dust using raw low-level `.call()` invocations of `IERC20.transfer`, but only checks that the call itself did not revert (`success`). It never decodes and validates the returned `bool` payload. Tokens that return `false` on failure instead of reverting (a common TRC20/legacy-ERC20 pattern, and explicitly the deployment's own configured `FEE_TOKEN`, USDT) will silently fail to move funds while the contract proceeds as if the transfer succeeded.

### Finding Description
In `withdraw()`, escrowed balances are decremented and marked `_filled`/settled regardless of whether the underlying token transfer actually delivered funds: [1](#0-0) 

The same unchecked pattern is used for sweeping accumulated protocol dust to a beneficiary via `SweepDust`: [2](#0-1) 

The contract even imports `SafeERC20`/`IERC20` and uses `safeTransferFrom` in the deposit path (`fillOrder`'s escrow-in logic), showing awareness of the wrap-and-check pattern, but `withdraw()` (the fund-out path) bypasses `SafeERC20` entirely in favor of a manual `.call` that only checks `success`, not `abi.decode(data, (bool))`: [3](#0-2) 

Because TVM/TRC20 tokens (and USDT specifically, which the README designates as the deployment's `FEE_TOKEN`) can return `false` from `transfer()` on failure without reverting, `success` will be `true` even though no tokens moved. `_orders[body.commitment][token]` is still decremented and `_filled[body.commitment]` is still set, permanently marking the order as settled with no path for the beneficiary to reclaim the escrowed tokens.

### Impact Explanation
Once `withdraw()` runs to completion, `_orders[commitment][token]` is zeroed and `_filled[commitment]` is set to the beneficiary, so the escrow is treated as fully settled. If the token transfer silently failed (returned `false`), the beneficiary — the original user (on refund/cancel) or the solver (on redeem) — permanently loses the escrowed funds with no retry or recovery mechanism, since the accounting no longer reflects any outstanding balance. This is concrete, permanent loss of user/solver funds, matching the High severity of the analog report.

### Likelihood Explanation
This is reachable by any user or solver going through the normal intent lifecycle (`placeOrder` → `cancelOrder`/`fillOrder` → cross-chain settlement `onAccept`/`onGetResponse` → `withdraw`), requiring no privileged role. The trigger condition is simply that the configured input/output/fee token (explicitly USDT per the Tron README) or any other non-compliant token returns `false` instead of reverting on transfer failure (e.g., insufficient balance in an edge case, blacklist checks, or paused token state) — a realistic and well-documented ERC20/TRC20 quirk.

### Recommendation
Decode and assert the boolean return value (or adopt `SafeERC20.safeTransfer`, consistent with the escrow-in path and with the non-Tron `IntentGatewayV2.sol`/`IntentsBase.sol` implementations) in `withdraw()` and the `SweepDust` handler, e.g.:
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length > 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
Better, replace the raw `.call` pattern in `withdraw()`/`SweepDust` with `SafeERC20.safeTransfer`, matching the pattern already used in `IntentsBase.sol`'s `_withdraw()`.

### Proof of Concept
1. Deploy `IntentGatewayV2` on TRON with `FEE_TOKEN` set to USDT (per deployment README) or any TRC20 token that returns `false` rather than reverting on failed transfers.
2. A user places an order and escrows tokens; the order is later cancelled/refunded or filled such that `onAccept`/`onGetResponse` triggers `withdraw()`.
3. Engineer (or naturally trigger) a condition where the token's `transfer()` call returns `false` (e.g., token temporarily paused, sanctions/blacklist hook, or non-standard token integrated later) while still returning successfully (not reverting). [4](#0-3) 
4. `success` is `true` (call didn't revert), so execution proceeds: `_orders[body.commitment][token] -= amount` runs and `_filled[body.commitment]` is set — the escrow is marked closed even though the beneficiary received nothing.
5. The beneficiary has no way to retry or reclaim the funds; they are permanently lost from the beneficiary's perspective while the protocol's internal accounting shows the order as fully and correctly settled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L55-56)
```text
contract IntentGatewayV2 is HyperApp, EIP712 {
    using SafeERC20 for IERC20;
```

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
