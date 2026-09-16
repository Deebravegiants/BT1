### Title
Unchecked low-level `.call()` for ERC20 transfers in `withdraw()`/`SweepDust` allows silent transfer failures to permanently freeze escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Halborn finding in `SprinklerUpgradeable` stems from using a raw, non-standard `token.call(...)` pattern for ERC20 transfers that only checks `success`, without validating that the token has deployed code or that the ERC20 call actually returned `true`. The Tron variant of `IntentGatewayV2` reproduces the exact same anti-pattern for token payouts in `withdraw()` and the `SweepDust` branch of `onAccept()`, even though the same file correctly uses OpenZeppelin's `SafeERC20` (which validates both code presence and boolean return) for deposits elsewhere.

### Finding Description
In `withdraw()`, escrowed ERC20 tokens are released to the beneficiary using a bare low-level call instead of `SafeERC20.safeTransfer`: [1](#0-0) 

The same pattern appears for the transaction-fee payout in the same function: [2](#0-1) 

and for the governance-triggered `SweepDust` handler: [3](#0-2) 

The check `if (!success) revert TransferFailed();` only verifies that the external call did not revert. Per the ERC20 standard, many tokens (non-standard/legacy implementations, and tokens with blacklist/pausable transfer hooks) return `false` instead of reverting when a transfer cannot be completed (e.g., recipient blacklisted, contract paused, insufficient allowance edge cases introduced by hooks). A `.call()` to such a token returns `success = true` with `returndata` decoding to `false`, which this code never inspects. Contrast this with the deposit path in the very same contract, which correctly uses `IERC20(token).safeTransferFrom(...)` via `using SafeERC20 for IERC20;` — a library that decodes the boolean return value and (via OpenZeppelin's `Address.verifyCallResultFromTarget`) also reverts if the target has no code: [4](#0-3) 

This inconsistency — safe library used for pulling funds in, raw unchecked call used for pushing funds out — is the same root-cause class the Halborn report flags: trusting a low-level `call`'s `success` flag as proof that value was actually moved.

### Impact Explanation
When `withdraw()` is invoked (via an authenticated `RedeemEscrow`/`RefundEscrow` ISMP message after a fill or cancellation), it unconditionally decrements the escrow accounting (`_orders[body.commitment][token] -= amount;`) and emits `EscrowReleased`/`EscrowRefunded` as soon as `success == true`, regardless of whether the token's `transfer` call actually returned `true`. If the underlying token silently returns `false` (e.g., the beneficiary is blacklisted by the token issuer, or the token is paused), the beneficiary never receives the funds, yet the protocol marks the escrow as resolved and there is no other code path to retry or reclaim it — the tokens remain permanently stuck in the `IntentGatewayV2` contract with no accounting reference pointing back to them. This is a permanent freezing of user/solver funds, reachable from the normal order-fill/cancel lifecycle that every intent solver and user relies on.

### Likelihood Explanation
This is reachable via the standard, unprivileged order lifecycle (`placeOrder` → fill/cancel → cross-chain `RedeemEscrow`/`RefundEscrow` message → `withdraw()`), triggered whenever an order uses a token with non-reverting failure semantics or a beneficiary address that a token issuer can restrict (blacklisting is common on major stablecoins and RWA tokens). No special privileges are required from the order placer or solver to select such a token/beneficiary pair, making this a Medium-likelihood, high-impact (fund-freezing) issue whenever such tokens are whitelisted/used by the deployment.

### Recommendation
Replace all raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` usages in `withdraw()` and the `SweepDust` handler with `IERC20(token).safeTransfer(...)` (the library is already imported and used elsewhere in this same contract via `using SafeERC20 for IERC20;`), ensuring both code-presence and boolean-return validation are enforced consistently across all token-moving code paths.

### Proof of Concept
1. Governance/asset registration allows a token `T` implementing legacy ERC20 semantics (returns `false` on failed transfer instead of reverting) to be used as an order input/output asset.
2. A user calls `placeOrder` with input token `T`, which is escrowed via the correctly-guarded `safeTransferFrom` path.
3. The order is filled/cancelled on the counterpart chain, and a `RedeemEscrow`/`RefundEscrow` message is relayed back and authenticated, invoking `withdraw()`.
4. If the recipient (`beneficiary`) is blacklisted by token `T` (or `T` is paused) at the time of withdrawal, `token.call(...)` returns `success = true` with `returndata` decoding to `false` — no tokens move.
5. `withdraw()` proceeds past `if (!success) revert TransferFailed();` (since `success == true`), decrements `_orders[body.commitment][token]`, and emits `EscrowReleased`/`EscrowRefunded`.
6. The escrowed tokens remain in the `IntentGatewayV2` contract balance with no on-chain accounting entry left to reclaim them — permanently frozen.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-460)
```text
        } else {
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-681)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
                unchecked {
                    ++i;
                }
                emit DustSwept(token, amount, req.beneficiary);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-709)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
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
