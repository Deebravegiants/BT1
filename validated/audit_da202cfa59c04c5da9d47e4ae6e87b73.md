### Title
Escrow withdrawal uses low-level `.call` with `IERC20.transfer.selector` instead of `safeTransfer`, allowing silent transfer failures to be treated as success - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.withdraw` on the Tron variant of the IntentGateway pays out escrowed order tokens and protocol fees using a raw low-level `.call` encoded with `IERC20.transfer.selector`, checking only that the call itself did not revert (`success`). It never inspects the ABI-encoded boolean return value that `transfer` is supposed to produce. This is exactly the bug class described in the external report (use of `transfer`/`transferFrom` instead of OpenZeppelin's `safeTransfer`/`safeTransferFrom`), except here it is worse: the code doesn't even call the plain interface method (which would at least revert on a `false`-decoding failure in Solidity's strict-mode ABI decoding for interface calls) — it uses a raw `.call`, so a ERC-20 token that returns `false` on failure (rather than reverting) will make the low-level call succeed while the transfer itself silently fails.

### Finding Description
In `withdraw()`: [1](#0-0) 

the token payout branch does:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
and the same pattern is repeated for fee-token payout at line 720. `success` here only reflects whether the external call reverted — it does not decode/validate the returned `bool` that a compliant ERC-20 `transfer` returns. Any token that returns `false` on failure instead of reverting (a common non-standard-but-legal ERC-20 pattern, e.g. old USDT-style tokens, or any custom token used in escrow output) will cause `success == true` even though no tokens were actually moved.

Immediately after this unchecked "success", the contract decrements the internal escrow accounting (`_orders[body.commitment][token] -= amount;`) and emits `EscrowReleased`/`EscrowRefunded`, permanently marking the order as settled. The `SweepDust` handler in the same contract has the identical pattern: [2](#0-1) 

This contrasts with the rest of the codebase (and the non-Tron `IntentGatewayV2.sol`/`ExtrinsicIntents.sol`), which correctly uses `SafeERC20.safeTransfer`/`safeTransferFrom` for escrow inflows, e.g. `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);` [3](#0-2) , showing the Tron variant's raw `.call` payout path is the outlier and inconsistent with the project's own SafeERC20 usage elsewhere.

### Impact Explanation
This is reachable by any user who places or fills a cross-chain intent order through `IntentGatewayV2` (Tron), an unprivileged, permissionless entry point. If the escrowed output token silently returns `false` on transfer failure (e.g., due to token-specific restrictions, blacklists, insufficient balance edge cases, or non-standard implementations), the escrow contract will:
1. Mark the order as filled/refunded (`_filled[body.commitment] = beneficiary`) and emit success events, misleading off-chain relayers/indexers and the solver/user into believing settlement occurred.
2. Decrement/zero-out `_orders[body.commitment][token]`, permanently erasing the escrow accounting for those funds.
3. Leave the tokens stuck in the contract (unbacked by any escrow record), effectively causing a permanent freeze/loss of funds for the intended beneficiary, since the withdrawal path cannot be retried (the internal accounting has already been debited and the commitment consumed).

This maps to "concrete theft or permanent freezing of funds" via the intents escrow token-bridge redemption path explicitly in scope.

### Likelihood Explanation
Likelihood is **Medium**: it requires a non-standard ERC-20 token (one that returns `false` instead of reverting) to be used as an order input/output/fee token in the Tron IntentGateway deployment. Given IntentGatewayV2 is designed to support arbitrary ERC-20 tokens configured per order (not just a fixed allow-list of well-known assets), and Tron's TRC-20 ecosystem includes tokens with non-standard transfer semantics, this is a realistic, not purely theoretical, scenario for a live deployment. No admin/attacker privilege is required — a normal solver-fill/withdraw flow with an incompatible token triggers the bug.

### Recommendation
Replace the raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` (lines 706 and 720) and in the `SweepDust` handler (line 674) with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the rest of the codebase (`using SafeERC20 for IERC20;` is already imported/used in this same file for `safeTransferFrom`). This guarantees the ABI-encoded return value is checked and reverts atomically on failure, preventing escrow state from being consumed without an actual successful transfer.

### Proof of Concept
1. Deploy (or use an already-deployed) ERC-20/TRC-20 token whose `transfer` function returns `false` on failure instead of reverting (e.g., a token with a paused/blacklist check that returns `false`).
2. A solver fills a cross-chain order using this token as an output/escrow asset via `IntentGatewayV2` (Tron), populating `_orders[commitment][token]`.
3. Before withdrawal, the beneficiary address becomes blacklisted/restricted by the token (or the token's internal check otherwise fails) such that `transfer` returns `false`.
4. The relayer delivers the `RedeemEscrow`/`RefundEscrow` message, `authenticate` passes, and `withdraw()` is invoked:
   - `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(true, abi.encode(false))` — the call succeeds at the EVM level even though the transfer logically failed.
   - `success` is `true`, so `TransferFailed` is never reverted.
   - `_orders[body.commitment][token] -= amount` executes, zeroing out escrow accounting.
   - `EscrowReleased`/`EscrowRefunded` is emitted.
5. Result: the beneficiary never receives the tokens, the tokens remain stuck in the `IntentGatewayV2` contract, and the escrow record is gone — funds are permanently unrecoverable through the normal contract flow.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L320-322)
```text
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
```
