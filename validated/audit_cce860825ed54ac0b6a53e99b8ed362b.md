## Title
Unchecked ERC20 `transfer()` boolean return value in escrow withdrawal leads to permanent loss of escrowed funds - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron variant of `IntentGatewayV2.sol` release escrowed ERC20 tokens using a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` instead of `SafeERC20.safeTransfer`. The code only checks that the low-level call did not revert (`success`), but never decodes and validates the ABI-encoded `bool` that `ERC20.transfer()` returns. This is the exact bug class described in the external report for `SelfOwnedStETHBurner.sol`: a boolean return value from `transfer()` is produced but never processed.

### Finding Description
In `withdraw()`: [1](#0-0) 

and in the `SweepDust` handling inside `onAccept()`: [2](#0-1) 

both paths do:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
```
`success` only reflects whether the EVM call reverted, not whether the token's internal transfer logic actually moved funds. Many ERC20 implementations (especially older/non-standard tokens) return `false` on failure instead of reverting. For such tokens, `token.call(...)` returns `success = true` with encoded return data `false`, so the guard `if (!success) revert TransferFailed();` never fires.

Immediately afterward, `withdraw()` unconditionally decrements the escrow accounting:
```solidity
_orders[body.commitment][token] -= amount;
```
and, at the top of the function, immediately marks the order filled:
```solidity
_filled[body.commitment] = beneficiary;
```
So even when the underlying token transfer silently failed, the contract's state is updated as if the beneficiary was paid — the escrow slot is emptied and the order is marked filled/redeemed — while the tokens remain stuck in the `IntentGatewayV2` contract's balance, unassociated with any commitment, and unrecoverable through the normal `withdraw`/`cancelOrder` flow (the order is already `_filled`, so calling withdraw or requesting a refund again will hit `UnknownOrder()`).

This contrasts with the sibling EVM implementation, which uses `SafeERC20.safeTransfer` in the equivalent `_withdraw` function of `IntentsBase.sol`, correctly reverting on both call failure and a `false` return value: [3](#0-2) 

The Tron contract diverges from this pattern and reintroduces the unchecked-return-value bug for its escrow release and dust-sweep paths.

### Impact Explanation
Escrowed user funds (`_orders[commitment][token]`) can become permanently frozen: the accounting marks the order `_filled` and zeroes the escrow entry, but the beneficiary never actually receives the tokens if the token's `transfer()` returns `false` without reverting. Because `_filled[commitment]` is already set, subsequent calls to `withdraw`/`cancelOrder` for that commitment cannot recover the funds — the tokens sit permanently stranded in the gateway contract with no state pointing back to them. This is a concrete permanent freezing-of-funds condition triggered by a reachable, unprivileged flow (a normal solver fill/redeem or a governance-triggered dust sweep).

### Likelihood Explanation
The trigger requires a non-standard ERC20 token whitelisted as an order input/output token that returns `false` on transfer failure instead of reverting (a well-known category of non-conforming ERC20 tokens). Given `IntentGatewayV2` is a general-purpose intents/bridge gateway intended to support arbitrary tokens supplied by users/solvers in `order.inputs`/`order.output.assets`, exposure to such tokens is realistic, and the failure path (e.g., transient insufficient allowance/edge-case in a non-standard token's `transfer`) does not require any privileged actor — it can occur during ordinary redeem/refund processing.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer`, matching the pattern already used in `evm/src/apps/intentsv2/IntentsBase.sol`. This ensures both call-level reverts and a `false` boolean return are treated as failures, preventing the contract from marking escrow as released when the underlying transfer did not actually succeed.

### Proof of Concept
1. Configure an order (or a `SweepDust` admin message) whose token is a non-standard ERC20 that returns `false` from `transfer()` on failure (e.g., insufficient balance edge case) rather than reverting.
2. Trigger `withdraw()` via a `RedeemEscrow`/`RefundEscrow` incoming request, or trigger `SweepDust` via a Hyperbridge-authenticated `onAccept` message.
3. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` succeeds at the EVM level (`success == true`) but the beneficiary balance does not increase (token internally returned `false`).
4. `withdraw()` proceeds to set `_filled[commitment] = beneficiary` and decrement `_orders[commitment][token]`, permanently marking the order as settled.
5. The beneficiary never receives the tokens, and because the order is already `_filled`, no further withdrawal/refund attempt for that commitment can succeed — the tokens are permanently stuck in the `IntentGatewayV2` contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
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
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-723)
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
