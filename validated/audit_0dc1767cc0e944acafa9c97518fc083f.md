## Analog Found

### Title
Unchecked ERC20 transfer return value lets escrow accounting advance while the actual token transfer silently fails - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order/dust funds using a raw low-level `.call` to the ERC20 `transfer` function and only checks that the call did not revert (`success`), without decoding and validating the returned boolean. Non-standard ERC20 tokens that signal transfer failure (e.g., insufficient contract balance/liquidity) by returning `false` instead of reverting will make these functions treat the transfer as successful. Escrow state is permanently decremented and the order is marked filled/refunded even though the beneficiary received nothing — directly analogous to the yAxis Controller bug, where insufficient liquidity fails to raise an error and the ledger proceeds as if funds moved.

### Finding Description
In `withdraw()`, the escrow release path for beneficiaries does: [1](#0-0) 

```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
...
_orders[body.commitment][token] -= amount;
```
This only checks that the low-level call itself didn't revert — it never decodes/verifies the `bool` return value that `IERC20.transfer` is supposed to return. Standard OpenZeppelin `SafeERC20.safeTransfer` (used correctly elsewhere, e.g. `evm/src/apps/intentsv2/IntentsBase.sol` line 468) checks this return data; the Tron contract deliberately bypasses it with a manual `.call`, likely for Tron TRC20 compatibility, but this reintroduces the classic "unchecked-return-value" ERC20 pitfall.

The same unchecked pattern recurs in the dust-sweep path: [2](#0-1) 

If `token` is a non-standard ERC20 (or the contract lacks sufficient balance and the token implementation returns `false` rather than reverting — a legitimate ERC20 behavior per the standard, unlike OZ's own implementation), `success` is still `true` for the outer `.call` (the low-level call executed without reverting), so the code proceeds:
- `_orders[body.commitment][token]` is decremented as if the beneficiary was paid.
- On `finalize`, `_filled[body.commitment]` is set and `EscrowReleased`/`EscrowRefunded` is emitted.
- The beneficiary receives zero tokens.

This exactly mirrors the report's root cause: the state-machine advances ("shares burned"/"order filled") without validating that the underlying value transfer ("liquidity withdrawal") actually succeeded, so accounting and reality diverge irreversibly.

### Impact Explanation
This is a fund-freezing/fund-loss bug reachable by any user completing the intents escrow-release flow (fill, cancel/refund, or dust sweep) when the escrowed token is a non-reverting-on-failure ERC20 (a widely-encountered real-world token behavior, and one Tron/TRC20 tokens are especially prone to, which is presumably why this file diverges from `safeTransfer` in the first place). The `_orders` mapping is permanently decremented and the order is marked filled/refunded, so the beneficiary has no recourse to reclaim the escrowed value — a permanent loss of the escrowed funds for the intended recipient, matching the "concrete theft or permanent freezing of funds" bar.

### Likelihood Explanation
Medium-to-High: it requires only that the escrowed/dust token used in an order return `false` on transfer failure instead of reverting (common for tokens ported without strict EIP-20 compliance, and specifically plausible on Tron given TRC20 quirks that appear to motivate this manual `.call` pattern in the first place). No privileged role is needed — any solver, filler, or order-canceller triggers `withdraw()`/dust-sweep as part of the normal intents lifecycle.

### Recommendation
Decode and check the boolean return value on every raw `.call` to `IERC20.transfer`/`transferFrom` in `evm/tron/contracts/apps/IntentGatewayV2.sol` (both the `withdraw()` escrow-release path and the `SweepDust` path), e.g.:
```solidity
(bool success, bytes memory data) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success || (data.length > 0 && !abi.decode(data, (bool)))) revert TransferFailed();
```
Alternatively, adopt a Tron-compatible `SafeERC20`-style helper that performs this check uniformly, so escrow debits/finalization can never occur without a confirmed successful transfer.

### Proof of Concept
1. Configure an order whose input/output token is a TRC20/ERC20-like token that returns `false` on `transfer` when its own balance is insufficient (rather than reverting) — this is legal per the ERC20 spec and observed on several deployed tokens.
2. Have the contract's token balance for that asset become insufficient relative to the escrowed `_orders[commitment][token]` amount (e.g., due to a prior partial drain, rounding, or race across concurrent withdrawals of dust/escrow).
3. Call the path that invokes `withdraw()` (fill completion, `cancelOrder` same-chain path, or `RedeemEscrow`/`RefundEscrow` `onAccept`) or `SweepDust` via `onAccept`.
4. The token's `transfer` call returns `false` without reverting; `success` from the low-level `.call` is still `true` because the call itself did not revert.
5. The function proceeds: `_orders[commitment][token] -= amount` executes, `_filled[commitment]` is set on finalize, and `EscrowReleased`/`DustSwept` is emitted — while the beneficiary's on-chain token balance is unchanged (zero received). The escrowed funds are now unrecoverable through the contract's accounting.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-680)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-714)
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
```
