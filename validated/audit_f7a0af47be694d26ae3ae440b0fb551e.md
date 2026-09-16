## Analysis

The reported bug class — an ERC20 transfer whose failure is not properly checked, causing broken internal accounting and permanently locked funds — has a direct analog in the Tron variant of the Intent Gateway's escrow settlement path.

In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` function (invoked from `onAccept` when a `RedeemEscrow`/`RefundEscrow` message is delivered, and also inline in the `SweepDust` handler) settles ERC20 payouts using a raw low-level call instead of `SafeERC20`: [1](#0-0) 

```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

and identically for fee redemption: [2](#0-1) 

and for `SweepDust`: [3](#0-2) 

`success` here only reflects whether the low-level `.call` itself reverted — it does **not** decode and validate the returned boolean. Non-standard ERC20 tokens that signal failure by returning `false` (instead of reverting) will pass this check even though no tokens were actually moved. Because `_orders[body.commitment][token] -= amount` (escrow debit) unconditionally executes right after, the escrow accounting is permanently decremented while the beneficiary never received the tokens — silently bricking the funds, exactly the failure mode described in the reference report.

By contrast, the primary (non-Tron) EVM `IntentGatewayV2.sol` app uses OpenZeppelin's `SafeERC20.safeTransfer`, which does perform the returndata check and reverts on non-compliant token failures, so it is not affected — this issue is isolated to the Tron contract's manual low-level-call pattern.

### Title
Unchecked ERC20 return value in Tron IntentGatewayV2 `withdraw`/`SweepDust` can brick escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron `IntentGatewayV2` settle ERC20 payouts via a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the external call did not revert (`success`), never decoding/validating the ERC20 boolean return value.

### Finding Description
Non-standard ERC20 tokens (e.g., tokens that return `false` on transfer failure rather than reverting) will make the low-level call succeed (`success == true`) even though the transfer did not occur. Immediately after, the code unconditionally decrements the internal escrow ledger (`_orders[body.commitment][token] -= amount`) or, for `SweepDust`, simply emits an event without any post-transfer verification. This breaks the invariant that on-chain token balances match internal accounting. [4](#0-3) 

### Impact Explanation
This is reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` cross-chain message (via `onAccept` → `authenticate` → `withdraw`), or by Hyperbridge delivering a `SweepDust` instruction — i.e., a standard, permissionless message-delivery path, not an admin/governance action. If the underlying token misbehaves (returns `false` instead of reverting), the beneficiary's escrowed funds are debited from `_orders` but never actually paid out, permanently freezing solver/user funds with no recovery path, matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
Likelihood depends on whether tokens configured as intent inputs/outputs on the Tron deployment include any non-standard ERC20 implementations that return `false` instead of reverting on failure (a known pattern for several legacy/compliance-gated tokens). Given the intent gateway is generic and accepts arbitrary configured tokens across chains, this is a realistic configuration risk rather than a purely theoretical one.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` branch with OpenZeppelin's `SafeERC20.safeTransfer`, matching the approach already used in the primary EVM `IntentGatewayV2.sol`/`IntentsBase.sol`, so that both call-reverts and false-boolean-return failures cause the transaction to revert before escrow accounting is mutated.

### Proof of Concept
1. Configure (or have a solver select) an intent output/input token that implements `transfer` to return `false` on failure instead of reverting (e.g., due to a blocklist or paused state) on the Tron chain.
2. A relayer delivers a `RedeemEscrow` message that resolves to that token/beneficiary combination where the transfer would fail (e.g., beneficiary is blocklisted by the token).
3. `withdraw()` executes `token.call(...)`; the call itself does not revert, so `success == true`, but the token internally returns `false` and moves no funds.
4. `_orders[body.commitment][token] -= amount` still executes, permanently zeroing/reducing the escrow record for that commitment even though the beneficiary received nothing — funds become unrecoverable through the intent gateway's normal flow.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
        }
    }
```
