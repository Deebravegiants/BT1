### Title
Unchecked ERC20 return-data boolean in `IntentGatewayV2.withdraw()`/`onAccept` sweep allows silent transfer failure to be treated as success - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` performs escrow token payouts and dust-sweeping with raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the outer call's `success` flag, never decoding/validating the returned boolean data. This is the same bug class as the reported "some token transfers have no return value" issue, but inverted in effect: it does not revert on non-standard no-return tokens (good), but it also does not validate that a token which *does* return a boolean actually returned `true`. Tokens that return `false` on failure instead of reverting (a well-known non-standard ERC20 behavior) will make `success` (the low-level call outcome) `true` even though no tokens moved, since the call itself doesn't revert — only the encoded return value would be `false`.

### Finding Description
In `withdraw()`, escrowed token payouts to the beneficiary are performed as: [1](#0-0) 

and fee redemption: [2](#0-1) 

and dust sweeping via governance-originated `SweepDust` requests: [3](#0-2) 

In every case the code does `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, to, amount)); if (!success) revert TransferFailed();`. The `success` variable here only reflects whether the low-level call reverted — it says nothing about the ABI-decoded boolean return value that many ERC20 implementations use to signal transfer failure (e.g., returning `false` instead of reverting on insufficient balance edge cases, blacklists, or paused states). Because the returned bytes are discarded (the second tuple element is unused), a token that returns `false` will still cause `withdraw()`/`SweepDust` to mark `_filled[body.commitment] = beneficiary`, decrement `_orders[...]`, and emit `EscrowReleased`/`EscrowRefunded`/`DustSwept` events as if the transfer succeeded — even though the beneficiary received nothing.

This directly parallels the reported bug's root cause (blind trust in a transfer outcome without proper validation), but manifests through the opposite failure mode of a non-reverting `false`-return token rather than a no-return token.

### Impact Explanation
`withdraw()` is the exit path for the escrow that holds all user/solver deposits placed via `placeOrder`/`newOrder` on the Tron `IntentGatewayV2`. If the escrowed asset is (or later becomes) a token whose `transfer()` can return `false` without reverting, `withdraw()` will:
- Permanently record the commitment as filled (`_filled[body.commitment] = beneficiary`) and decrement the internal escrow accounting (`_orders[body.commitment][token] -= amount`) without the beneficiary actually receiving funds, causing a permanent loss/freezing of the escrowed funds (they remain locked in the contract with no accounting entry left to redeem them).
- Emit `EscrowReleased`/`EscrowRefunded` events that relayers and downstream systems (fillers, solvers, UI) will treat as a successful settlement, propagating incorrect state about fund delivery.

This satisfies "concrete theft or permanent freezing of funds" from an unprivileged, ordinary flow (fill/redeem/refund an escrow), since the only requirement is that one of the tokens configured for the gateway's orders exhibits this non-reverting-false-return behavior.

### Likelihood Explanation
Likelihood depends on whether any token whitelisted/used with the Tron `IntentGatewayV2` implements non-reverting `false`-returning transfers (a known real-world pattern, distinct from but related to the USDT no-return-value pattern cited in the source report). Given intents-based gateways are typically designed to be token-agnostic (accepting arbitrary ERC20 tokens supplied in `Order.inputs`/`Order.output.assets`), and the contract explicitly avoids `SafeERC20` here (unlike `IntentsBase.sol`/main `IntentGatewayV2.sol`, which use `safeTransferFrom`), the exposure is real whenever a non-conforming token is used on this Tron deployment.

### Recommendation
Decode and check the boolean return value in addition to the call success flag, mirroring `SafeERC20`'s semantics (accept both "no return data" and "return data decodes to true"), e.g.:
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length != 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
or simply use `SafeERC20.safeTransfer` (already imported via `using SafeERC20 for IERC20;` in this file) consistently for all escrow payouts and dust sweeps, instead of manual low-level calls.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` with a mock ERC20 whose `transfer()` returns `false` (without reverting) when, e.g., a per-recipient blacklist flag is set (mirrors real non-reverting stablecoin behavior) or when a self-imposed condition fails.
2. Place an order using this token as escrowed input via `newOrder`, so `_orders[commitment][token] = amount` is recorded.
3. Trigger `onAccept` with a `RedeemEscrow`/`RefundEscrow` request for that commitment (authenticated per the existing `authenticate()` check) so `withdraw()` executes.
4. Configure/trigger the mock token to return `false` for this specific transfer (call still succeeds, no revert).
5. Observe: `withdraw()` does not revert, `_filled[commitment]` is set, `_orders[commitment][token]` is decremented to 0, and `EscrowReleased`/`EscrowRefunded` is emitted — yet the beneficiary's token balance is unchanged, permanently freezing the funds inside the contract with no remaining accounting path to reclaim them.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-714)
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
