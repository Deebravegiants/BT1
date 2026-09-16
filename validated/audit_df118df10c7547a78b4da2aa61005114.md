### Title
Unchecked ERC20 `transfer` return value lets a malicious order-input token steal a solver's real payment - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` uses `SafeERC20.safeTransferFrom` for all inbound token collection (`placeOrder`, fee collection), but its escrow-release path (`withdraw`) and the `SweepDust` handler pay tokens out with a raw low-level `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the call did not revert — they never decode/validate the ABI-encoded boolean return value. This is the exact "unchecked ERC20 return value" bug class from the referenced Cooler report, applied to an outbound payment instead of an inbound one.

### Finding Description
`withdraw()` releases escrowed input tokens to the beneficiary (the filling solver, in the `RedeemEscrow` flow) using: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;
```

`success` here only reflects whether the external call reverted — it says nothing about the boolean value the ERC20 contract itself returned. Non-compliant/legacy ERC20s (and any custom token deliberately crafted this way) return `false` instead of reverting on a failed transfer. For such a token, `token.call(...)` returns `success = true` even though no tokens moved, so the check passes, `_orders[...]` is decremented, and the order is marked filled/redeemed as if payment succeeded.

The same unchecked pattern also releases transaction fees and appears again in the `SweepDust` handler: [2](#0-1) [3](#0-2) 

Critically, `placeOrder` accepts **arbitrary, user-supplied token addresses** as order inputs and escrows them via `safeTransferFrom` (which does correctly enforce success): [4](#0-3) 

So the initial deposit into escrow is verified, but the payout leg is not. An order creator can therefore choose a token contract whose `transfer()` returns `false` (without reverting) on the redeem path — the input token is genuinely escrowed at `placeOrder` time (so the order looks legitimate and the commitment/escrow bookkeeping is consistent), but when `withdraw()` later attempts to pay that token out to the solver, the transfer silently no-ops while the contract still marks the order filled and decrements the internal escrow balance.

### Impact Explanation
In the intents flow, the solver calls `fillOrder` on the destination chain and immediately delivers **real** output tokens (e.g. DAI/USDC) to the order's beneficiary before the cross-chain `RedeemEscrow` message later releases the escrowed input token to the solver via `withdraw()` on the source chain (per the documented Fill Flow / Settlement sequence). If the escrowed input token is one that returns `false` on failure, the solver never actually receives payment for goods already delivered, while the protocol's accounting treats the escrow as fully and successfully redeemed. This is a direct theft of solver funds (or, in the cancel/refund path, of the user's own refunded tokens, which get permanently stuck in the gateway with no future ability to reclaim since `_orders[...]` has already been zeroed out) — matching the "concrete theft" and "permanent freezing of funds" criteria.

### Likelihood Explanation
Any unprivileged user can place an order (`placeOrder`) specifying an arbitrary ERC20 token as an input, including a token they deploy themselves engineered to return `false` on `transfer` under conditions they control (or simply relying on well-known non-reverting legacy tokens). No special privileges, governance action, or race condition is required — just crafting/selecting the input token used in a normal, permissionless order placement and fill.

### Recommendation
Use `SafeERC20.safeTransfer`/`safeTransferFrom` (already imported and used elsewhere in the same file) for all outbound token movements in `withdraw()` and `SweepDust`, instead of raw `.call(...)` with only a "did-not-revert" check. `SafeERC20` decodes and validates the actual return data (or absence thereof) and reverts if the token indicates failure, closing the gap between "call succeeded" and "transfer actually succeeded."

### Proof of Concept
1. Attacker deploys a custom ERC20 `EvilToken` whose `transfer()` function always returns `false` (without reverting) when called by the `IntentGatewayV2` contract (e.g., conditioned on `msg.sender == gatewayAddress`), but behaves normally for the initial `transferFrom` during escrow.
2. Attacker calls `placeOrder` with `EvilToken` as the sole input asset and a real, valuable token (e.g. USDC) as the requested output — `safeTransferFrom` succeeds and the tokens are genuinely escrowed in the gateway.
3. An honest solver sees the order, calls `fillOrder`, and transfers real USDC to the attacker's beneficiary address.
4. The `RedeemEscrow` message is delivered and `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, solver, amount))` against `EvilToken`; the call does not revert (`success = true`) but internally returns `false` and transfers nothing.
5. `withdraw()` proceeds to decrement `_orders[commitment][token]` and mark the order filled/redeemed — the solver receives 0 `EvilToken` despite having already paid out real USDC, and the attacker keeps the USDC while never truly paying for it.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L404-406)
```text
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L670-676)
```text
                if (token == address(0)) {
                    (bool sent,) = req.beneficiary.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L702-710)
```text
            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L717-722)
```text
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
