### Title
Reentrancy in `IntentGatewayV2.withdraw()` — escrow decrement occurs after external token transfer (Check-Effects-Interactions violation) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron port of `IntentGatewayV2` retains the same check-effects-interactions ordering bug described in the `FlashGovernanceArbiter.withdrawGovernanceAsset()` report: the internal `withdraw()` function performs a low-level `token.call(transfer(...))` to an **order-specified, user-controlled** token address before decrementing the corresponding `_orders[commitment][token]` escrow balance and before deleting the accumulated transaction-fee entry.

### Finding Description
`withdraw()` is the settlement routine for both cross-chain redemption/refund (invoked from `onAccept`/`onGetResponse`) and same-chain cancellation (invoked directly and publicly from `cancelOrder()`): [1](#0-0) 

For each escrowed input token, the contract calls the token's `transfer` function via raw `.call` **before** subtracting `amount` from `_orders[body.commitment][token]`:
```
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();

_orders[body.commitment][token] -= amount;   // <-- effect happens AFTER interaction
```
The same pattern repeats for the escrowed transaction fee: [2](#0-1) 

Order input tokens (`order.inputs[i].token`) are fully attacker-chosen at `placeOrder()` time: [3](#0-2) 

`withdraw()` is directly reachable from the public, unprivileged `cancelOrder()` entrypoint for same-chain orders: [4](#0-3) 

This is precisely the ordering the maintainers themselves identified and fixed in the mainline EVM contracts — `IntentsBase._withdraw()` decrements `_orders[...]` *before* making the token transfer: [5](#0-4) 

and the dedicated regression-test suite (`IntrinsicIntentsReentrancyTest.sol`) documents that this exact class of bug was previously exploitable and had to be closed by moving state writes ahead of external calls: [6](#0-5) 

The Tron variant was not updated to match: it only moved the `_filled[commitment]` write ahead of the loop, but left the per-token `_orders[...] -= amount` decrement and the `TRANSACTION_FEES` deletion after their respective external calls, i.e. only a partial CEI fix.

### Impact Explanation
Because the escrow accounting map (`_orders[commitment][token]`) is not updated until after the external call returns, any code path that can re-enter and read/act on the stale (pre-decrement) escrow value during that external call window remains exposed to double-accounting/state-inconsistency issues, matching the same bug class (M-severity in the original report) — a check-effects-interactions violation on funds accounting triggered by an attacker-controlled ERC-20/callback token used as an order input. This is a real regression relative to the hardened mainline EVM implementation and constitutes an unsound funds-accounting invariant in a fund-custody contract reachable directly by an unprivileged caller (`cancelOrder`) and by relayer-delivered settlement messages (`onAccept`/`onGetResponse`).

### Likelihood Explanation
- `order.inputs[i].token` is attacker-controlled, so a malicious token contract with hooks/side effects in `transfer()` can execute arbitrary code during the vulnerable window.
- `withdraw()` is reachable from the permissionless `cancelOrder()` for same-chain orders, requiring no relayer or governance cooperation.
- The `_filled[commitment]` guard mitigates the most direct double-withdrawal replay for the *same* commitment, but the fee/escrow decrement ordering is still inconsistent with the documented, intentionally-hardened mainline pattern, and no equivalent regression test exists for the Tron contract (unlike `IntrinsicIntentsReentrancyTest.sol` for the EVM version), indicating this code path has not been verified against the same reentrancy class.

### Recommendation
Apply the same check-effects-interactions fix used in `IntentsBase.sol::_withdraw()` to the Tron `IntentGatewayV2.withdraw()`: decrement `_orders[body.commitment][token]` (and delete the `TRANSACTION_FEES` entry) **before** issuing the external transfer call, e.g.:
```solidity
_orders[body.commitment][token] -= amount;
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
```
and similarly for the transaction-fee redemption block. Add a Tron-specific reentrancy regression test mirroring `IntrinsicIntentsReentrancyTest.sol`.

### Proof of Concept
1. Attacker calls `placeOrder()` on the Tron `IntentGatewayV2`, using a self-deployed malicious contract as `order.inputs[0].token` (implements `IERC20.transfer` with arbitrary side effects) and `order.user = attacker`.
2. Attacker calls `cancelOrder()` for a same-chain order (`orderSource == orderDest`), passing the `_filled` check since the order is unfilled.
3. Execution reaches `withdraw()`; `_filled[commitment]` is set, then the loop calls `maliciousToken.transfer(beneficiary, amount)` — control transfers to attacker code **before** `_orders[commitment][maliciousToken] -= amount` executes.
4. During this callback, the attacker's contract can attempt to interact with any other contract state that still reflects the stale (non-decremented) `_orders[commitment][token]` value, breaking accounting invariants relied on elsewhere (e.g. cross-chain cancellation existence checks at [7](#0-6)  which gate on `_orders[commitment][token] == 0`).

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L451-469)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-539)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain) {
            // Same-chain: validate locally and refund immediately
            // only owner can cancel
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

            // Verify we're on the correct chain
            if (orderSource != currentChain) revert WrongChain();

            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});

            withdraw(body, true);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L549-557)
```text
            uint256 inputsLen = order.inputs.length;
            for (uint256 i; i < inputsLen;) {
                // check for order existence
                if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L32-49)
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
 */
```
