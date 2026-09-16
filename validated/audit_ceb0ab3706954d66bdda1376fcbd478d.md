## Title
Unchecked ERC20 `transfer` return value in Tron `IntentGatewayV2.withdraw()` can permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order tokens via a raw low-level `.call()` to the ERC20 `transfer` selector and only checks that the *call itself* did not revert, never decoding the returned `bool`. Non-standard/non-reverting ERC20 tokens that return `false` on failure (a well-known class on TRC20/Tron and legacy ERC20 tokens) will cause the escrow accounting to be decremented and the order marked filled/refunded while the tokens never actually leave the contract, permanently orphaning them from the beneficiary they were meant for. This mirrors the reported `AaveV2Plugin` bug class: the contract trusts a nominal "amount" to reflect an actual balance movement without verifying the real transfer outcome.

### Finding Description
`IntentGatewayV2.withdraw()` in the Tron deployment iterates over the withdrawal request's tokens and, for ERC20s, performs: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

Only the low-level call's `success` boolean (whether execution reverted) is checked. The ABI-encoded return data (the ERC20 `bool` return value of `transfer`) is never decoded or checked. Tokens that implement `transfer` to return `false` instead of reverting on failure (insufficient balance, blacklist, paused state, etc.) will make this code path proceed as if the transfer succeeded: `success == true`, `_orders[...][token] -= amount` runs, and (in the caller) `_filled[body.commitment] = beneficiary` is set, permanently marking the order settled.

This same unchecked pattern recurs at the other outgoing-transfer sites in the same file (fee disbursement, `SweepDust`, etc.), all using `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` without validating the returned boolean: [2](#0-1) 

By contrast, the mainline EVM `IntentGatewayV2`/`IntentsBase.sol` withdrawal path uses OpenZeppelin's `SafeERC20.safeTransfer`, which explicitly checks the returned boolean and reverts on `false`: [3](#0-2) 

The Tron contract diverges from this safe pattern, reintroducing the class of bug the rest of the codebase deliberately guards against.

### Impact Explanation
Because `_orders[body.commitment][token]` is decremented and the order is marked `_filled`/finalized regardless of whether the token transfer actually succeeded, a beneficiary interacting with such a token (or a token that later becomes non-standard, e.g., through a proxy upgrade, blacklist, or pause) will never receive their tokens, yet the protocol's bookkeeping treats the escrow as fully and correctly settled. There is no retry path: once `_filled` is set and escrow is zeroed, the withdrawal cannot be re-triggered. This is a permanent freezing/loss of user or solver funds reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow` message or GET response for an order using an incompatible ERC20 token — no privileged access is required, only a normal fill/refund flow against a token with non-reverting failure semantics.

### Likelihood Explanation
Likelihood depends on whether such tokens are used as intent inputs/outputs on Tron deployments. TRC20/USDT-style tokens on Tron and various legacy ERC20-style tokens are known to return `false` rather than revert on failure, and the intent gateway is explicitly designed to be token-agnostic (it already handles fee-on-transfer tokens elsewhere in the codebase, showing non-standard tokens are an expected input). Given the contract accepts arbitrary tokens specified in orders, the likelihood of hitting a non-reverting-failure token is realistic on Tron specifically, where this pattern is common practice.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()`, `onAccept()`'s `SweepDust` handler, and the fee-disbursement branch with OpenZeppelin's `SafeERC20.safeTransfer` (as already used in `IntentsBase.sol` and other IntentGatewayV2 code paths), or explicitly decode and check the returned boolean when the call succeeds but returns data:
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length > 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
Only decrement escrow accounting and mark the order filled after confirming the actual transfer succeeded.

### Proof of Concept
1. Deploy a TRC20-style mock token whose `transfer` function returns `false` on failure conditions (e.g., insufficient balance or a blacklisted recipient) instead of reverting, matching real-world non-standard tokens deployed on Tron.
2. Create and fill an intent order that escrows this token in `IntentGatewayV2` (Tron), then trigger a `RedeemEscrow`/`RefundEscrow` delivery (or the `onGetResponse` refund path) targeting a beneficiary for which the mock token's `transfer` returns `false` (e.g., simulate insufficient gateway balance or a blacklisted address).
3. Observe that `withdraw()` does not revert: `success` from the low-level call is `true` even though the encoded return value is `false`, so `_orders[commitment][token] -= amount` executes and `_filled[commitment] = beneficiary` is set.
4. Confirm the beneficiary's on-chain token balance is unchanged (transfer never actually occurred) while the order is now marked filled/refunded and cannot be retried — the tokens are permanently stranded in the contract, inaccessible via any subsequent withdrawal call for that commitment.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-714)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L461-469)
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
