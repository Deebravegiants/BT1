## Analysis

The Tron variant of `IntentGatewayV2` bypasses OpenZeppelin's `SafeERC20` and instead performs raw low-level calls to `IERC20.transfer`, checking only that the call itself did not revert — never decoding and validating the actual boolean return value the ERC20 standard specifies. This is the exact bug class from the reference report ("doesn't check the result of ERC20.transfer calls"), reachable by any solver/relayer calling `withdraw`/`onAccept` paths in the intents escrow flow.

### Title
Escrow/fee withdrawal in Tron `IntentGatewayV2` treats non-reverting `false`-returning ERC20 transfers as success, permanently freezing/losing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.withdraw` and the `SweepDust` handler in `evm/tron/contracts/apps/IntentGatewayV2.sol` release escrowed order tokens and accumulated fees using a raw low-level `.call()` encoding `IERC20.transfer`, and only check the outer call-success boolean rather than decoding the ERC20 `transfer` return value.

### Finding Description
In `withdraw`, escrowed tokens are released to a beneficiary and the escrow accounting is decremented regardless of whether the actual token transfer succeeded, because only `success` (call-level, i.e. "did not revert") is checked, not the decoded boolean payload of `transfer`: [1](#0-0) 

The same unchecked pattern appears in the `SweepDust` incoming-request handler, which pays out swept dust to a beneficiary: [2](#0-1) 

For any ERC20 implementation that returns `false` on a failed transfer instead of reverting (a still-common, standard-compliant behavior, e.g. many legacy or intentionally defensive tokens), `token.call(...)` will report `success == true` because the call did not revert — the code never inspects the returned `bytes` for the ABI-encoded `bool`. This is precisely the vulnerability class described in the reference report: `_orders[body.commitment][token] -= amount;` (and the fee-escrow decrement) proceed as though tokens were delivered, when in fact zero tokens moved.

By contrast, the standard EVM `IntentGatewayV2` (`evm/src/apps/IntentGatewayV2.sol`) and `IntentsBase.sol`/`IntrinsicIntents.sol`/`ExtrinsicIntents.sol` consistently use `SafeERC20.safeTransfer`/`safeTransferFrom`, which do validate the returned boolean and revert on failure or non-compliant tokens: [3](#0-2) 

The Tron deployment specifically diverges from this pattern for its outbound transfer calls in `withdraw`/`SweepDust`.

### Impact Explanation
Because escrow/fee accounting (`_orders[commitment][token]`, `TRANSACTION_FEES` slot) is decremented and the order is marked `_filled`/finalized unconditionally once the low-level call returns without reverting, a `false`-returning token silently "succeeds": the beneficiary receives no tokens, but the protocol's bookkeeping treats the withdrawal as complete. The escrowed balance is permanently lost (it is decremented from accounting yet never actually transferred out, so it cannot be re-claimed), and the same commitment cannot be withdrawn again since `_filled` and the `_orders` mapping have already been updated. This satisfies "permanent freezing/loss of funds" for order originators, fillers, and relayers relying on this fee/escrow release path.

### Likelihood Explanation
This path is reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow`/`SweepDust` incoming ISMP request, or any user/solver triggering `withdraw` indirectly through normal intent settlement — no privileged role is required. The only precondition is that the escrowed/output token used in an order is a standards-compliant ERC20 that returns `false` rather than reverting on failure (a well-documented, non-exotic behavior class), making this a realistic risk for arbitrary tokens permitted by the intents system rather than a purely theoretical edge case.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw` and the `SweepDust` handler with `SafeERC20.safeTransfer` (already imported and used elsewhere via `using SafeERC20 for IERC20;`), which decodes and validates the ERC20 return value (and handles tokens that return no data at all) before treating the transfer as successful.

### Proof of Concept
1. Register/permit an ERC20 token in an order's `inputs`/`output.assets` whose `transfer` implementation returns `false` on failure instead of reverting (e.g., insufficient allowance/balance edge case that the token contract handles gracefully rather than via `require`).
2. Have a solver fill the order and trigger the `RedeemEscrow` flow so `withdraw` is invoked with that token, under a condition causing the token's internal transfer to fail (e.g., a paused/blacklisted recipient in a token with pause/blacklist support that returns `false` instead of reverting).
3. Observe `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `success == true` (call didn't revert) even though no tokens moved to `beneficiary`.
4. `_orders[body.commitment][token] -= amount;` executes, and `_filled[body.commitment]` is set — the order is marked resolved and cannot be retried, while `beneficiary`'s balance never increased: escrowed funds are permanently lost.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
