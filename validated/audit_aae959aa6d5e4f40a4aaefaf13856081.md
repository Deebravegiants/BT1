### Title
Unchecked ERC20 return value in `withdraw()` and `SweepDust` handling lets a non-reverting-`false` token permanently strand escrowed/dust funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of the Intent Gateway (`evm/tron/contracts/apps/IntentGatewayV2.sol`) imports `SafeERC20` and uses `safeTransferFrom` for escrow deposits in `placeOrder`, but its `withdraw()` function and the `SweepDust` branch of `onAccept()` transfer tokens out via raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the external call did not revert — they never decode/verify the boolean return value of `transfer`.

### Finding Description
In `withdraw()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
_orders[body.commitment][token] -= amount;
``` [1](#0-0) 

and in the fee-release path:
```solidity
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];
``` [2](#0-1) 

and in `onAccept`'s `SweepDust` branch:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
if (!success) revert TransferFailed();
``` [3](#0-2) 

A Solidity low-level `.call` only reports `success = false` when the callee **reverts**. Non-standard (but real-world) ERC20 tokens that return `false` instead of reverting on a failed transfer will make this `.call` return `success = true` even though no tokens moved. Because the code never inspects the ABI-decoded boolean return value (as `SafeERC20.safeTransfer` does), the contract proceeds as if the transfer succeeded: it decrements `_orders[commitment][token]` (or deletes the fee entry) and marks the order `_filled`, permanently finalizing escrow accounting while the beneficiary never received the tokens. This is inconsistent with the rest of the same file, which correctly uses `IERC20(token).safeTransferFrom(...)` for deposits [4](#0-3) , and with the primary EVM `IntentGatewayV2.sol`/`IntentsBase.sol` withdraw path, which uses `safeTransfer` throughout [5](#0-4) .

`withdraw()` is reachable from `onAccept()` for both `RedeemEscrow` and `RefundEscrow` request kinds delivered through Hyperbridge's cross-chain messaging (a relayed, ISMP-verified message, not privileged) [6](#0-5) , and also from `onGetResponse()` on order cancellation [7](#0-6) . Any user placing an order with such a token, or a solver filling with such a token as an output/dust asset, can trigger this silent-failure path without any privileged role.

### Impact Explanation
Once `_orders[commitment][token]` is decremented (or the fee slot deleted) without the tokens actually leaving the contract, the escrow accounting no longer matches the token balance the user/solver is entitled to: the beneficiary's funds are permanently unrecoverable through the normal withdraw/refund flow, since the order is already marked filled/refunded and the escrow entry consumed (`UnknownOrder` would revert on any retry, and no re-attempt path exists). This constitutes permanent freezing/loss of user or protocol funds for tokens that return `false` on failure rather than reverting.

### Likelihood Explanation
Requires a specific token behavior (returns `false` rather than reverting on failed transfer). Such tokens exist in the wild (older/non-compliant ERC20s), and nothing in `placeOrder`/order validation restricts the input/output token set to standard-reverting tokens — arbitrary token addresses are accepted per order. Given IntentGateway is explicitly designed to be token-agnostic (accepting arbitrary `TokenInfo.token` addresses from unprivileged users/solvers), likelihood of a bridger/solver introducing such a token, deliberately or not, is realistic.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` and the `SweepDust` branch of `onAccept()` with `SafeERC20.safeTransfer`, matching the pattern already used for deposits in the same file and for withdrawals in `evm/src/apps/intentsv2/IntentsBase.sol`. This ensures both a non-reverting call and a `false` boolean return are treated as failures, preventing escrow state from being finalized when no tokens actually moved.

### Proof of Concept
1. Deploy a mock ERC20 whose `transfer` returns `false` on failure (e.g., insufficient balance) instead of reverting.
2. User calls `placeOrder` with this token as an input, escrowing tokens successfully via `safeTransferFrom` in `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `placeOrder`.
3. Trigger a scenario where the gateway's balance of that token is insufficient at the time `withdraw()` executes the payout `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` (e.g., partial fill / dust accounting drift, or an order manipulated so the transfer would fail) — the mock token returns `false`.
4. Observe: `success` is `true` (call didn't revert), so `withdraw()` proceeds to decrement `_orders[commitment][token]` and mark `_filled[commitment] = beneficiary`, while `beneficiary`'s token balance never increased — the escrow is finalized/lost with no path to reclaim it.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-676)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-711)
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
