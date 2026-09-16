### Title
`withdraw()` and `SweepDust` handling in `IntentGatewayV2` (Tron) treat a false-returning ERC20 `transfer` as success, permanently burning escrow accounting without delivering funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` uses `SafeERC20`/`safeTransferFrom` for pulling tokens into escrow, but pays escrowed tokens *out* (on fill-redemption, refund, and dust-sweep) via a raw low-level `.call` to the token's `transfer` selector, checking only that the call did not revert — not that the returned boolean is `true`.

### Finding Description
In `withdraw()`, which is invoked from `onAccept` when a relayed `RedeemEscrow`/`RefundEscrow` message is delivered (a standard, unprivileged relayer-driven cross-chain fill/refund path), tokens are paid out like this: [1](#0-0) 

The same unchecked-boolean pattern is used for fee redemption in the same function: [2](#0-1) 

And again in the `SweepDust` branch of `onAccept`, reachable from a Hyperbridge-relayed governance/dust-sweep message: [3](#0-2) 

`(bool success,)` from a raw `.call` only reflects whether the target contract reverted — it does not decode or validate the ABI-encoded `bool` return value of `transfer`. Many real-world ERC20/TRC20 tokens (including well-known Tron-based tokens such as older USDT-TRC20 clones and various non-standard tokens) return `false` on a failed transfer (e.g., due to a paused state, blacklist, or insufficient balance edge case) instead of reverting. For such tokens, `success` will be `true` even though no tokens were actually transferred to `beneficiary`.

Once `success` is (incorrectly) treated as true, the code proceeds to decrement `_orders[body.commitment][token] -= amount` and emit `EscrowReleased`/`EscrowRefunded`/`DustSwept`, permanently marking the escrow as settled. The intended recipient receives nothing, and the escrowed balance is written off — this is functionally identical to the referenced UXDController bug class ("some tokens don't revert but instead return false").

By contrast, the token *pull* side of the same file correctly uses `SafeERC20.safeTransferFrom`, e.g.: [4](#0-3) 
confirming that only the payout path was left unprotected.

### Impact Explanation
This causes a direct, unrecoverable loss of escrowed user funds on a token whose `transfer` returns `false` instead of reverting: the accounting is finalized (`_orders[...] -= amount`, escrow events emitted, `_filled` marked) while the actual token transfer silently fails. There is no retry path once the escrow entry is zeroed out and `_filled` is set, so funds are permanently stuck in the `IntentGatewayV2` contract with no way for the beneficiary to reclaim them. This qualifies as concrete theft/permanent freezing of user funds.

### Likelihood Explanation
Likelihood depends on whether a deployment ever escrows a non-standard token that returns `false` on failure rather than reverting. Given Tron/TRC20 tokens are historically known for exactly this behavior (and the intent-gateway design explicitly supports arbitrary ERC20/TRC20 input/output tokens chosen by users placing orders), this is a realistic risk specific to the Tron variant of the contract, triggered simply by an order or dust sweep involving such a token combined with a transfer-failure condition (e.g., blacklist, pause, insufficient contract-level balance quirks).

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` (both the token loop and the fee-token payout) and in the `SweepDust` branch of `onAccept` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with how `safeTransferFrom` is already used elsewhere in this same file. This ensures any `false` return value or missing return value is treated as a failure and reverts the transaction.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron) with a mock/real token whose `transfer(to, amount)` returns `false` on failure instead of reverting (e.g., simulate a blacklisted recipient or insufficient allowance in the token's own logic while returning `false`).
2. A user places and escrows an order with that token: `_orders[commitment][token] = amount` is set via the normal order-placement flow.
3. A relayer delivers a `RedeemEscrow` (or `RefundEscrow`) request through `onAccept`, which calls `withdraw(body, ...)`.
4. Inside `withdraw`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` executes; the token's internal logic returns `false` (e.g., because the beneficiary is disallowed) but the low-level call itself succeeds (`success == true`).
5. The code decrements `_orders[commitment][token] -= amount` and emits `EscrowReleased`, finalizing settlement, even though `beneficiary` received zero tokens — the funds are now unrecoverable, since the escrow record is zeroed and `_filled[commitment]` is set.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-710)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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
