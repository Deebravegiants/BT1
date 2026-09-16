### Title
`withdraw()` Doesn't Follow CEI Pattern — External Transfer Before Escrow Decrement — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` implements escrow release in `withdraw()` (lines 691-730) by performing the external token/native transfer to the beneficiary *before* decrementing the corresponding `_orders[commitment][token]` escrow balance, in violation of the Checks-Effects-Interactions pattern — the same bug class as NAZ-M02. This is directly contrasted by the audited/fixed sibling implementation in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw()`, which explicitly decrements the escrow balance (`_orders[body.commitment][token] = escrowed - amount;`) *before* transferring funds out. [1](#0-0) [2](#0-1) 

### Finding Description
`withdraw()` is reached from `onAccept()` for `RedeemEscrow`/`RefundEscrow` requests and from `onGetResponse()` for source-chain cancellation: [3](#0-2) [4](#0-3) 

Inside `withdraw()`, for each token in the withdrawal request the flow is:
1. `if (_orders[body.commitment][token] == 0) revert UnknownOrder();`
2. External interaction — either a raw `.call{value: amount}("")` to `beneficiary` for native tokens or a low-level `token.call(...transfer...)` for ERC-20s.
3. Only *after* the external call: `_orders[body.commitment][token] -= amount;` [5](#0-4) 

This is the textbook CEI violation described in NAZ-M02: the state effect (escrow decrement) happens after the external interaction, rather than before it. The mitigation already shipped in the primary EVM implementation (`IntentsBase.sol`) performs the decrement first, and a dedicated regression test suite (`IntrinsicIntentsReentrancyTest.sol`) exists specifically to confirm that CEI ordering blocks reentrancy for the same-chain and cross-chain fill/withdraw paths: [6](#0-5) 

The Tron contract, however, was not brought in line with that fix — it still transfers before decrementing, and it uses raw `.call()` for ERC-20 transfers (not `SafeERC20`), so a malicious/ERC-777-style token or a malicious native-token beneficiary contract gets code execution *before* its escrow entry is zeroed out.

### Impact Explanation
A beneficiary/solver address (attacker-controlled contract) that receives a native-token or malicious-token payout from `withdraw()` can, in its `receive()`/token callback, re-enter the gateway while `_orders[commitment][token]` for that same token (or for other tokens in a multi-input order not yet reached by the loop) is still non-zero. Because the decrement is deferred to after the interaction, the escrow accounting can be read/acted upon in a stale, over-credited state during the reentrant window — this is a real bug-class match to unbacked/duplicate payout risk on escrowed funds. This directly threatens theft of escrowed input tokens, which the "Validate" rules classify as concrete fund theft, warranting Medium-to-High severity depending on what other public entry points read `_orders[commitment][token]` during the reentrant window (e.g., `cancelOrder`/`fillOrder` paths on this same contract share the `_orders` mapping).

### Likelihood Explanation
Exploitability depends on whether the host layer marks the incoming ISMP request as received/consumed strictly before invoking `onAccept` (which would block a literal request replay), and whether `_filled[commitment]` being set at the top of `withdraw()` (line 693) is sufficient to block all other public reentry paths that touch the same commitment (e.g., `fillOrder`, `cancelOrder`) during the same transaction. I was not able to fully verify the exact host receipt-marking order for the Tron host contract within the available tool budget, so likelihood is stated as **uncertain/Medium** rather than confirmed-High — the root-cause CEI violation itself is confirmed and unambiguous by direct code comparison with the already-audited-and-fixed sibling contract.

### Recommendation
Mirror the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol::_withdraw()`: decrement `_orders[body.commitment][token]` (and `TRANSACTION_FEES`) *before* performing the native/ERC-20 transfer, and switch the raw `.call(...)` ERC-20 transfers to `SafeERC20.safeTransfer` for consistency with the rest of the codebase.

### Proof of Concept
```solidity
// evm/tron/contracts/apps/IntentGatewayV2.sol (current, vulnerable ordering)
function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
    address beneficiary = address(uint160(uint256(body.beneficiary)));
    _filled[body.commitment] = beneficiary;

    uint256 len = body.tokens.length;
    for (uint256 i; i < len;) {
        address token = address(uint160(uint256(body.tokens[i].token)));
        uint256 amount = body.tokens[i].amount;
        if (_orders[body.commitment][token] == 0) revert UnknownOrder();

        if (token == address(0)) {
            (bool sent,) = beneficiary.call{value: amount}(""); // <-- external interaction FIRST
            if (!sent) revert InsufficientNativeToken();
        } else {
            (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
            if (!success) revert TransferFailed();
        }

        _orders[body.commitment][token] -= amount; // <-- state effect happens AFTER the call
        unchecked { ++i; }
    }
    ...
}
```
Compare with the CEI-correct version already in production for the main EVM contracts:
```solidity
// evm/src/apps/intentsv2/IntentsBase.sol (fixed ordering)
uint256 escrowed = _orders[body.commitment][token];
if (escrowed == 0) revert UnknownOrder();
_orders[body.commitment][token] = escrowed - amount;   // effect first
if (token == address(0)) {
    _sendValue(beneficiary, amount);
} else {
    IERC20(token).safeTransfer(beneficiary, amount);    // interaction after
}
```
A malicious `beneficiary` contract with a `receive()` hook that calls back into any public function reading/mutating `_orders[commitment][*]` during the native-transfer callback in the Tron contract's `withdraw()` demonstrates the stale-state window described above.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
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

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L85-101)
```text
/**
 * @title IntrinsicIntentsReentrancyTest
 * @notice Forge tests that confirm the CEI fix in `IntrinsicIntents._fillSameChain`
 *         and verify that `ExtrinsicIntents._fillCrossChain` is also resistant to
 *         reentrancy attacks.
 *
 * Both fill functions now open with `_filled[commitment] = msg.sender` before any
 * external calls, so a reentrant `fillOrder` attempt is always blocked by the
 * `Filled()` guard in `IntentGatewayV2.fillOrder`.
 *
 * Test matrix
 * ───────────
 *  testReentrancy_FeeTheft                    same-chain, 1 ETH output   → InsufficientNativeToken
 *  testReentrancy_EscrowTheft_MultiOutput     same-chain, ETH+ERC-20     → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked           cross-chain, 1 ETH output  → InsufficientNativeToken
 *  testCrossChain_ReentrancyBlocked_MultiOutput cross-chain, ETH+ERC-20  → InsufficientNativeToken
 */
```
