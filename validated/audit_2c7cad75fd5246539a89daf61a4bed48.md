### Title
Unsafe/unchecked ERC20 return value in `IntentGatewayV2.withdraw()` and `SweepDust` handling silently drops payouts while decrementing escrow accounting - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` pays out escrowed order tokens, transaction fees, and dust using a raw low-level `.call()` to the ERC20 `transfer` function, and only checks that the call itself did not revert (`success`), never inspecting the ABI-decoded boolean return value of `transfer`. This is the exact bug class flagged in the referenced Sherlock report for `BetaProvider.sol` (unchecked ERC20 transfer return value), reachable here through the unprivileged, relayer-delivered `onAccept`/`withdraw` path of the intents settlement flow.

### Finding Description
In `withdraw()`, which is invoked from `onAccept`/`onGetResponse` when a relayer delivers a `WithdrawalRequest` (fill or refund) for an intent order, and in the `SweepDust` request handler, payouts to the beneficiary are performed with: [1](#0-0) 

and similarly for transaction fee redemption: [2](#0-1) 

and for dust sweeping: [3](#0-2) 

In all three cases, only the low-level call's `success` boolean (whether the call reverted) is checked; the returned `bytes` payload — which per ERC20 should encode a `bool` indicating whether the transfer actually succeeded — is discarded (`(bool success,)`). Many real-world and non-standard ERC20 tokens (e.g., tokens that return `false` on failure instead of reverting, or tokens with quirky/partial return data) will make this call return `success = true` even though no tokens were actually moved.

Directly afterward, the contract unconditionally decrements the internal escrow accounting regardless of whether the transfer actually delivered funds: [4](#0-3) 

and marks the order as filled/refunded via `_filled[body.commitment] = beneficiary` before the loop even begins: [5](#0-4) 

For comparison, the escrow (deposit) side of the same contract correctly uses `SafeERC20.safeTransferFrom`, which reverts on a falsy return value: [6](#0-5) 
but the payout side reverts to unchecked raw calls, breaking the safety guarantee that `SafeERC20` is meant to provide elsewhere in the same file.

### Impact Explanation
Because escrow bookkeeping (`_orders[commitment][token]`) and the `_filled` mapping are updated as if the transfer succeeded, a beneficiary whose token transfer silently fails (returns `false`) will never receive the underlying tokens, yet the order is marked filled/refunded and the escrowed balance is destroyed. The tokens become permanently stuck in the `IntentGatewayV2` contract with no way for the beneficiary to reclaim them (the commitment can't be re-withdrawn because `_orders[...][token]` is already zeroed and `_filled` is already set). This is a straightforward theft/permanent-freezing-of-funds impact for any intents order settled with a non-reverting, falsy-return ERC20 token (or a token whose `transfer` return value truncates/malforms in a Tron/TVM ABI-encoding edge case).

### Likelihood Explanation
The `withdraw()`/`SweepDust` code path is reached whenever any relayer delivers a valid ISMP response/POST for an intent fill, refund, or dust sweep — an ordinary, permissionless part of the intents lifecycle that every solver/relayer/order flow depends on. No special privilege is required beyond normal message delivery; the only prerequisite is that the escrowed/fee token behaves like a non-reverting ERC20 (return `false` on failure) rather than reverting, which is common among widely used tokens (e.g., many that predate strict ERC20 revert semantics) and is realistically deployable on Tron's TRC20 ecosystem where this contract is specifically meant to run.

### Recommendation
Replace all three raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` payout sites in `withdraw()` and the `SweepDust` handler with `SafeERC20.safeTransfer`, consistent with how the deposit side already uses `safeTransferFrom`. This ensures a falsy or malformed return value reverts the whole operation instead of allowing escrow state to advance without the funds actually moving.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an escrow/fee token that implements ERC20 but returns `false` on a failed `transfer` (e.g., due to insufficient balance in a corner case, blacklist, or pausable state) rather than reverting.
2. Create and fill/refund an intent order such that `withdraw()` is invoked with this token as one of `body.tokens`.
3. Have the token's `transfer` call return `false` (call succeeds, no revert, but the boolean payload is `false`).
4. Observe: `(bool success,) = token.call(...)` yields `success == true` because the low-level call didn't revert; `_orders[body.commitment][token] -= amount` executes normally, and `_filled[body.commitment] = beneficiary` is already set.
5. The beneficiary's token balance did not increase, but the contract's internal accounting and `_filled` state indicate the order was successfully settled — the tokens are now unrecoverable, confirming permanent loss of funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L459-459)
```text
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-693)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-708)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L710-710)
```text
            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
