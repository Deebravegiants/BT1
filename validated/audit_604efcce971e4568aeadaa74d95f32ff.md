The bug-class from the `Vepoch.sol` report — unchecked ERC20 `transfer`/`transferFrom` return values — has a direct, reachable analog in the Tron variant of the IntentGateway. Unlike the canonical EVM contracts, which use OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom` throughout, the Tron port of `IntentGatewayV2.sol` reimplements token transfers with raw low-level calls that check only that the call didn't revert — not that the ERC20's returned boolean is `true`.

### Title
Unchecked ERC20 Boolean Return in `withdraw()`/`onAccept` Allows Escrow to Be Decremented Without Delivering Tokens - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron `IntentGatewayV2` release escrowed ERC20 tokens using `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` and only check the low-level `success` flag (whether the call reverted), never decoding/verifying the ABI-encoded `bool` return value.

### Finding Description
`withdraw()` is invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` request kinds and from `onGetResponse()` for cancellations — both are message-delivery entry points reachable by any relayer who submits a valid ISMP proof, not privileged actors. [1](#0-0) [2](#0-1) 

Inside `withdraw()`, each escrowed token is paid out via a raw `call` whose only check is `success` (i.e., the call did not revert): [3](#0-2) 

The same pattern is used for the transaction-fee payout and in the `SweepDust` handler: [4](#0-3) [5](#0-4) 

Any ERC20 (or TRC20, which is the actual token standard used on Tron and has multiple non-reverting-on-failure implementations in the wild) that returns `false` instead of reverting on a failed transfer will cause `success` to be `true` even though no tokens were actually delivered. Immediately after, the code still executes `_orders[body.commitment][token] -= amount;`, permanently decrementing the escrow accounting as if the transfer succeeded. Contrast this with the canonical EVM path, `IntentsBase._withdraw`, which correctly uses `SafeERC20.safeTransfer`, which decodes and enforces the boolean return: [6](#0-5) 

### Impact Explanation
Because the escrow balance is unconditionally decremented (and, for `RedeemEscrow`, `_filled[body.commitment]` is unconditionally set) regardless of whether the beneficiary actually received tokens, a silently-failing `transfer()` results in: the solver/beneficiary receiving nothing while the order is marked filled, and the escrowed tokens remaining permanently stuck in the contract (unreachable by any subsequent withdrawal path since `_orders[...][token]` was already reduced and `_filled` finalized). This is a permanent loss/freezing of user or solver funds triggered from a normal cross-chain settlement or cancellation flow.

### Likelihood Explanation
Exploitation requires only that the deployed input/output/fee token used with the Tron `IntentGatewayV2` be one whose `transfer`/`transferFrom` returns `false` on failure instead of reverting (a common, spec-compliant ERC20/TRC20 behavior, e.g. under insufficient balance/allowance edge cases, blacklist/pausable tokens, or fee-on-transfer tokens interacting with rounding). No privileged role is needed — the path is triggered by the normal `onAccept`/`onGetResponse` message-delivery flow that any relayer can submit once a valid proof exists.

### Recommendation
Replace the manual `token.call(...)` + `success`-only check with `SafeERC20.safeTransfer` (already imported and used elsewhere in this same file, e.g. `IERC20(token).safeTransferFrom` in `placeOrder`), consistent with the non-Tron `IntentsBase._withdraw` implementation, for the escrow, fee, and dust-sweep transfers in `withdraw()` and `onAccept()`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an ERC20/TRC20 token `T` whose `transfer()` returns `false` (rather than reverting) when, e.g., the recipient is blacklisted or a transfer-limit is exceeded.
2. A user places a cross-chain order escrowing `T` on the source chain via `placeOrder`.
3. A solver fills the order on the destination chain; the `RedeemEscrow` settlement message is relayed back and delivered via `onAccept` → `withdraw(body, false)`.
4. If `T.transfer(beneficiary, amount)` returns `false` for the beneficiary at that moment (e.g., beneficiary temporarily blacklisted, or contract balance insufficient due to a rounding/fee-on-transfer quirk), `success` from the low-level call is still `true` (call didn't revert), so execution proceeds to `_orders[body.commitment][token] -= amount` and `_filled[body.commitment] = beneficiary`, finalizing the order.
5. The beneficiary never receives the tokens `T`, and the escrow accounting no longer reflects the un-delivered balance — the tokens are permanently stuck in the `IntentGatewayV2` contract with no remaining code path to release them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L718-722)
```text
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
