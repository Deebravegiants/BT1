This confirms the issue is isolated to the Tron variant of `IntentGatewayV2.sol`, unlike the standard EVM version which uses OpenZeppelin's `SafeERC20.safeTransfer`.

### Title
Unchecked ERC20 return value in Tron `IntentGatewayV2.withdraw()` and `SweepDust` allows silent transfer failure with permanent escrow loss - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` releases escrowed order funds and sweeps dust using a raw low-level `.call()` to the ERC20 `transfer` selector, checking only that the call did not revert (`success`) but never inspecting/decoding the returned boolean. Non-standard ERC20 tokens that return `false` on failure instead of reverting will cause silent failure: the contract still finalizes the order and decrements escrow accounting as if the transfer succeeded.

### Finding Description
In `withdraw()`, escrowed tokens are released to the `beneficiary` for each token in the withdrawal request: [1](#0-0) 

and transaction fees: [2](#0-1) 

as well as `SweepDust` handling in `onAccept`: [3](#0-2) 

In all three call sites, the code performs `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` and only checks the boolean `success` (i.e., that the low-level call did not revert). It never decodes/validates the returned data as required by the ERC20 standard. Tokens that implement `transfer` to return `false` on failure (rather than reverting) will make `success == true` while the actual token transfer never took place, since a non-reverting call with `false` return data still reports `success = true` at the EVM call level.

`withdraw()` unconditionally marks `_filled[body.commitment] = beneficiary` and decrements `_orders[body.commitment][token] -= amount`  before/regardless of whether the underlying transfer actually delivered funds, and emits `EscrowReleased`/`EscrowRefunded`. Once `_filled` is set, `onGetResponse` will revert on a later legitimate refund attempt (`Filled()` check), so there's no retry path to recover the un-delivered funds — the escrow accounting is silently zeroed and the beneficiary receives nothing.

By contrast, the standard EVM `IntentGatewayV2`/`IntentsBase.sol` path uses OpenZeppelin's `SafeERC20.safeTransfer`, which correctly reverts on both a low-level call failure and a `false`/malformed boolean return value: [4](#0-3) 

The Tron variant re-implements the same escrow-release logic but drops this safety check.

### Impact Explanation
Any order filled/refunded on the Tron `IntentGatewayV2` whose escrowed token (or dust) is a non-standard ERC20 that returns `false` instead of reverting on failure (e.g., due to insufficient balance edge cases, blacklisting, paused state, or other custom failure semantics) results in permanent loss of the escrowed funds for the beneficiary: the contract believes the transfer succeeded, marks the commitment filled, and decrements internal accounting, but the tokens remain stuck in the contract with no accounting path to reclaim them. This is a direct loss-of-funds vulnerability reachable by any relayer delivering a `RedeemEscrow`/`RefundEscrow`/`SweepDust` message once an order has been placed with such a token.

### Likelihood Explanation
Likelihood depends on whether tokens used as intent inputs/outputs on Tron include non-standard ERC20/TRC20 implementations that return `false` rather than revert on failure. This is a known and common pattern among TRC20/ERC20 tokens on Tron (e.g. certain wrapped/administered tokens), making this a realistic risk rather than a purely theoretical one, especially since the gateway is designed to be permissionless with respect to which tokens can be used in orders.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` branch of `onAccept()` with OpenZeppelin's `SafeERC20.safeTransfer` (already imported and used via `using SafeERC20 for IERC20;` in this same file), matching the approach used in `IntentsBase.sol`. This ensures both call-level reverts and `false`/malformed boolean returns cause the whole transaction to revert, preventing escrow from being marked filled/decremented when the transfer did not actually succeed.

### Proof of Concept
1. An order is placed with input/output token `T`, a TRC20/ERC20 whose `transfer()` returns `false` (does not revert) when, e.g., the recipient is blacklisted or some internal condition fails, while `balanceOf`/`approve`/`transferFrom` behave normally during escrow deposit.
2. The order is filled/refunded normally; a relayer delivers a `RedeemEscrow` or `RefundEscrow` message that decodes to `WithdrawalRequest{ beneficiary, tokens: [T amount], commitment }`.
3. `onAccept` → `withdraw(body, isRefund)` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`. Because `T.transfer` returns `false` without reverting, `success == true`.
4. `withdraw()` proceeds to set `_filled[commitment] = beneficiary`, decrement `_orders[commitment][token] -= amount`, and emit `EscrowReleased`, even though `beneficiary` never received the tokens `T` remain trapped in the contract, permanently unaccounted for and unrecoverable through the escrow's own token-tracked withdrawal path.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L465-477)
```text
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```
