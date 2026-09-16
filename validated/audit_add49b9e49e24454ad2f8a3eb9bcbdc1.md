### Title
Escrow `withdraw()` and `SweepDust` handler in the Tron IntentGatewayV2 don't check the ERC20 transfer return value - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`withdraw()` and the `SweepDust` branch of `onAccept()` in the Tron deployment of `IntentGatewayV2` release escrowed tokens using a raw low-level `.call()` to the `IERC20.transfer` selector, but only check that the call itself did not revert (`success`). They never decode and check the boolean return value that `transfer` is supposed to return. Any ERC20-like token that signals failure by returning `false` (rather than reverting) — which is common on Tron/TRC20 tokens and other non-standard ERC20s — will silently fail the transfer while the contract still decrements escrow accounting and emits success events as if the transfer had succeeded.

### Finding Description
In `withdraw()`: [1](#0-0) 

```
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}

_orders[body.commitment][token] -= amount;
...
address feeToken = IDispatcher(host()).feeToken();
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
delete _orders[body.commitment][TRANSACTION_FEES];
```

The same pattern appears in the `SweepDust` request handler: [2](#0-1) 

In both cases, `success` from a low-level `.call()` only indicates that the callee did not revert and that the call target has code — it says nothing about the ABI-encoded `bool` return value of `transfer`. A token that implements `transfer` to return `false` on insufficient balance/blacklist/paused conditions (instead of reverting) — a pattern that is common for TRC20 tokens deployed on Tron, the exact chain this contract targets — will make the `.call()` succeed while no tokens actually move. The contract nonetheless proceeds to decrement `_orders[body.commitment][token]` and, for fees, `delete _orders[body.commitment][TRANSACTION_FEES]`, and emits `EscrowReleased`/`EscrowRefunded`/`DustSwept` as if the beneficiary was paid.

This directly matches the reported bug class (Cooler `Cooler.sol` not checking ERC20 `transfer`/`transferFrom` results) — the root cause is identical: trusting a `bool` success flag without verifying the underlying ERC20 return value. Note that elsewhere in this same file and in the EVM (non-Tron) `IntentGatewayV2.sol`/`IntentsBase.sol`, the protocol correctly uses OpenZeppelin's `SafeERC20.safeTransfer`/`safeTransferFrom`, which does perform this check — the Tron variant is the outlier that regressed to manual raw calls without validating the return data.

### Impact Explanation
This is reachable by any unprivileged party: a user placing an order that (or whose destination fill) uses a non-standard ERC20 token on the Tron deployment, or any relayer delivering a `RedeemEscrow`/`RefundEscrow`/`SweepDust` message for such a token. When the underlying token silently returns `false`:
- The solver/user who is supposed to receive escrowed funds receives nothing, yet the escrow ledger (`_orders[commitment][token]`) is decremented as though they were paid, permanently freezing/losing the underlying value — the escrowed tokens remain stuck in the contract with no accounting entry left to claim them.
- Protocol fee sweeps (`SweepDust`) can similarly "succeed" without moving funds, while the dust is considered swept and lost from any future recovery path.

This is a concrete loss/freezing-of-funds scenario, matching the High severity of the original report.

### Likelihood Explanation
Likelihood is a function of whether a non-standard, non-reverting ERC20/TRC20 token is ever configured as an intent input/output or fee token on the Tron deployment. Since `IntentGatewayV2` is a generic multi-token intent-settlement gateway that accepts arbitrary caller-supplied `token` addresses in `Order.inputs`/`output.assets` (there is no token whitelist visible in this flow), and since TRC20 non-bool-returning/false-returning tokens are common on Tron, an attacker or ordinary token issuer can trivially trigger this path without any privileged access — simply by placing/filling orders denominated in such a token.

### Recommendation
Replace every raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` transfer with OpenZeppelin's `SafeERC20.safeTransfer` (as already used in the non-Tron `IntentGatewayV2.sol`/`IntentsBase.sol`), which reverts unless the call succeeds and the returned data, if present, decodes to `true`. Apply this fix to:
- `withdraw()` escrow token transfer and fee token transfer, at [3](#0-2)  and [4](#0-3) 
- the `SweepDust` handler at [5](#0-4) 

### Proof of Concept
1. Deploy a TRC20-style token whose `transfer(address,uint256)` returns `false` (instead of reverting) when the transfer cannot be completed (e.g., insufficient balance in the gateway, or the token owner pauses/blacklists the destination address) — a realistic pattern for tokens on Tron.
2. A user places an order with this token as an input, escrowing it in `IntentGatewayV2` via `placeOrder` (uses `safeTransferFrom`, so escrow deposit succeeds normally).
3. A solver fills the order on the destination chain and the settlement message triggers `onAccept()` → `withdraw()` on the Tron IntentGatewayV2, targeting the escrowed token.
4. If the token's `transfer` call returns `false` (e.g., because it was paused after escrow, or the beneficiary is blacklisted), `token.call(...)` still returns `success = true` (the low-level call did not revert), so `TransferFailed()` is never raised.
5. `_orders[body.commitment][token] -= amount` executes, `EscrowReleased`/`EscrowRefunded` is emitted, and the function returns normally — but the beneficiary's balance never increased. The escrowed tokens are now stuck in the contract with no ledger entry to reclaim them, resulting in permanent loss of the escrowed funds.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L673-676)
```text
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-722)
```text
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
```
