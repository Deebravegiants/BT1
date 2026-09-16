## Title
Zero-amount token transfer can permanently freeze Tron IntentGateway escrow withdrawals - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron `IntentGatewayV2.withdraw()` function performs a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` for every token entry in a `WithdrawalRequest`, without ever checking that the transfer amount is greater than zero. This mirrors the Axis Finance H-2 pattern exactly: if any token in the withdrawal/refund list is a "revert on zero transfer" ERC20, and its amount resolves to `0`, the entire withdraw loop reverts and the whole `onAccept`/`onGetResponse` call permanently fails, freezing every other escrowed token in the same commitment as well.

### Finding Description
`IntentGatewayV2.withdraw()` (Tron variant) iterates over `body.tokens` and unconditionally transfers each entry: [1](#0-0) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    ...
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
        ...
    }
```

Unlike this legacy path, the current EVM `IntentsBase._withdraw()` explicitly guards against this exact defect with `if (amount == 0) continue;` before calling `safeTransfer`: [2](#0-1) 

The presence of this explicit skip in the newer implementation, and its absence in the Tron contract, indicates the Tron code was not backported the same fix that the H-2-style bug requires. `withdraw()` is reached via `onAccept` for `RedeemEscrow`/`RefundEscrow` requests (cross-chain fill settlement and destination-driven cancellation refunds) and via `onGetResponse` for source-side cancellation refunds: [3](#0-2) [4](#0-3) 

Both are triggered by relayer-delivered cross-chain messages that ultimately settle a user's own escrowed order — a normal, unprivileged flow (a user places an order, a solver fills it or the user cancels it, a relayer delivers the settlement message). If any escrowed token amount for a given commitment legitimately becomes `0` at withdrawal time (e.g., a token whose full input amount was already reduced to zero through protocol-fee deduction/dust accounting, or an input entry present with amount `0` in the withdrawal request body), and that token is a "revert-on-zero-transfer" ERC20 (a class the protocol does not exclude — same class covered by the original H-2 report), the `token.call(...)` will return `success = false`, causing `revert TransferFailed()`. Because this happens inside the same loop that also finalizes `_filled[body.commitment]` and transfers all other legitimate tokens for the order, the entire settlement transaction reverts, and it will keep reverting on every retry since the underlying condition (amount == 0 for that token) is deterministic and immutable.

### Impact Explanation
This is a fund-freezing bug: a user's escrowed input tokens (potentially significant value, since one order can escrow multiple token types) become permanently unrecoverable, because the `onAccept`/`onGetResponse` message will never succeed for that commitment — matching the "Medium" severity classification the original Axis Finance H-2 report received (permanent freezing of a party's own funds due to a single problematic token in the settlement path). It affects both order fills (`RedeemEscrow` to the solver) and cancellations (`RefundEscrow`/GET-response refund to the user), so either the solver or the original user could have their entire order's escrow locked forever by an incidental zero-amount transfer for one revert-on-zero token in a multi-token order.

### Likelihood Explanation
The precondition of "amount == 0 for one entry in a multi-token order body" is plausible in normal accounting given fee deductions and dust routines elsewhere in the codebase, and revert-on-zero-transfer ERC20s are an established class of tokens the underlying report already established as in-scope/realistic for the protocol's token support model. No admin or governance privilege is required — this occurs during a standard relayer-delivered settlement of a user-initiated order/cancellation.

### Recommendation
Add the same zero-amount guard used in the current EVM `IntentsBase._withdraw()` to the Tron `IntentGatewayV2.withdraw()` function:
```solidity
if (amount == 0) continue;
```
before performing the token transfer, ensuring escrow amount checks and other bookkeeping for the token entry aren't skipped incorrectly, and preserving parity with the already-patched non-Tron implementation.

### Proof of Concept
1. A cross-chain order escrows two input tokens, `A` (a standard ERC20) and `B` (a revert-on-zero-transfer ERC20), on the Tron-deployed `IntentGatewayV2`.
2. Through order lifecycle accounting (partial-fill dust routing, protocol-fee reduction, or a withdrawal request body constructed with `tokens[i].amount = 0` for token `B`), the `WithdrawalRequest.tokens` array delivered in the `RedeemEscrow`/`RefundEscrow` message contains an entry for token `B` with `amount == 0`.
3. `onAccept` (or `onGetResponse`) calls `withdraw(body, ...)`.
4. The loop reaches token `B`, calls `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, 0))`.
5. Because `B` reverts on zero-amount transfers, `success == false`, and the function reverts with `TransferFailed()`.
6. The whole settlement transaction reverts — token `A`'s legitimate transfer is rolled back too, `_filled[commitment]` is never set, and every retry of this delivery hits the identical revert, permanently freezing the entire order's escrow. [5](#0-4)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-729)
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

        if (isRefund) {
            emit EscrowRefunded({commitment: body.commitment});
        } else {
            emit EscrowReleased({commitment: body.commitment});
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L455-469)
```text
        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
