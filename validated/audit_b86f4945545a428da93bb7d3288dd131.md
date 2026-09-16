### Title
Non-standard TRC20 tokens silently fail escrow withdrawals in the Tron `IntentGatewayV2`, permanently freezing user/solver funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron deployment of `IntentGatewayV2` releases escrowed tokens via a raw low-level `.call()` to the token's `transfer` selector and only checks that the *call itself* did not revert. Unlike the rest of the codebase, which consistently uses OpenZeppelin's `SafeERC20.safeTransfer` (which also validates the returned boolean when present), this contract ignores the returned data entirely. A non-standard TRC20 token that returns `false` on a failed transfer instead of reverting (e.g. paused/blacklisted transfers, insufficient internal balance, deflationary/fee-taking tokens with edge-case failures) will cause the escrow accounting to be finalized as if the transfer succeeded, while the tokens themselves never leave the contract.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`, the `withdraw()` internal function — invoked from both the `RedeemEscrow`/`RefundEscrow` request-kind handler in `onAccept` and from `onGetResponse` (the GET-response path for order-cancellation queries) — releases escrowed ERC20/TRC20 tokens like this: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the low-level call reverted, not whether the token's internal transfer logic actually succeeded. For any TRC20 implementation that returns `false` (rather than reverting) on a failed transfer, `success` is still `true` — the check passes, `_orders[body.commitment][token]` is decremented, `_filled[body.commitment] = beneficiary` is set, and `EscrowReleased`/`EscrowRefunded` is emitted, even though the beneficiary received nothing.

The same unchecked pattern is used in the `SweepDust` governance branch of `onAccept`: [2](#0-1) 

This is inconsistent with the rest of the contract and the rest of the codebase: the file imports and enables `SafeERC20` (`using SafeERC20 for IERC20;`) and other parts of the protocol — the canonical `IntentsBase._withdraw` on EVM chains, `EvmHost.withdraw`, `SimplexPaymaster`, and the `HyperFungibleToken`/`WrappedHyperFungibleToken` apps — all correctly use `IERC20(token).safeTransfer(...)`, which both checks the call succeeded *and* decodes/validates the returned boolean when returndata is present: [3](#0-2) [4](#0-3) 

Because `withdraw()` marks the order as `_filled` and decrements the escrow bookkeeping unconditionally once the raw call doesn't revert, there is no retry path: once this executes, the commitment can never be withdrawn again (the `UnknownOrder`/`Filled()` guards prevent any second attempt), and the tokens remain stuck in the `IntentGatewayV2` contract forever.

### Impact Explanation
This is a permanent freezing-of-funds bug reachable through the core, unprivileged relayed-message delivery path: any solver/user whose order is settled cross-chain via `RedeemEscrow` or `RefundEscrow` (delivered by any relayer submitting a valid consensus/state proof) or via the `onGetResponse` cancellation-query path can have their escrowed TRC20 input tokens or fee-token proceeds silently swallowed by the contract if the token's `transfer` implementation returns `false` on failure rather than reverting. Because the order is simultaneously marked `_filled` and the internal escrow ledger decremented, there is no recovery mechanism — the tokens are permanently locked with no legitimate withdrawal path, matching a Critical/High severity "permanent freezing of funds" outcome.

### Likelihood Explanation
The trigger condition depends on token behavior (transfer returning `false` instead of reverting), which is not universal for all TRC20 tokens but is a well-documented category of non-standard token implementations (the exact class flagged in the original report for USDT-style tokens). Given `IntentGatewayV2` is a general-purpose intents gateway meant to support arbitrary tokens configured by users/solvers (not just a fixed allowlist of audited tokens), the likelihood of a whitelisted-by-the-market but non-standard-behaving token being used, or of a transfer transiently failing (e.g. a token pausing transfers, hitting a blacklist, or a fee-on-transfer edge case) during withdraw is realistic over the contract's operational lifetime.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and in the `SweepDust` handler with `IERC20(token).safeTransfer(beneficiary, amount)`, consistent with the rest of the codebase (`IntentsBase._withdraw`, `EvmHost.withdraw`, etc.), so that both call failure and an explicit `false` return value cause a revert instead of a silently-finalized, unfunded withdrawal.

### Proof of Concept
1. A TRC20 token `T` is used as an order input/output whose `transfer()` implementation returns `false` (without reverting) when, e.g., the recipient is blacklisted or an internal check fails, instead of reverting like standard ERC20/TRC20 tokens.
2. A user places (or a solver fills) an order denominated in `T`, escrowing funds in `IntentGatewayV2`.
3. A relayer delivers a valid `RedeemEscrow`/`RefundEscrow` message (or the GET-response timeout path resolves) for that commitment, invoking `withdraw()`.
4. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success = true` (call did not revert) even though `T.transfer` internally returned `false` and moved no tokens.
5. `_orders[body.commitment][token] -= amount` executes, `_filled[body.commitment] = beneficiary` is set, and `EscrowReleased`/`EscrowRefunded` is emitted.
6. The beneficiary's TRC20 balance is unchanged, the escrowed tokens remain in the `IntentGatewayV2` contract, and because the commitment is now `_filled`, no further withdrawal for it is possible — the funds are permanently frozen.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
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

**File:** evm/src/core/EvmHost.sol (L651-659)
```text
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
```
