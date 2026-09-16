This confirms the analog. Compare the two implementations of the same `withdraw` logic:

- The **production/main EVM** version (`evm/src/apps/intentsv2/IntentsBase.sol`) correctly uses OpenZeppelin's `SafeERC20`: `IERC20(token).safeTransfer(beneficiary, amount);` [1](#0-0) 
- The **Tron** deployment target (`evm/tron/contracts/apps/IntentGatewayV2.sol`) reimplements the same escrow-release logic but replaces `safeTransfer` with a raw low-level `.call` that only checks the outer call-success boolean, not the ABI-decoded return value of `transfer`: [2](#0-1) 

The same unchecked pattern is repeated in the `SweepDust` handler in the same file. [3](#0-2) 

### Title
IntentGatewayV2 (Tron) `withdraw`/`SweepDust` accept a false ERC20 `transfer` return as success, permanently freezing escrowed user/solver funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron build of `IntentGatewayV2.sol` release escrowed tokens using a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the external call itself did not revert (`success`). They never decode/verify the boolean return value that ERC20's `transfer` is specified to return. This is the unsafe-transfer bug class the referenced report flags (use `safeTransferFrom`/`safeTransfer` instead of raw `transferFrom`/`transfer`), applied here to the token release path of Hyperbridge's cross-chain intent settlement rather than an NFT release.

### Finding Description
`withdraw(WithdrawalRequest memory body, bool isRefund)` is the function invoked by `onAccept` when a `RedeemEscrow` or `RefundEscrow` ISMP message is delivered from the counterpart `IntentGateway` on another chain (settlement path for cross-chain intent fills), and also from `onGetResponse` for cancellation refunds [2](#0-1) . For every ERC20 token being released it does:

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the low-level call reverted, not whether the token itself reports the transfer succeeded. Tokens that follow ERC20 exactly but return `false` on failure instead of reverting (a well-known and common ERC20 non-conformance) will make this call return `success = true` while no tokens actually moved. The code proceeds to decrement `_orders[body.commitment][token]` and mark `_filled[body.commitment] = beneficiary`, treating the withdrawal as fulfilled and finalizing the order state. The identical unchecked-return pattern is used again for the transaction-fee payout in the same function, and for the `SweepDust` branch of `onAccept` [3](#0-2) .

This is the same root cause the report describes for `CollateralToken._releaseToAddress` — using an unchecked/unsafe transfer primitive on the asset-release path so a failure to actually deliver the asset is silently treated as success. The correct pattern (`safeTransfer`, which decodes and asserts a non-empty return value is `true`, or reverts if none is returned for non-standard tokens) is used correctly elsewhere in the codebase, e.g. the mainline `IntentsBase._withdraw` on other EVM deployments: `IERC20(token).safeTransfer(beneficiary, amount);` [1](#0-0) , confirming this Tron variant is the outlier/regressed copy.

### Impact Explanation
Once `_orders[commitment][token]` is decremented and `_filled[commitment]` is set to the beneficiary, the order is irrevocably marked as settled: there is no other code path to re-attempt the transfer or to reclaim the escrow. If the underlying token silently returns `false` on the release call (e.g., due to an edge case like a blacklist, paused state, or non-standard token behavior that the deploying integration did not anticipate), the escrowed funds remain permanently locked in the `IntentGatewayV2` contract while the protocol's own accounting believes the solver/user was already paid. This is a permanent freezing/loss-of-funds condition reachable by a single cross-chain settlement message (`RedeemEscrow`/`RefundEscrow`) or a `SweepDust` dispatch — both are normal, expected message flows of the Intent Gateway, not privileged or malicious-actor-dependent paths.

### Likelihood Explanation
Likelihood depends on which ERC20 tokens are configured for intents on the Tron deployment; tokens that return `false` instead of reverting on failed transfers are documented ERC20 edge cases (rather than reverting), and any transient failure condition on such a token (e.g., temporary pause, blacklist, insufficient allowance/balance edge racing) triggers the silent-failure state during ordinary settlement processing initiated by relayed ISMP messages — no attacker privilege is required, only the natural flow of order fulfillment/cancellation.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` handler of `evm/tron/contracts/apps/IntentGatewayV2.sol` with OpenZeppelin's `SafeERC20.safeTransfer`, matching the pattern already used in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw`. This ensures a `false` return value from a non-reverting-but-failing ERC20 `transfer` call is treated as a failure and reverts the whole settlement, preventing escrow accounting from being finalized without the funds actually moving.

### Proof of Concept
1. Configure an intent order on the Tron `IntentGatewayV2` deployment using an ERC20 token whose `transfer` implementation returns `false` rather than reverting under some failure condition (e.g., a token with an on-chain pause/blacklist feature triggered between order placement and settlement, or any strict-ERC20 token that just returns `false` on insufficient balance in the gateway due to a prior partial sweep/rounding bug).
2. Have the counterpart gateway on the source/destination chain dispatch a `RedeemEscrow` (or `RefundEscrow`) ISMP POST that reaches `onAccept` → `withdraw()`.
3. Inside `withdraw`, the `token.call(...)` succeeds (returns `success = true` at the call level) even though the token's internal `transfer` logic returned `false` and did not move balance.
4. `_orders[body.commitment][token] -= amount` executes, and `_filled[body.commitment] = beneficiary` is set, permanently finalizing the order.
5. The beneficiary's on-chain token balance never increased, but the escrowed amount is now unrecoverable — no other function permits withdrawing `_orders[commitment][token]` once it's decremented and `_filled` is set.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-681)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-722)
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
```
