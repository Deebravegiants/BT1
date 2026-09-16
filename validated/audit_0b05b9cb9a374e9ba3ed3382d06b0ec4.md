### Title
Unchecked ERC20 return-value in `IntentGatewayV2.withdraw()`/`SweepDust` treats failed transfers as successful, permanently freezing escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Sherlock report flags `SecondaryRewarder.recover()` for using a typed `IERC20(token).transfer()` call that reverts against tokens which don't return a `bool` (e.g. USDT), permanently blocking recovery of that token. The analogous, reachable defect in this codebase is the mirror-image failure mode of the same root cause — "improper handling of ERC20 `transfer` return data" — in `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `withdraw()` and `SweepDust` handling, which every solver/relayer-submitted order fill or escrow redemption/refund flows through.

### Finding Description
In `withdraw()` [1](#0-0) , escrowed ERC20 tokens are released using a raw low-level call encoding `IERC20.transfer.selector`, checking only that the call itself did not revert:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

This pattern never decodes/validates the returned `bool` from `transfer()`. For any ERC20 implementation that signals failure by returning `false` instead of reverting (a well-documented "weird-ERC20" behavior — the same class of non-standard token behavior the Sherlock report is about), `success` will still be `true` (the low-level call itself did not revert), so the code proceeds as if the transfer succeeded. Immediately after, the escrow accounting is finalized:

```solidity
_orders[body.commitment][token] -= amount;
...
_filled[body.commitment] = beneficiary;
```

The same unchecked pattern recurs for the transaction-fee payout in the same function [2](#0-1) , and in the governance-triggered `SweepDust` handler [3](#0-2) , and again in the predispatch-call dispatcher-sweep path [4](#0-3) .

By contrast, the non-Tron EVM `IntentGatewayV2`/`IntentsBase` implementation correctly uses OpenZeppelin's `safeTransfer`, which decodes and validates the returned boolean: [5](#0-4) . This confirms the Tron variant is the outlier and diverges from the hardened pattern used elsewhere in the same protocol.

### Impact Explanation
`withdraw()` is the escrow-release path reached by an unprivileged solver filling an order (`RedeemEscrow`) or by a refund flow (`RefundEscrow`, `onGetResponse` after a failed-fill proof) — i.e., any submitted intent order that uses a token whose `transfer()` can return `false` on failure instead of reverting. If the transfer silently fails:
- `_orders[commitment][token]` is decremented and `_filled[commitment]` is set as though the beneficiary was paid, even though no tokens moved.
- The user's/solver's escrowed funds become **permanently unrecoverable**: the order is marked filled/refunded, so it can never be retried, and the tokens remain stuck in the contract with no accounting path pointing back to them.
- This constitutes a permanent freezing/loss of user funds on the token-bridging/intents settlement path, reachable from a single relayed message with no privileged actor required.

This meets the Medium/High bar (concrete permanent freezing of funds) requested by the validation criteria.

### Likelihood Explanation
Likelihood is bounded by which ERC20 tokens are configured as intent inputs/outputs for Tron deployments of `IntentGatewayV2`. Any token that returns `false` on failure (rather than reverting) — common among certain audited/older token implementations and some bridged/wrapped tokens on Tron — triggers this path deterministically whenever a transfer legitimately fails (e.g., transient balance/allowance edge cases, blacklist/pause logic in some ERC20s). Because the flow is driven by ordinary solver fill/refund traffic and governance sweep requests, no attacker privilege is required to hit this path; only a non-reverting-failure token needs to be in scope.

### Recommendation
Replace all `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` occurrences in `evm/tron/contracts/apps/IntentGatewayV2.sol` (`withdraw`, `SweepDust`, and the predispatch dispatcher-sweep transfer-call construction) with OpenZeppelin's `SafeERC20.safeTransfer`, matching the pattern already used in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw`. This decodes and enforces the ERC20 return value (or absence thereof) correctly, rejecting both "no return data" (USDT-style) and "returns false" failure tokens instead of silently treating a failed transfer as a success.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with a mock ERC20 whose `transfer()` returns `false` on failure conditions (e.g., insufficient allowance-independent internal check, blacklist, or a simple `MockFailingToken` that always returns `false` without reverting) instead of reverting.
2. A user places an order escrowing this token via `placeOrder`, populating `_orders[commitment][token]`.
3. Trigger `onAccept`/relayed `RedeemEscrow` (or a filler calling the corresponding fill path) so `withdraw()` executes with this token.
4. Have the mock token's `transfer()` return `false` (not revert) for the withdrawal call.
5. Observe: `token.call(...)` returns `success == true` (low-level call succeeded even though the ERC20 semantically failed), so execution continues past `if (!success) revert TransferFailed();`.
6. `_orders[body.commitment][token] -= amount` executes and `_filled[body.commitment] = beneficiary` is set, while `token.balanceOf(address(intentGateway))` is unchanged and the beneficiary never received funds.
7. The order can no longer be retried (already marked filled), and there is no other extraction path for the stuck balance — permanent loss of the escrowed tokens.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L427-435)
```text
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

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
