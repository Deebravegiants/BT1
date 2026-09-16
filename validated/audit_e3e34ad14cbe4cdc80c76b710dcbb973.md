### Title
Unchecked ERC20 `transfer()` return value in Tron `IntentGatewayV2.withdraw()` / `SweepDust` permanently freezes escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron variant of the IntentGateway settle escrowed tokens using a raw low-level `.call()` to `transfer()` and only check that the call itself did not revert (`success`). They never decode/verify the boolean return value that ERC20's `transfer()` is supposed to return, so a token that returns `false` on failure (rather than reverting) will be treated as a successful payout while the escrow accounting is decremented and no tokens actually move.

### Finding Description
In `withdraw()`, escrowed tokens and fees are paid out via:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

`success` here reflects only whether the external call reverted, not whether the token's own `transfer()` logic returned `true`. Per the standard ERC20 interface, a compliant token may return `false` on failure without reverting; `success` will still be `true` in that case because the low-level call itself completed normally. Immediately after this unchecked transfer, the code unconditionally decrements the escrow balance:
```solidity
_orders[body.commitment][token] -= amount;
``` [2](#0-1) 

The same pattern is repeated for the transaction-fee payout in the same function [3](#0-2)  and for the dust-sweep path in `onAccept`'s `SweepDust` branch:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [4](#0-3) 

`withdraw()` is reached from `onAccept`, which is only callable by the host, for `RedeemEscrow`/`RefundEscrow` requests delivered cross-chain after normal proof verification — i.e. it is the standard settlement path for every filled or refunded intent order [5](#0-4) . It is also called directly from `onGetResponse` for the storage-query cancellation flow [6](#0-5) .

By contrast, the canonical (non-Tron) `IntentsBase.sol` implementation uses OpenZeppelin's `SafeERC20.safeTransfer`, which does decode and enforce the boolean return value, correctly reverting on a `transfer()` that returns `false`:
```solidity
IERC20(token).safeTransfer(beneficiary, amount);
``` [7](#0-6) 

The Tron variant deliberately avoids `SafeERC20` (likely due to some TRC20 tokens not returning any data), but the manual `.call()` check it substitutes is incomplete: it never inspects the returned bytes for a `false` boolean, so any ERC20-style token used as an order's input/output/fee token that returns `false` on failure passes this check unnoticed.

### Impact Explanation
Since escrow accounting (`_orders[body.commitment][token] -= amount`) and fee accounting (`delete _orders[body.commitment][TRANSACTION_FEES]`) are updated unconditionally after the unchecked transfer, a silently-failed `transfer()` results in:
- The beneficiary receiving nothing.
- The contract's internal bookkeeping recording the order/fee as fully settled, so the tokens can never be withdrawn again (`UnknownOrder` will trigger on any retry since the escrow entry is now zero/deleted).

The result is a permanent freeze/loss of the escrowed principal and/or fee tokens for any order that uses a non-reverting, return-false-on-failure ERC20 token — a real and reasonably common token behavior pattern. This matches the reported bug class (unchecked `transfer()` return value) and produces concrete, permanent loss of user/solver funds.

### Likelihood Explanation
Exploitability depends on a token used in an order's `inputs`/`outputs`/fee token returning `false` instead of reverting on transfer failure (e.g., insufficient allowance/balance edge cases, blacklist/pausable tokens, or non-standard TRC20/ERC20 implementations common on Tron). Any user, solver, or relayer selecting such a token for an order — which is not restricted to privileged roles — can trigger this path through the normal fill/refund/dust-sweep lifecycle, making it reachable without any special access.

### Recommendation
Replace the manual `.call()` + `success`-only check with OpenZeppelin's `SafeERC20.safeTransfer` (or equivalent) in `withdraw()` and the `SweepDust` branch, decoding and validating the returned boolean data (when present) in addition to checking that the call did not revert:
```solidity
if (!success || (data.length > 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
If the intent is specifically to tolerate TRC20 tokens that return no data, retain the `data.length == 0` exemption but always fail closed when data is returned and decodes to `false`.

### Proof of Concept
1. Deploy a mock ERC20/TRC20 token whose `transfer()` returns `false` on failure (a valid, spec-compliant behavior) instead of reverting, e.g. when the internal balance check fails.
2. Use this token as an order's `output` or `fees` asset in `IntentGatewayV2` (Tron), and drive the transferred balance in the contract to be insufficient at settlement time (e.g., via a race/attack that drains the contract's held balance of that token before `withdraw()` executes, or a token whose `transfer` fails for a recipient-specific reason).
3. Trigger `onAccept` with `RedeemEscrow`/`RefundEscrow`, invoking `withdraw()`.
4. Observe: `token.call(...)` returns `success = true` (call didn't revert) even though the token's `transfer()` internally returned `false` and moved no tokens.
5. `_orders[body.commitment][token] -= amount;` executes, zeroing/decrementing the escrow record.
6. The beneficiary never receives the tokens, and the escrow entry is now consumed, so no future retry/refund can recover them — permanent loss of the escrowed tokens.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-469)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
