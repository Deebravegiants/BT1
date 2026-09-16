### Title
`cancelOrder` refund path uses unreduced input amounts against protocol-fee-reduced escrow, causing withdraw() to revert and permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` escrows `reducedInputs[i].amount` (input amount minus `protocolFeeBps`) per token, but `cancelOrder` builds every `WithdrawalRequest` using the original, unreduced `order.inputs`. `withdraw()` then subtracts the unreduced amount from the escrow ledger that only ever held the reduced amount, causing an arithmetic underflow revert on every cancellation/refund whenever a nonzero protocol fee applies to the order's destination. This mirrors the reported class of bug: code assumes a value computed/transferred by one path (escrowed amount) always equals a related but independently-derived value used in a later payout path (withdrawal amount), and a fee/haircut mechanism silently breaks that assumption, reverting the payout 100% of the time under a specific, protocol-controlled condition.

### Finding Description
In `placeOrder`, when `protocolFeeBps > 0` (from `_destinationProtocolFees[destinationHash]` or the fallback `_params.protocolFeeBps`), each input's escrowed amount is deliberately reduced by the fee before being recorded: [1](#0-0) 

That reduced amount — not the original — is what gets added to the escrow ledger, both in the predispatch branch and the plain-transfer branch: [2](#0-1) [3](#0-2) 

However, `cancelOrder` constructs the `WithdrawalRequest.tokens` array from `order.inputs` — the original, unreduced amounts — in all three cancellation branches (same-chain, cross-chain source-side proof context, and destination-side refund dispatch): [4](#0-3) [5](#0-4) [6](#0-5) 

`withdraw()` then uses that unreduced `amount` both to push tokens to the beneficiary and to decrement the escrow ledger: [7](#0-6) 

Since `_orders[commitment][token]` only ever held the fee-reduced amount, `_orders[body.commitment][token] -= amount` (line 710) subtracts a larger `amount` than the stored balance. Solidity ^0.8.24's default checked arithmetic makes this revert with an underflow panic every single time, before the transfer's success/failure is even relevant.

### Impact Explanation
Whenever an order's destination has a nonzero protocol fee configured (a normal, expected, admin-controlled setting reachable via `setParams`/destination fee updates — not an attacker-only or malicious-admin scenario, since a positive fee is the intended default operating mode), `cancelOrder` can never successfully refund the user: same-chain cancellation reverts immediately in `withdraw()`, and cross-chain cancellation reverts identically once the `RefundEscrow`/GET-response callback reaches `withdraw()`. Because `cancelOrder`/refund is the only path back to the user for an order that is never filled, this results in permanent freezing of escrowed input tokens for every fee-bearing order that goes unfilled, matching the "permanent freezing of funds" acceptance criterion.

### Likelihood Explanation
This is not an edge case dependent on a third-party protocol's insolvency (as in the original DSU report); it triggers deterministically any time `protocolFeeBps > 0` for the relevant destination and an order is cancelled/refunded instead of filled — a routine occurrence (orders expire or the user changes their mind) rather than a rare tail event. Given protocol fees are a first-class configurable feature of this gateway, the likelihood is high.

### Recommendation
Store and reuse the reduced amounts consistently across the whole lifecycle: build every `WithdrawalRequest.tokens` array (in `cancelOrder`'s same-chain, source-side proof, and destination-side refund paths) from the fee-reduced amounts (`reducedInputs`) that were actually escrowed, not from `order.inputs`. Since `reducedInputs` is not persisted, either (a) recompute the reduction deterministically from `_destinationProtocolFees`/`_params.protocolFeeBps` at cancel time using the same formula as `placeOrder`, or (b) persist the reduced `TokenInfo[]` alongside the order commitment so cancellation can reference the exact escrowed figures without recomputation risk.

### Proof of Concept
1. Admin sets a nonzero `protocolFeeBps` (either via `_params.protocolFeeBps` or a destination-specific fee in `_destinationProtocolFees`).
2. User calls `placeOrder` with input token `T`, amount `A`. `placeOrder` computes `protocolFee = A * protocolFeeBps / 10_000`, `reducedAmount = A - protocolFee`, and stores `_orders[commitment][T] = reducedAmount` (plain-transfer path, lines 462–463), while `IERC20(T).safeTransferFrom(msg.sender, address(this), A)` pulls the full `A` into the contract (line 459).
3. Order is never filled; user calls `cancelOrder` before/after expiry as appropriate. `cancelOrder` builds `WithdrawalRequest({commitment, tokens: order.inputs, beneficiary: order.user})` where `order.inputs[i].amount == A` (unreduced), for same-chain (line 536-537), or the cross-chain proof/refund context (lines 559-560, 597-599).
4. `withdraw()` is invoked (directly for same-chain, or via `onAccept`/`onGetResponse` for cross-chain) with `amount = A`. It transfers `A` tokens to the beneficiary (line 706), then executes `_orders[commitment][T] -= A` (line 710), where `_orders[commitment][T] == reducedAmount < A`. This underflows and reverts under Solidity 0.8 checked arithmetic, reverting the entire cancel/refund transaction and leaving the user's escrowed tokens permanently stuck.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L359-374)
```text
        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L440-441)
```text
                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L462-463)
```text
                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L536-537)
```text
            WithdrawalRequest memory body =
                WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user});
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L559-560)
```text
            bytes memory context =
                abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L597-599)
```text
            bytes memory body = bytes.concat(
                bytes1(uint8(RequestKind.RefundEscrow)),
                abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}))
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
