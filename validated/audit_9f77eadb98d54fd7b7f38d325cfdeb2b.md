## Title
`IntentGatewayV2` (Tron) silently drops failed ERC20 transfers by ignoring the `bool` return value instead of using `SafeERC20`, permanently freezing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` imports and uses `SafeERC20` for `placeOrder`'s inbound transfers (`safeTransferFrom`), but the escrow-release paths (`withdraw()` and the `SweepDust` handler) instead perform raw low-level `.call` invocations of `transfer()` and only check that the **call itself** succeeded, discarding the returned boolean that indicates whether the token transfer actually succeeded.

### Finding Description
In `withdraw()`, which is invoked from `onAccept` when a `RedeemEscrow`/`RefundEscrow` message is delivered by any relayer, escrowed tokens are paid out with: [1](#0-0) 

and accumulated fees similarly with: [2](#0-1) 

The `SweepDust` admin-message handler has the same pattern: [3](#0-2) 

In all three cases, `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` only captures whether the low-level call did not revert — it does not decode/verify the returned `bool` from `transfer()`. Any ERC20/TRC20 implementation that returns `false` on failure instead of reverting (a well-known non-compliance pattern, common among Tron TRC20 tokens) will make `success == true` even though no tokens moved. The function then proceeds to decrement escrow accounting (`_orders[body.commitment][token] -= amount;`), delete the fee entry, mark the order `_filled[body.commitment] = beneficiary`, and emit `EscrowReleased`/`DustSwept` as if the transfer succeeded.

This is exactly the bug class from the reference report (`FeeBuyback` using raw `transferFrom`/`approve` without `SafeERC20`) — except here it affects the withdrawal/settlement path of the intents escrow rather than a fee-buyback contract, and the same file (`evm/tron/contracts/apps/IntentGatewayV2.sol`) already imports `SafeERC20`/uses `safeTransferFrom` elsewhere, showing the inconsistency is not a deliberate design choice. Compare with the canonical (non-Tron) implementation, which correctly uses `safeTransfer`: [4](#0-3) 

### Impact Explanation
Once `withdraw()` runs to completion, the escrow bookkeeping for that commitment is finalized/decremented and the order is marked filled — there is no retry path. If the underlying token silently returns `false`, the intended beneficiary (a legitimate solver or user refund recipient) never receives the tokens, yet the contract's internal state says the escrow was already released. The tokens remain permanently locked in the `IntentGatewayV2` contract with no accounting entry pointing to them and no mechanism to reclaim them. This is a permanent freezing/loss of user and solver funds, reachable purely through the normal, permissionless relayed-message delivery path (`onAccept` → `withdraw`) or via a legitimate `SweepDust` governance message paying to a non-compliant token.

### Likelihood Explanation
The Tron deployment of Hyperbridge's Intent Gateway is specifically intended to interoperate with Tron's TRC20 tokens, some of which are known for non-standard ERC20 semantics (return `false` on failure rather than reverting, similar to historical Ethereum tokens like BNB or older USDT variants). Given this contract is deployed to support intents on Tron, encountering at least one input/output token with this behavior is realistic, and every fill/settlement flowing through `withdraw()` for such a token is affected without any special attacker action — solvers/users need only select or be paid out in an affected token.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` invocations in `withdraw()` and the `SweepDust` handler with `IERC20(token).safeTransfer(...)` from OpenZeppelin's `SafeERC20` (already imported and used elsewhere in this same file), so that both non-reverting `false`-returning tokens and non-standard no-return tokens are handled safely and consistently with the rest of the codebase.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a TRC20/ERC20 mock token whose `transfer()` returns `false` on failure instead of reverting (e.g., insufficient balance edge case, blacklist, or paused state).
2. A user places an order escrowing this token via `placeOrder` (uses `safeTransferFrom`, so this step succeeds normally).
3. A relayer delivers a `RedeemEscrow` ISMP message; `onAccept` calls `withdraw(body, false)`.
4. Inside `withdraw`, the token's `transfer()` call returns `false` but does not revert; `token.call(...)` still yields `success == true` because the low-level call did not revert.
5. `_orders[body.commitment][token] -= amount` executes, `_filled[commitment]` is set, and `EscrowReleased` is emitted — but the beneficiary's balance is unchanged and the tokens remain stuck in the `IntentGatewayV2` contract with no accounting path left to recover them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L463-469)
```text

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
