### Title
Unchecked ERC20 transfer return value in Tron IntentGatewayV2 `withdraw`/`SweepDust` can finalize escrow and mark orders filled without delivering funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` imports and uses OpenZeppelin's `SafeERC20` for the escrow *inflow* path (`placeOrder`), but for the escrow *outflow* path (`withdraw`) and the governance `SweepDust` handler it bypasses `safeTransfer` and instead performs a raw low-level `.call` with the `IERC20.transfer` selector, checking only that the call did not revert — never decoding/validating the ERC20 boolean return value.

### Finding Description
`withdraw()` and the `SweepDust` branch of `onAccept()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` transfer ERC20 tokens like this: [1](#0-0) [2](#0-1) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```

This only guarantees the external call itself didn't revert; it does not decode `result` to confirm the token actually returned `true`. Per the ERC20 spec, a compliant token is allowed to return `false` on failure instead of reverting. For such a token, `success` will be `true` even though no tokens moved, so the code proceeds as if the transfer succeeded.

Immediately after this unchecked "successful" transfer, `withdraw()` mutates critical protocol state unconditionally: [3](#0-2) 

`_filled[body.commitment] = beneficiary` is set and `_orders[body.commitment][token] -= amount` is decremented regardless of whether the token transfer truly succeeded. This is directly analogous to the reported `cleanToken` bug class (unchecked ERC20 `transfer` return value driving downstream logic/events), except here the downstream effect is state finalization of an escrow withdrawal rather than just an event.

Note the rest of the codebase consistently uses `SafeERC20.safeTransfer`/`safeTransferFrom` (e.g. `IntentsBase.sol` `_withdraw`, `_sweepDust`, and the same Tron file's own `placeOrder` via `IERC20(token).safeTransferFrom`), confirming this raw `.call` pattern in `withdraw`/`SweepDust` is an inconsistency/regression rather than intentional design. [4](#0-3) 

### Impact Explanation
This is reachable from the standard escrow-release path that any relayer can trigger: a `RedeemEscrow`/`RefundEscrow` cross-chain message, or a `GET` response resolved via `onGetResponse` → `withdraw`, both of which are part of the normal intent-fill/cancel flow reachable without special privilege beyond authenticated ISMP delivery. [5](#0-4) [6](#0-5) 

If the escrowed input or output token (which is user-configurable at order-placement time — any ERC20 address can be specified as `order.inputs[i].token`) is one that returns `false` rather than reverting on failure (e.g., due to insufficient contract balance from a prior partial drain, a paused/blacklisted state, or non-standard implementations), the escrow accounting is permanently zeroed and the order is irreversibly marked as filled/refunded — while the beneficiary never actually receives the tokens. Funds become permanently stuck in the gateway contract with no accounting path to reclaim them, since the order can only be withdrawn once (`_filled` check / `_orders[...] == 0` guard prevents retry). This is a permanent freezing/loss of user escrowed funds.

### Likelihood Explanation
Exploitability depends on the specific ERC20 token used for an order returning `false` instead of reverting on transfer failure — this is a real subset of ERC20 tokens in production, and the token address is attacker/user-chosen when placing an order, so an attacker (or a buggy/adversarial token integration) can deliberately target this path. Even absent malicious intent, any legitimate token exhibiting this behavior under any transient failure condition (temporary insufficient balance, blacklist, pause) would trigger silent fund loss for real users.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`IntentsBase.sol`, and this file's own `placeOrder`). `SafeERC20` correctly decodes and enforces the ERC20 return value (or handles tokens that omit a return value entirely), preventing state finalization on a silently-failed transfer.

### Proof of Concept
1. User places an order with `order.inputs[0].token` set to a token contract that implements `transfer` to return `false` on failure instead of reverting (a valid ERC20 pattern).
2. The order is later refunded/redeemed via Hyperbridge, invoking `withdraw()` on the Tron `IntentGatewayV2`.
3. If the token's `transfer` call returns `false` (e.g., contract temporarily has insufficient balance to that specific low-level call context, or the token has some conditional restriction), `token.call(...)` still returns `success = true` because the call did not revert.
4. `withdraw()` proceeds to set `_filled[body.commitment] = beneficiary` and decrement `_orders[body.commitment][token] -= amount`, finalizing the order as fulfilled/refunded.
5. The beneficiary never received the tokens, and since the order state is now finalized, there is no mechanism to retry or recover — the escrowed funds are permanently lost/frozen in the gateway contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-680)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
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
