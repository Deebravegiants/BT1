### Title
Escrow accounting updated after external token transfer in `withdraw()` — CEI violation enables reentrant double-withdrawal - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
In the Tron deployment of `IntentGatewayV2`, the internal `withdraw()` function — reachable from `onAccept()` (for `RedeemEscrow`/`RefundEscrow` messages) and from `onGetResponse()` (source-chain cancellation) — sends escrowed native tokens or ERC-20 tokens to an attacker-controlled `beneficiary` address via a low-level `.call` **before** decrementing the `_orders[commitment][token]` escrow accounting. This is the same bug class as the BNO exploit: state (staked/escrowed balance) is not settled before the external interaction that can trigger re-entrant execution, allowing the attacker to extract the same escrow multiple times.

### Finding Description
`withdraw()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` performs: [1](#0-0) 

```
_filled[body.commitment] = beneficiary;
for each token:
    if (_orders[body.commitment][token] == 0) revert UnknownOrder();
    (bool sent,) = beneficiary.call{value: amount}("");      // EXTERNAL CALL
    ...
    _orders[body.commitment][token] -= amount;                // STATE UPDATE AFTER THE CALL
```

The escrow balance for a token (`_orders[commitment][token]`) is only checked for `!= 0` before the transfer — it is not decremented until *after* the native-token `.call` returns. Compare this to the audited/fixed EVM version's `_withdraw()` in `IntentsBase.sol`, which explicitly follows checks-effects-interactions by decrementing before transferring: [2](#0-1) 

The Tron contract sets `_filled[commitment]` first (blocking a second top-level `onAccept`/`onGetResponse` delivery of the *same* message due to `onlyHost` gating and replay protections upstream), but it does **not** protect the per-token `_orders` balance itself, and the `beneficiary` is fully attacker-controlled data decoded from the cross-chain message (`WithdrawalRequest.beneficiary`, ultimately `msg.sender` of the original solver on `RedeemEscrow`, or `order.user` on `RefundEscrow`). If the beneficiary is a malicious contract, its `receive()`/fallback fires during the `.call{value: amount}("")` before the corresponding `_orders[commitment][token] -= amount` line executes for that same token entry, and before any decrements for tokens later in the loop. In a `WithdrawalRequest` whose `tokens` array lists the same token position more than once (or, more generally, any state where the loop has not yet decremented a given token's escrow when the callback fires), the reentered path can read a still-nonzero `_orders[commitment][token]` and repeat the transfer, mirroring the `emergencyWithdraw()`/`unstakeNft()` sequencing flaw in the BNO exploit where a callback loop executed a sequence of calls before the previous state mutation had committed.

### Impact Explanation
A successful reentrant call would drain escrowed native tokens beyond what was legitimately deposited for an order, i.e., theft of user/protocol funds held by the Tron `IntentGatewayV2` contract — a direct violation of the "concrete theft of funds" bar. This affects the source-chain escrow that backs every cross-chain and same-chain intent settled through this instance.

### Likelihood Explanation
The `beneficiary` address is externally influenced (decoded from message data reflecting `order.user` or the filling solver's address), so an attacker can trivially deploy a malicious contract as beneficiary. The main mitigating factor is that `onAccept`/`onGetResponse` are `onlyHost`-gated and typically invoked once per verified message, and a single `WithdrawalRequest.tokens` array in practice enumerates each token once. Full exploitability therefore depends on whether the host/handler layer permits any secondary entry into `withdraw()`'s escrow bookkeeping while the first native-token call is still in flight (e.g., via duplicate token entries in a single request, or any reentrant path into contract functions that read/write `_orders` before the loop's own decrement executes). This could not be conclusively confirmed within the available context — the surrounding `HandlerV2`/host message-delivery replay-protection code that would rule in/out same-transaction re-invocation was not found in the indexed portion of the codebase.

### Recommendation
Apply the same checks-effects-interactions ordering used in the EVM `IntentsBase._withdraw()`: decrement `_orders[body.commitment][token]` (and clear `TRANSACTION_FEES`) before performing the native-token `.call` or ERC-20 transfer in the Tron `withdraw()` function, and add an explicit reentrancy guard (`nonReentrant`) around `onAccept`/`onGetResponse`/`withdraw` as defense in depth, consistent with the reentrancy fix already documented and tested for `IntrinsicIntents`/`ExtrinsicIntents` on the standard EVM path.

### Proof of Concept
Not independently reproducible from the indexed context — a concrete PoC would require confirming (1) that a single delivered `WithdrawalRequest` can list a repeated token entry or that the host allows a nested call into `withdraw()`'s escrow state before the loop's decrement commits, and (2) instrumenting a malicious `beneficiary` contract whose `receive()` calls back into the reachable path. This mirrors the BNO PoC pattern (flash-swap callback looping `stakeNft → pledge → emergencyWithdraw → unstakeNft` to repeatedly extract value before state was fully settled), but the exact reentry vector into Tron's `IntentGatewayV2.withdraw()` should be validated against the host/handler's message-delivery code before treating this as fully proven.

### Citations

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
