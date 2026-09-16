### Title
Unchecked ERC20 `transfer` return value lets the escrow be finalized and decremented even when the beneficiary receives nothing - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
In the Tron variant of the IntentGateway, `withdraw()` releases escrowed order funds to a solver/user by making a raw low-level `.call` to the ERC20 `transfer` function and only checking that the call itself did not revert. It never inspects the returned boolean. For any non-compliant ERC20 that signals failure by returning `false` instead of reverting, the escrow accounting is decremented and the order is marked finalized (`_filled[commitment] = beneficiary`) as if the transfer succeeded, even though the beneficiary received zero tokens. This mirrors the reported LMPVault pattern: the contract *assumes* the transfer/settlement succeeded and finalizes state (burn shares / mark filled) without validating the actual outcome.

### Finding Description
`withdraw()` is the internal settlement routine invoked from `onAccept()` for `RedeemEscrow`/`RefundEscrow` cross-chain messages, and from `onGetResponse()` for cancel-from-source refunds: [1](#0-0) 

Key issues in the loop:
- `_filled[body.commitment] = beneficiary;` is set unconditionally at the top of the function, before any transfer is attempted, finalizing the order regardless of transfer outcome.
- For ERC20 tokens, it does `(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount)); if (!success) revert TransferFailed();` — this only checks that the low-level call did not revert. It never decodes/validates the returned `bool` from `transfer()`.
- Immediately after, `_orders[body.commitment][token] -= amount;` decrements the escrow bucket unconditionally, treating the transfer as successful.

This is invoked from `onAccept`: [2](#0-1) 

and from `onGetResponse`: [3](#0-2) 

Contrast this with the standard EVM implementation (`IntentsBase.sol`), which uses OpenZeppelin's `SafeERC20.safeTransfer`, which does check the return value and reverts on `false`: [4](#0-3) 

The Tron contract deliberately avoids `SafeERC20`/return-value checks, exposing exactly the class of bug described in the external report: state is finalized/burned on the *assumption* that funds were fully delivered, without an assertion that verifies it.

### Impact Explanation
If any input or output token registered in an order behaves like a legacy ERC20 that returns `false` on failed transfer instead of reverting (a known real-world pattern for some tokens, and trivially achievable with a malicious/non-standard token an attacker convinces a user or solver to use in an order), then:
1. The escrow ledger entry `_orders[commitment][token]` is decremented as though funds left the contract.
2. `_filled[commitment]` is set, permanently finalizing/locking the order so it cannot be retried, cancelled, or refunded.
3. The intended beneficiary (solver on `RedeemEscrow`, user on `RefundEscrow`/cancel) receives zero tokens.

This is a permanent loss of escrowed funds for the beneficiary — the exact "permanent freezing/loss of funds" class the report calls out, reached through the standard cross-chain settlement path (`onAccept`/`onGetResponse`) that every relayed order redemption or refund goes through.

### Likelihood Explanation
Likelihood is Medium: it requires a token used as an order input/output that returns `false` rather than reverting on transfer failure (e.g., due to insufficient balance drift, blacklist checks, or pausable transfer states in certain tokens). Since `IntentGatewayV2` accepts arbitrary caller-specified ERC20 addresses for `inputs`/`outputs` (no token allow-list enforced at this layer), an order can be crafted with such a token, or a legitimate token can enter such a state (e.g., a blacklisted address) at redemption time, silently bricking that order's escrow.

### Recommendation
Use `SafeERC20.safeTransfer` (as already done in the canonical `IntentsBase.sol`) instead of a raw `.call` with only a revert-on-call-failure check, so a `false` return value causes a revert rather than silent finalization of escrow state. Additionally, avoid unconditionally setting `_filled[body.commitment]` before the transfer succeeds — finalize state only after all transfers in the loop have completed successfully, consistent with checks-effects-interactions and the report's underlying recommendation to verify actual transferred amounts before finalizing accounting.

### Proof of Concept
1. Place a same-chain or cross-chain order whose input/output token is a non-standard ERC20 that returns `false` on a failed `transfer` (rather than reverting), e.g. due to the beneficiary being blacklisted or a paused state at settlement time.
2. Solver fills the order (or user cancels); a `RedeemEscrow`/`RefundEscrow` message is dispatched and delivered via Hyperbridge, invoking `onAccept` → `withdraw()`.
3. `token.call(...transfer...)` returns `(true, encodedFalse)` — the low-level call succeeds (no revert), so `success == true` and `TransferFailed()` is not triggered.
4. `_orders[commitment][token] -= amount` executes, and `_filled[commitment] = beneficiary` was already set — the order is now permanently finalized.
5. `beneficiary`'s ERC20 balance is unchanged (transfer failed at the token level), yet the protocol believes the order is fully settled; the beneficiary's escrowed funds are irrecoverably lost.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-730)
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

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
        }
```
