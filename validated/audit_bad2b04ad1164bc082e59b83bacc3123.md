### Title
Silent ERC20 transfer failures in Tron `IntentGatewayV2.withdraw()`/`SweepDust` permanently strand escrowed user funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent funds and sweeps protocol dust using raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks that the call did not revert (`success`), without decoding/verifying the returned boolean. Non-compliant ERC20 tokens that return `false` on failure instead of reverting will cause the transfer to silently fail while the contract still marks the order as filled and debits the internal escrow accounting.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the internal `withdraw()` function releases escrowed tokens to a beneficiary: [1](#0-0) 

It performs `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount)); if (!success) revert TransferFailed();` and then unconditionally decrements `_orders[body.commitment][token]`, and does the same for the fee token. `success` only reflects whether the external call reverted, not the ERC20 `transfer` boolean return value. Tokens that follow the non-reverting "return false on failure" pattern (a known class of non-standard ERC20 tokens) will make `success == true` even though no tokens were actually moved, since the return data is never decoded or checked.

The same pattern appears in the `SweepDust` admin-request handler: [2](#0-1) 

This is a real divergence from the pattern used elsewhere in the codebase (e.g. the standard-EVM `IntentsBase.sol` and `IntentGatewayV2.sol` use `SafeERC20.safeTransfer`/`safeTransferFrom`, which reverts on a `false` return): [3](#0-2) 

`withdraw()` is reached directly from the cross-chain `handle()` path for `RedeemEscrow`/`RefundEscrow` requests, which any user (via `authenticate`) or the honest fill/refund flow can trigger: [4](#0-3) 

and also from `onGetResponse`, used when a GET-based liveness/settlement check completes: [5](#0-4) 

### Impact Explanation
Because `_orders[body.commitment][token] -= amount` and `_filled[body.commitment] = beneficiary` execute regardless of whether the underlying token transfer actually moved funds, a silently-failing transfer permanently orphans the escrowed tokens inside the contract: the order's escrow accounting is zeroed out (or the order is marked filled/refunded) so it can never be retried or reclaimed, while the beneficiary receives nothing. This is a permanent freezing/loss of user funds for any input/output token used in the Tron IntentGatewayV2 that exhibits the non-reverting-false-return behavior, satisfying the "permanent freezing of funds" impact bar.

### Likelihood Explanation
Likelihood depends on whether tokens configured for use with the Tron IntentGatewayV2 include any non-standard ERC20 implementation that returns `false` instead of reverting on failure (e.g., due to insufficient balance/allowance edge cases, blacklist/pausable tokens, or bespoke Tron TRC20 tokens with this quirk). Given IntentGatewayV2 is designed to be token-agnostic (any user-supplied ERC20 address can be used as an order input/output), and Tron's TRC20 ecosystem includes several tokens with this non-reverting behavior, the precondition is realistically reachable without any privileged action — it only requires an order involving such a token going through the normal redeem/refund flow.

### Recommendation
Replace the raw `.call` + `success`-only check with `SafeERC20.safeTransfer` (already imported and used via `using SafeERC20 for IERC20;` elsewhere in the same contract) in `withdraw()` and the `SweepDust` handler, so that a `false` return value or missing return data causes an explicit revert rather than a silent no-op.

### Proof of Concept
1. Register/use a non-compliant TRC20 token `T` (returns `false` on failed `transfer` instead of reverting) as an order's input token in `placeOrder`, escrowing `_orders[commitment][T] = amount`.
2. Have Hyperbridge deliver a `RefundEscrow`/`RedeemEscrow` request (or trigger the GET-response path) targeting this order, where `T.transfer(beneficiary, amount)` returns `false` (e.g., because of an internal transfer restriction that doesn't revert).
3. `(bool success,) = token.call(...)` returns `success = true` since the call itself didn't revert; `withdraw()` proceeds to set `_filled[commitment] = beneficiary` and decrement `_orders[commitment][T] -= amount`.
4. The tokens remain locked in the `IntentGatewayV2` contract, the order is marked filled/refunded so it cannot be retried, and the beneficiary never receives their funds — a permanent loss.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
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

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
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
