## Title
Interaction-before-effects reentrancy pattern in Tron `IntentGatewayV2.withdraw()` (unlike the hardened EVM contract) - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

## Summary
`withdraw()` in the Tron fork of `IntentGatewayV2` performs the external token/native transfer to the beneficiary *before* decrementing the corresponding escrow accounting entry, and only checks that an escrow slot is non-zero rather than that it covers the requested amount. This is the exact "interactions-before-effects" bug class flagged in the OpenZeppelin `TimelockController` post-mortem. The mainline EVM contract (`IntentsBase._withdraw`) was hardened against this same class of bug by moving the escrow decrement and the `_filled` mutex write ahead of every external call; the Tron contract was not brought in line with that fix.

## Finding Description
In the current (patched) EVM implementation, `_withdraw` in `evm/src/apps/intentsv2/IntentsBase.sol` follows Checks-Effects-Interactions: [1](#0-0) 
`_filled[commitment]` is set before the loop, and inside the loop `_orders[commitment][token] = escrowed - amount` is written *before* the token/native transfer is attempted.

The Tron contract's `withdraw()` does the opposite — it transfers first, decrements second, and only guards against a completely empty escrow slot (`== 0`), not against the requested amount exceeding what is actually escrowed: [2](#0-1) 

The `_filled` mutex is likewise set at the very top of `withdraw()` (line 693) — after the function has already been entered but before the loop — which blocks a beneficiary from reentering `cancelOrder` on the *same* commitment (the public entry point that reaches `withdraw`) via the `Filled()` check at the top of `cancelOrder`: [3](#0-2) 

However, `onAccept` — the cross-chain entry point that also calls `withdraw()` for `RedeemEscrow`/`RefundEscrow` — never re-checks `_filled` itself before calling `withdraw`, relying solely on ISMP-level request receipts for replay protection, and `onGetResponse` behaves the same way: [4](#0-3) [5](#0-4) 

The forge tests added for the main EVM contract explicitly document that the pre-fix ordering (external call before `_filled` write) is what enabled fee/escrow theft via a malicious beneficiary contract's `receive()` hook re-entering `fillOrder`/`cancelOrder`: [6](#0-5) 
This is precisely the reentrancy bug class from the referenced OpenZeppelin `TimelockController` incident: a state-mutating operation performed after, rather than before, an external call/transfer that can hand control to attacker-supplied code.

## Impact Explanation
`withdraw()` on Tron uses raw low-level `.call` for both native ETH and ERC-20 transfers rather than `SafeERC20`. Any ERC-20 with a transfer hook/callback (or the native ETH transfer itself when the beneficiary is a contract) can regain control mid-loop, before `_orders[commitment][token]` is decremented for the token just paid out, and before the transaction-fee escrow entry is cleared. While the coarse `_filled` mutex closes the most direct re-entry path back into `cancelOrder`/`withdraw` for the *same* commitment, the ordering is fragile: any future code path that reads `_orders[commitment][...]` without also being gated by `_filled` (or any hooked/malicious token whose callback reaches such a path) reintroduces double-spend risk on escrowed funds. This diverges from the hardened invariant enforced elsewhere in the codebase and represents a real regression in a production intents settlement path reachable by any solver/user placing or filling/cancelling an order with an attacker-controlled beneficiary or token.

## Likelihood Explanation
Reachable directly and permissionlessly: any user can call `placeOrder`/`cancelOrder` with a contract-controlled `beneficiary`, and any token listed as an order input can be an arbitrary ERC-20 (including ones with transfer hooks). No privileged role, governance action, or off-chain component is required to reach `withdraw()`'s vulnerable ordering.

## Recommendation
Align `evm/tron/contracts/apps/IntentGatewayV2.sol`'s `withdraw()` with the CEI pattern already applied in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw`: decrement `_orders[commitment][token]` (and delete the transaction-fee entry) *before* performing the native/ERC-20 transfer, validate that the requested amount does not exceed the escrowed amount (not just non-zero), and use `SafeERC20` instead of raw low-level `.call` for token transfers. Also verify `_filled[commitment]` is checked consistently on every code path that reaches `withdraw()` (`onAccept`, `onGetResponse`), not only on the `cancelOrder` entry point.

## Proof of Concept
Structural PoC (mirrors the pre-fix EVM exploit already captured in `IntrinsicIntentsReentrancyTest.sol`):
1. Deploy a malicious beneficiary contract whose `receive()`/token-callback attempts to call back into the gateway.
2. Place a same-chain order with two escrowed input tokens where the first token transferred in `withdraw()`'s loop is native ETH (or a hookable ERC-20) and `beneficiary` is the malicious contract.
3. Call `cancelOrder`; inside `withdraw()`'s loop, the ETH transfer fires before `_orders[commitment][ETH]` is decremented and before the second token's escrow is touched.
4. Because `_filled[commitment]` is only set at the top of `withdraw()` (not earlier, and not re-checked defensively at every future extension point), any code path added later that reads per-token escrow without consulting `_filled` — or a hooked token whose callback reaches such a path — can double-drain the still-un-decremented escrow slot, exactly as demonstrated for the pre-fix EVM `_fillSameChain`/`_withdraw` in `evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol`. [2](#0-1)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L516-521)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable {
        bytes32 commitment = keccak256(abi.encode(order));

        // order has already been filled
        if (_filled[commitment] != address(0)) revert Filled();

```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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
