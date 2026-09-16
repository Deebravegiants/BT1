### Title
Reentrancy in `IntentGatewayV2.withdraw` (Tron variant) transfers escrowed tokens/native value before decrementing escrow accounting — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of the Intent Gateway contains a `withdraw` function that pays out escrowed order tokens (including native TRX/ETH via a raw `.call{value:}`) to a beneficiary-controlled address *before* decrementing the `_orders[commitment][token]` escrow accounting, and before deleting `_orders[commitment][TRANSACTION_FEES]`. This is the same "transfer-before-state-update" anti-pattern described in the referenced H-01 report for USDA's `_withdraw`. The main EVM `IntentGatewayV2`/`IntentsBase.sol` code base was hardened against exactly this class of bug (see `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`, which documents a prior fix moving `_filled[commitment] = msg.sender` and reordering to CEI in `_fillSameChain`/`_fillCrossChain`), but the Tron contract's `withdraw` (and its escrow bookkeeping) still performs the external call ahead of the storage write.

### Finding Description
`evm/tron/contracts/apps/IntentGatewayV2.sol` `withdraw(WithdrawalRequest memory body, bool isRefund)`: [1](#0-0) 

```solidity
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

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

        _orders[body.commitment][token] -= amount;   // <-- decremented AFTER the transfer/call
        unchecked { ++i; }
    }

    uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
    if (fees > 0) {
        address feeToken = IDispatcher(host()).feeToken();
        (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
        if (!success) revert TransferFailed();
        delete _orders[body.commitment][TRANSACTION_FEES];   // <-- cleared AFTER transfer
    }
    ...
}
```

For the native-token branch, `beneficiary.call{value: amount}("")` hands full execution control to an attacker-controlled beneficiary contract before `_orders[body.commitment][token]` is decremented. This mirrors the H-01 pattern exactly: an external transfer of value happens while the internal ledger still reflects the pre-transfer state, so any reentrant call that reads/uses `_orders[commitment][token]` (or any other function keyed by the same commitment/token pair, e.g. the multi-token loop itself for a subsequent iteration referring to `address(0)` twice, or a parallel path reachable while the loop is mid-flight) can observe stale escrow state.

By contrast, the currently-shipped, audited EVM contract (`evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`) performs the decrement (`_orders[body.commitment][token] = escrowed - amount;`) *before* the transfer: [2](#0-1) 

showing the project's own established, audited pattern for this exact operation — and the regression test suite `IntrinsicIntentsReentrancyTest.sol` explicitly documents that CEI ordering was a deliberate fix for a previously-exploitable fee/escrow-theft reentrancy in the fill path: [3](#0-2) 

The Tron variant is a separately maintained copy of `IntentGatewayV2.sol` (used for the Tron chain, where behavior/opcodes differ) that does not carry this fix forward, and additionally lacks the `nonReentrant` modifier the main contract's `placeOrder` uses.

### Impact Explanation
`withdraw` is invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` message kinds and from `onGetResponse` (GET-response driven cancellation), as well as directly from `cancelOrder` for same-chain cancellation — all of which are reachable through relayed/dispatched ISMP messages or a user's own cancel transaction, i.e., an unprivileged path any relayer or intent participant can trigger. If a beneficiary address is an attacker-controlled contract, its `receive()`/fallback executes with full call context while `_orders[commitment][token]` still holds the pre-payout balance. Depending on what other entry point can be reached and keyed by the same escrow slot during that window (e.g., a second concurrent cancellation/redeem racing on the same commitment, or any function that trusts `_orders[commitment][token]` being nonzero as proof of unspent escrow), this enables double-payout / drain of escrowed input tokens and fee-token balances held by the gateway — a direct theft-of-funds impact, consistent with the High severity of the referenced report.

### Likelihood Explanation
High for a determined attacker who can control the `beneficiary` address of an order (attacker places their own order or is selected/self-fills as beneficiary) and who can arrange a second call into a function keyed off the same `commitment`/`token` pair during the reentrant window (e.g., invoking `cancelOrder`/another dispatch path for the same order while the native-token `.call` is executing). The ERC20 branch uses a raw `.call` to `transfer` rather than `safeTransfer`, so exotic ERC777/ERC1363-style tokens with transfer hooks would also grant reentrancy even without native TRX/ETH being involved.

### Recommendation
Apply the same CEI (checks-effects-interactions) fix already used in `IntentsBase.sol::_withdraw`: decrement `_orders[body.commitment][token]` (and delete `_orders[body.commitment][TRANSACTION_FEES]`) *before* performing the native `.call` / token `transfer`, and add a `nonReentrant` guard consistent with the audited EVM `IntentGatewayV2` contract. Port the CEI ordering used in `evm/src/apps/intentsv2/IntentsBase.sol` (`_orders[...] = escrowed - amount;` before `IERC20(token).safeTransfer(...)` / `_sendValue(...)`) into the Tron `withdraw` implementation, and switch the raw `.call`-based ERC20 transfer to `safeTransfer`.

### Proof of Concept
1. Attacker places (or is selected as beneficiary of) an order with `beneficiary` set to a malicious contract, escrowing native value and/or ERC20 tokens under `commitment`.
2. A `RedeemEscrow`/`RefundEscrow` message (or same-chain `cancelOrder`) triggers `withdraw(body, ...)`.
3. Inside the loop, for the native-token entry, `beneficiary.call{value: amount}("")` transfers native value to the attacker contract and executes its fallback — at this point `_orders[commitment][token]` has *not yet* been decremented.
4. From the fallback, the attacker re-enters a reachable function keyed by the same `commitment`/`token` (e.g., a second `cancelOrder`/redeem path, or, on tokens with transfer callbacks, the ERC20 branch of the same loop) while `_orders[commitment][token]` still shows the pre-payout balance, allowing a second withdrawal/transfer against the same escrow before it is zeroed.
5. Result: the attacker extracts more value than was actually escrowed for that commitment, draining the gateway's held input tokens/fees for other users' orders.

### Citations

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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-48)
```text
/**
 * @title ReentrantBeneficiary
 * @notice Malicious beneficiary contract that attempts to re-enter `fillOrder` during
 *         the ETH transfer made by `_fillSameChain` or `_fillCrossChain`.
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
```
