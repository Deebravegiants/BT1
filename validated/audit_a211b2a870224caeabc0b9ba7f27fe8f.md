### Title
Withdraw/SweepDust in Tron `IntentGatewayV2` Check Only Call Success, Not the Decoded ERC-20 Return Value - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` deliberately imports `SafeERC20` and uses `IERC20.safeTransferFrom`/`IERC20.safeTransfer` for escrow *deposits* (`placeOrder`), but its escrow *withdrawal* path (`withdraw()`, reached via `RedeemEscrow`/`RefundEscrow`/`onGetResponse`) and the governance `SweepDust` handler instead build raw low-level calls and only check that the call itself did not revert, never decoding/validating the ERC-20 `transfer` boolean return value.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, `withdraw()` releases escrowed tokens like this: [1](#0-0) 

and the fee payout right after it: [2](#0-1) 

The `SweepDust` governance action has the identical pattern: [3](#0-2) 

In every one of these, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` only checks the outer `bool success` — i.e., that the call did not revert/OOG — but never decodes and checks the ERC-20 function's own `bool` return value. Some ERC-20/TRC-20 tokens (including deployments built with older, non-standard implementations, which are common in the Tron ecosystem this contract explicitly targets) return `false` on a failed transfer instead of reverting. In that case `success` is `true` (the call completed without reverting) even though no tokens moved.

This is the exact bug class described in the referenced report: the return value of a value-moving external call ("withdraw"/"transfer") is not checked, so a partial/failed operation is silently accepted as success. Note the contrast: the sibling EVM contract `IntentsBase.sol` (`_withdraw`) uses `IERC20(token).safeTransfer(beneficiary, amount)` which reverts on a `false` return via OpenZeppelin's `SafeERC20`, correctly closing this gap: [4](#0-3) 

But the Tron contract's `withdraw` and `SweepDust` paths bypass `SafeERC20` (despite importing it and using it for `safeTransferFrom`/on the deposit side) and use raw `.call()` + only-outer-success checks.

Because `withdraw()` unconditionally decrements `_orders[body.commitment][token] -= amount` and marks `_filled[body.commitment] = beneficiary` regardless of whether the underlying token transfer actually delivered funds: [5](#0-4) 

a token that returns `false` instead of reverting causes the escrow accounting to be permanently zeroed out and the order marked filled/refunded — with the beneficiary receiving nothing. There is no retry path (the commitment is consumed), so the escrowed funds for that token become permanently stuck/lost in the contract.

### Impact Explanation
This is reachable from the normal, unprivileged cross-chain intent-fill/refund flow: any solver/relayer that triggers `RedeemEscrow`/`RefundEscrow` (via `authenticate`) or the hyperbridge-relayed `SweepDust` action on the Tron `IntentGatewayV2` deployment can hit this path with any listed token. If that token is a non-standard TRC-20/ERC-20 that returns `false` on failure rather than reverting (e.g., due to a paused state, blacklist, or insufficient contract balance edge case), the escrow bookkeeping is finalized as if the transfer succeeded while the user's/beneficiary's escrowed tokens remain trapped in the contract — a permanent freezing/loss of user funds, matching the "unauthorized app action / permanent freezing of funds" acceptance criteria.

### Likelihood Explanation
Likelihood is Medium: it requires escrowing a non-standard ERC-20/TRC-20 token whose `transfer` can return `false` without reverting (not all tokens behave this way, but this is a well-documented category of tokens, particularly prevalent on networks like Tron where this exact contract is deployed). Given the escrow inputs are user-supplied token addresses at `placeOrder` time, an attacker or unlucky integrator can select such a token and trigger loss of the corresponding escrowed funds on withdrawal/refund.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept` with `SafeERC20.safeTransfer` (already imported and used elsewhere in this file), so a `false` return is treated as a revert instead of being silently accepted, consistent with the EVM `IntentsBase._withdraw` implementation.

### Proof of Concept
1. Deploy/escrow a TRC-20/ERC-20 token in the Tron `IntentGatewayV2` whose `transfer()` implementation returns `false` (rather than reverting) when insufficient balance or another failure condition occurs (e.g., a legacy or misconfigured token, or one deliberately crafted to always return `false`).
2. Place an order via `placeOrder`, escrowing that token: `IERC20(token).safeTransferFrom(...)` succeeds and `_orders[commitment][token] += amount`.
3. Trigger fulfillment/refund so `withdraw(body, isRefund)` is invoked with `body.tokens` including this token and `amount` set such that the token's internal `transfer` logic returns `false` (e.g., contract holds less balance than a bug elsewhere caused, or token enforces some check).
4. `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));` — `success` is `true` because the low-level call didn't revert, even though the ERC-20 `transfer` function's returned `bool` was `false` and no tokens were actually moved.
5. `_orders[body.commitment][token] -= amount;` executes, and `_filled[body.commitment] = beneficiary;` is set — the order is now permanently finalized/consumed with the beneficiary never receiving the tokens, which remain stuck in the `IntentGatewayV2` contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
