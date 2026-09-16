Confirmed vulnerability. The `withdraw()` function (reachable via any user's `RedeemEscrow`/`RefundEscrow` settlement) and the `SweepDust` branch of `onAccept()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` use raw low-level `.call()` with `IERC20.transfer.selector`, checking only that the call didn't revert — not the ERC20 boolean return value. This deviates from the rest of the same file (and the mainline `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`) which correctly use OpenZeppelin's `safeTransfer`/`safeTransferFrom` that decode and enforce the return value.

### Title
Escrow withdrawal accepts failed ERC20 `transfer()` as success, permanently freezing user/solver funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` handling branch inside `onAccept()` release escrowed ERC20 tokens using a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))`, only checking that the external call did not revert (`success`). They never decode or check the ABI-encoded boolean return value of `transfer()`. Any ERC20 that follows the strict spec and returns `false` on failure instead of reverting (e.g. paused/blacklist-gated tokens, tokens with balance/allowance edge-case guards, non-standard tokens) will report a truthy `success` while `transfer` internally returned `false`, silently failing to move funds.

### Finding Description
`withdraw()` decrements `_orders[body.commitment][token]` and marks the order `_filled` regardless of whether the token transfer actually delivered funds: [1](#0-0) 
```
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
...
_orders[body.commitment][token] -= amount;
```
The same manual-call pattern (without checking the returned bool) is also used for transaction fee release and for the `SweepDust` branch: [2](#0-1) [3](#0-2) 

This is inconsistent with the rest of the codebase: `placeOrder()` in the same file uses `IERC20(token).safeTransferFrom(...)` from OpenZeppelin's `SafeERC20`, which reverts on a `false` return, and the canonical (non-Tron) equivalent `_withdraw()` in `IntentsBase.sol` correctly uses `safeTransfer`: [4](#0-3) 

`withdraw()` is reached whenever a `RedeemEscrow` or `RefundEscrow` ISMP message is authenticated and delivered via `onAccept()` — a path triggered by ordinary users placing orders and solvers filling them cross-chain, then relayed by any relayer: [5](#0-4) 

### Impact Explanation
If the escrowed token returns `false` instead of reverting on a failed transfer (a legitimate, spec-compliant ERC20 behavior), `withdraw()` will treat the payout as successful: it decrements the internal escrow accounting and marks the order filled/refunded, but the beneficiary (solver or user) never receives the tokens. The tokens remain stuck in the `IntentGatewayV2` contract with no accounting path left to reclaim them, since `_orders[...]` has already been decremented and the order is marked `_filled`. This is a permanent loss/freezing of escrowed user or solver funds, matching a Medium/High severity impact depending on token value at stake.

### Likelihood Explanation
This triggers deterministically for any listed/escrowed token whose `transfer()` implementation returns `false` on failure rather than reverting (a valid ERC20 behavior explicitly called out in the referenced report), or in edge cases like paused/blacklisted recipients. Given IntentGateway is designed to be permissionless with arbitrary user-specified `TokenInfo.token` addresses, an attacker or unlucky combination of token address + recipient state can realistically trigger this on the settlement path for any order.

### Recommendation
Replace the manual `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` (both the token loop and the transaction-fee release) and in the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer`, consistent with the rest of the contract (`safeTransferFrom` is already used via `using SafeERC20 for IERC20;`). This ensures both call-success and boolean-return-value checks are enforced.

### Proof of Concept
1. Deploy or use an ERC20 token (as `TokenInfo.token`) whose `transfer()` returns `false` on failure instead of reverting (e.g., a token that returns `false` when the recipient is blacklisted, or a minimal spec-compliant token intentionally crafted this way).
2. A user places an order escrowing this token via `placeOrder()` (uses `safeTransferFrom`, succeeds normally).
3. A solver fills the order cross-chain; Hyperbridge relays a `RedeemEscrow` message back to the source chain.
4. `onAccept()` → `withdraw()` calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`. The external call itself does not revert (`success == true`) even though `transfer()` internally returned `false` (e.g., beneficiary is blacklisted at settlement time).
5. `_orders[commitment][token] -= amount` executes, and `_filled[commitment] = beneficiary` is set — the order is marked complete — but the beneficiary never received the tokens, which remain locked in the contract with no valid escrow entry to redeem them again.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-714)
```text
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
