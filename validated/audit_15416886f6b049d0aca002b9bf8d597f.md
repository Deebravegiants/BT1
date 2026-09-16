I have enough evidence to confirm the vulnerability. This confirms the exact analog to the M-03 report: `withdraw()` and the `SweepDust` handler in the Tron `IntentGatewayV2.sol` use raw low-level `.call()` with `IERC20.transfer.selector`, checking only that the external call did not revert (`success`), but never inspect/decode the returned boolean data — unlike the rest of the same contract (and other gateway variants) which correctly use `SafeERC20.safeTransferFrom`/`safeTransfer`.

### Title
Unchecked ERC20/TRC20 transfer return value causes silent escrow loss in Tron IntentGatewayV2 `withdraw()`/`SweepDust` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`withdraw()` (invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests) and the `SweepDust` branch of `onAccept()` move tokens out of escrow using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the low-level call did not revert, never decoding the returned `bool`. This is the exact `transfer()`/`transferFrom()` unchecked-return-value bug class from the referenced report, except here it is reachable through Hyperbridge's cross-chain message delivery path, not just a direct user call.

### Finding Description
`onAccept()` is the ISMP handler that Hyperbridge's relayer-delivered `PostRequest`s route into after proof verification [1](#0-0) . For `RedeemEscrow`/`RefundEscrow` kinds it calls internal `withdraw()`, which unconditionally marks the order filled (`_filled[body.commitment] = beneficiary`) and decrements the escrow ledger (`_orders[body.commitment][token] -= amount`) based solely on whether the low-level `.call` reverted, not on the actual boolean return value of the token's `transfer()`: [2](#0-1) 

Any TRC20/ERC20 token that returns `false` on failure instead of reverting (a common non-compliant token behavior, explicitly the scenario the referenced report warns about) will cause `success` to be `true` even though no tokens were actually moved to the beneficiary. The function nonetheless proceeds to decrement the escrow accounting and mark `_filled`, permanently erasing the record that tokens are owed, while the beneficiary never receives them.

The same unchecked pattern also appears in the `SweepDust` handler reachable from the same `onAccept()` entrypoint: [3](#0-2) 

Notably, this same contract already imports and uses `SafeERC20` correctly for the deposit-side flows (`safeTransferFrom` on placeOrder/fillOrder paths, e.g. lines 405, 459, 484), demonstrating the withdrawal path is an inconsistent regression from the safe pattern used elsewhere in the same file and in the non-Tron `IntentGatewayV2.sol`/`IntentsBase.sol` (`evm/src/apps/intentsv2/IntentsBase.sol:468`, `evm/src/apps/intentsv2/IntentGatewayV2.sol:250,321`), which correctly use `safeTransfer`/`safeTransferFrom`.

### Impact Explanation
This results in permanent freezing/loss of user or solver funds: escrowed tokens remain locked in the `IntentGatewayV2` contract (since `_orders[...]` accounting is decremented as if paid out) while the intended beneficiary (user on refund, or solver/filler on redeem) receives nothing. Because `_filled[body.commitment]` is set unconditionally, the withdrawal cannot be retried — the funds are permanently stuck with no recovery path. This is a direct, unbacked loss of escrowed value, matching the High/Critical bar for concrete freezing of funds via a relayed cross-chain settlement message.

### Likelihood Explanation
The path is reachable by any relayer delivering a valid, proven `RedeemEscrow`/`RefundEscrow` post request through the standard Hyperbridge ISMP flow — no privileged or malicious actor is required. The only precondition is that the input/output token used in an intent order is a non-compliant TRC20/ERC20 (returns `false` instead of reverting on failure, e.g. due to insufficient contract balance from a prior partial transfer, blacklist, or paused state) — a realistic condition for a permissionless intents system accepting arbitrary tokens, and explicitly the exact scenario the linked report calls out as the reason to avoid raw `.transfer()`/`.transferFrom()`.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with OpenZeppelin's `SafeERC20.safeTransfer()` (already imported and used elsewhere in this same contract), which reverts on both call failure and a `false` return value, ensuring escrow accounting is only mutated when the transfer actually succeeds.

### Proof of Concept
1. A user places a cross-chain order in `IntentGatewayV2` (Tron) escrowing a non-standard token `T` that returns `false` (rather than reverting) on transfer failure.
2. Order is filled/cancelled on the counterpart chain; a relayer delivers a valid `RedeemEscrow`/`RefundEscrow` `PostRequest` and it passes `authenticate()`.
3. `onAccept()` calls `withdraw(body, isRefund)` [1](#0-0) .
4. Inside `withdraw()`, `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` executes without reverting but token `T` internally returns `false` (e.g., due to a paused/blacklist state or precision-loss self-check) [4](#0-3) .
5. `success` is `true`, so no revert occurs; `_orders[body.commitment][token] -= amount` and `_filled[body.commitment] = beneficiary` are committed, and `EscrowReleased`/`EscrowRefunded` is emitted — even though the beneficiary's token balance never changed.
6. The escrowed tokens are now permanently unreachable: the gateway's internal accounting shows the escrow as paid out, so `withdraw()` cannot be invoked again for this commitment (`_orders[...] == 0` triggers `UnknownOrder()` on any future attempt), and the tokens remain stuck in the contract.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-683)
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
