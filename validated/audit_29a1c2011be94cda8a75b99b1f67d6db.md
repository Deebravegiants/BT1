### Title
Unchecked ERC20 `transfer` return value in `IntentGatewayV2.withdraw()` and `SweepDust` handler permanently freezes escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` settles escrow withdrawals and dust sweeps using a raw low-level `call` to the token's `transfer` selector, but only checks that the call did not revert — it never decodes/validates the ABI-encoded boolean return value. Tokens (most notably USDT/TRC20-style tokens, which are exactly the class called out by the referenced report) that return `false` on a failed transfer instead of reverting will cause the gateway to treat a failed transfer as successful, permanently zeroing the escrow accounting for funds that were never actually delivered.

### Finding Description
In `withdraw()`, escrowed tokens are released with: [1](#0-0) 

and the transaction-fee payout uses the identical pattern: [2](#0-1) 

The `SweepDust` handler in `onAccept` has the same pattern: [3](#0-2) 

In all three sites, `success` from `token.call(...)` only reflects whether the external call *executed without reverting* — it says nothing about the ABI-decoded `bool` that a standards-compliant `transfer()` is supposed to return. Per EIP-20 and the well-documented behavior of several deployed tokens (canonically USDT, as called out in the referenced finding), a token can execute the transfer logic, decide the transfer cannot be completed, and simply `return false` without reverting. The low-level `call` in that scenario still returns `success == true` (with `returndata` decoding to `false`), so `withdraw()` proceeds exactly as though the transfer succeeded.

Right after the loop body executes for each token, the code unconditionally decrements escrow accounting: [4](#0-3) 

and `_filled[body.commitment]` is set at the top of the function before any transfer is attempted: [5](#0-4) 

Because `_orders[body.commitment][token]` is driven to zero regardless of whether the beneficiary actually received tokens, any retry of the withdrawal for that commitment will revert with `UnknownOrder`: [6](#0-5) 

This is reachable from the normal, unprivileged intent-fulfillment flow: a solver fills an order, the destination gateway dispatches a `RedeemEscrow`/`RefundEscrow` request back to the source chain, and `onAccept` on the Tron `IntentGatewayV2` (restricted only to `onlyHost`, i.e. any relayer that delivers a valid cross-chain proof) executes `withdraw()` against the escrowed token — no special privilege beyond normal relaying is required to trigger the vulnerable code path.

Note the EVM mainline `evm/src/apps/IntentGatewayV2.sol` consistently uses `SafeERC20.safeTransferFrom` for pulling tokens in, e.g.: [7](#0-6) 

but the Tron variant reintroduces the raw, unchecked `transfer` pattern for the *outbound* settlement path (`withdraw` and `SweepDust`), which is exactly the class of bug the report warns about.

### Impact Explanation
If the escrowed token silently returns `false` on `transfer` (a documented behavior class for popular stablecoins, and one that is especially relevant on Tron given the prevalence of TRC20 USDT-style tokens with non-standard semantics), the gateway:
1. Marks the order as filled/refunded (`_filled[commitment] = beneficiary`).
2. Zeroes out the escrow ledger entry for that token (`_orders[commitment][token] -= amount`).
3. Emits `EscrowReleased`/`EscrowRefunded` as if settlement succeeded.

The beneficiary never receives the tokens, and because the escrow entry is now zero, any future attempt to redeem reverts with `UnknownOrder`. This is a permanent loss of the solver's or user's escrowed funds with no recovery path — meeting the "permanent freezing of funds" bar.

### Likelihood Explanation
This does not require a malicious actor — only a token whose `transfer()` implementation returns `false` on failure rather than reverting (a well-known real-world behavior, especially for tokens ported to Tron/TRC20 semantics). Any transient condition that causes such a token to decline a transfer (e.g., an edge-case balance/allowance state, a paused/blacklist check in a non-standard token) silently and permanently destroys the corresponding escrow accounting. Given the report's own emphasis on USDT-class tokens, and that this is the Tron deployment of the gateway where TRC20 tokens are the norm, likelihood is realistic under normal operation, not just adversarial conditions.

### Recommendation
Use `SafeERC20.safeTransfer` (already imported and used elsewhere via `using SafeERC20 for IERC20;`) instead of raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` in `withdraw()` (both the token loop and the fee payout) and in the `SweepDust` handler in `onAccept`. `safeTransfer` correctly decodes and validates the returned boolean (when present) and reverts on failure, ensuring escrow state is only mutated when the transfer actually succeeds.

### Proof of Concept
1. Register/escrow an order in `IntentGatewayV2` on Tron for a token `T` whose `transfer()` implementation returns `false` (instead of reverting) under some failure condition (e.g., a non-standard TRC20 token, or any token that can be put into a state where `transfer` declines but does not revert).
2. Have `T` enter that failure state after escrow but before withdrawal (e.g., paused/blacklist toggle, or any implementation quirk causing `transfer` to return `false`).
3. Relay a valid `RedeemEscrow`/`RefundEscrow` request so `onAccept` → `withdraw()` executes for that commitment.
4. Observe: `token.call(...)` returns `success == true` (low-level call did not revert) even though the encoded return data is `false`; the code does not decode/check it, so it proceeds to decrement `_orders[commitment][token]` to zero and emits `EscrowReleased`.
5. The beneficiary's balance of `T` is unchanged (transfer silently failed), while the escrow record shows the funds as already withdrawn — any second attempt reverts with `UnknownOrder`, permanently freezing the beneficiary's funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-693)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L700-700)
```text
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L705-710)
```text
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-722)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/IntentGatewayV2.sol (L250-250)
```text
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
```
