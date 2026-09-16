### Title
Unchecked ERC20 `transfer` return-data on Tron IntentGateway escrow release permanently strands solver/beneficiary funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron `IntentGatewayV2.withdraw()` and the `SweepDust` branch of `onAccept()` release escrowed tokens using a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the *call itself* did not revert (`success`). They never inspect the returned ABI-encoded boolean. Non-reverting ERC20/TRC20 tokens that signal failure by returning `false` (the exact bug class from the referenced Footium report) will pass this check even though no tokens were actually moved, while the contract still decrements its internal escrow accounting and marks the order as settled.

### Finding Description
In `withdraw()`, escrowed input tokens and accumulated transaction fees are released via: [1](#0-0) 

and dust sweeping in `onAccept()`'s `SweepDust` handler uses the identical unchecked pattern: [2](#0-1) 

In both cases, `success` only reflects whether the external call reverted — it does not decode/validate the returned `bool` from `transfer`. Some TRC20/ERC20 tokens do not revert on transfer failure (e.g., insufficient balance) and instead return `false` in the call's return data. Because `success` is `true` for such a call, `TransferFailed()` is never triggered, so execution proceeds to:
- decrement `_orders[body.commitment][token] -= amount;` (escrow accounting reduced as if payment succeeded),
- mark `_filled[body.commitment] = beneficiary;` (order finalized),
- emit `EscrowReleased`/`EscrowRefunded` claiming success.

This is the same root cause identified in the referenced `FootiumPrizeDistributor.transfer()` report: the return value of a token `transfer` call is not validated. Notably, elsewhere in the very same file and in the mainnet `IntentGatewayV2.sol`/`IntentsBase.sol`, deposits and other releases correctly use OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, which decode and check the boolean return value: [3](#0-2) 

demonstrating that the Tron `withdraw()`/`SweepDust` path deviates from the safe pattern used consistently elsewhere in the codebase.

### Impact Explanation
If the escrowed token silently returns `false` on transfer failure (fee-on-transfer token hitting an edge case, blacklisted address, paused/proxy token, or any TRC20 with non-strict return semantics), the beneficiary (solver claiming escrow, or user being refunded) receives nothing, yet:
- the order is irrevocably marked filled/refunded (`_filled[body.commitment] = beneficiary`), preventing any retry through the normal settlement path,
- the escrow balance is decremented, so the tokens effectively become permanently locked/unreachable in the contract (accounting says they were paid out, but they remain in the contract with no path to reclaim them).

This results in permanent loss of solver/user funds — a direct fund-freezing bug reachable by any relayed `RedeemEscrow`/`RefundEscrow` message or an admin-initiated `SweepDust` request once a non-conforming token is involved.

### Likelihood Explanation
Likelihood is bounded by the token in play needing to return `false` instead of reverting. This is a known behavior for certain ERC20/TRC20 implementations (proxy tokens, custom implementations that don't strictly follow OZ semantics, or tokens with edge-case balance/allowance handling). Given IntentGatewayV2 is a general-purpose, permissionless intent settlement contract accepting arbitrary tokens supplied by users when placing orders, an attacker or unlucky integrator can trigger this simply by using such a token as an order input, then relaying the resulting settlement/dust-sweep message.

### Recommendation
Replace the raw `token.call(...)` + `success`-only checks in `withdraw()` and the `SweepDust` branch of `onAccept()` with OpenZeppelin's `SafeERC20.safeTransfer` (already imported and used elsewhere in this file via `using SafeERC20 for IERC20;`), which decodes and validates the boolean return value and reverts on `false`, consistent with the rest of the codebase (e.g., `IntentsBase._withdraw`).

### Proof of Concept
1. A user places an order with a non-standard token `T` whose `transfer` function returns `false` on failure instead of reverting (e.g., insufficient balance due to a rebasing/fee quirk introduced after escrow, or a proxy token temporarily paused).
2. A relayer delivers a valid `RedeemEscrow`/`RefundEscrow` post request; `onAccept()` calls `withdraw(body, isRefund)`.
3. Inside `withdraw()`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` succeeds at the call level but `T.transfer` internally returns `false` without reverting.
4. `success` is `true`, so `TransferFailed()` is not raised; `_orders[body.commitment][token] -= amount` executes, `_filled[body.commitment] = beneficiary` is set, and `EscrowReleased`/`EscrowRefunded` is emitted.
5. The beneficiary never receives tokens `T`, the order can never be retried (already marked filled), and tokens `T` remain stuck in the `IntentGatewayV2` contract with no recovery path — a permanent loss of funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-676)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
