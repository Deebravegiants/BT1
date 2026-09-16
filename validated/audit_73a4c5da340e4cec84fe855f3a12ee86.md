### Title
Unchecked low-level `IERC20.transfer` calls in `IntentGatewayV2.withdraw()` allow escrow to be marked filled/refunded without any actual token transfer for non-standard ERC20s - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed intent tokens using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the boolean `success` of the external call, never decoding/verifying the returned ABI-encoded `bool`. This is exactly the "use of unsafe transfer" bug class from the referenced report, applied to a token bridge/intents escrow settlement path instead of a prize distributor.

### Finding Description
`withdraw()`, which is invoked from `onAccept()` when a `RedeemEscrow`/`RefundEscrow` POST request is delivered by any relayer, releases escrowed input tokens and transaction fees to the beneficiary using: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
``` [2](#0-1) 

and again for fee payout: [3](#0-2) 

The same unchecked pattern is used for `SweepDust` in `onAccept()`: [4](#0-3) 

The contract imports `SafeERC20` and declares `using SafeERC20 for IERC20;`, and does correctly use `safeTransferFrom` when pulling tokens into escrow during `placeOrder`/`fillOrder`: [5](#0-4) [6](#0-5) 

But the outbound release path (`withdraw`, `SweepDust`) bypasses `SafeERC20.safeTransfer` and instead does a raw `.call` while checking only `success`, not the returned data. `success` from a low-level `.call` is `true` as long as the target contract exists and does not revert — it says nothing about the ABI-decoded return value. Any ERC20 (or ERC20-like/TRC20-like token on Tron) that returns `false` on failure instead of reverting will make this code treat the transfer as successful even though no tokens moved.

Compare with the mainline EVM `IntentGatewayV2.sol`, which correctly uses `IERC20(token).safeTransfer(...)` for the equivalent path — the Tron fork has regressed to the unsafe raw-call pattern.

### Impact Explanation
Because `_filled[commitment]` (or the escrow accounting `_orders[commitment][token] -= amount`) is updated unconditionally right alongside this "successful" but silently-failed transfer, the order state is finalized as filled/refunded even though the beneficiary/solver never received the tokens. This leads to:
- Permanent freezing/loss of the user's or solver's escrowed funds: the escrow accounting is decremented and the order marked filled, but the beneficiary receives nothing and has no path to re-claim (retry would revert with `UnknownOrder` since the escrow is already zeroed).
- Same issue applies to fee payouts and to `SweepDust` for arbitrary tokens routed to a beneficiary.

This satisfies "concrete theft or permanent freezing of funds" for the intents escrow/bids reachable path.

### Likelihood Explanation
This path is reached by ordinary, unprivileged protocol usage: any relayer delivering a `RedeemEscrow`/`RefundEscrow` settlement message (part of the normal cross-chain intent fill/cancel flow) triggers `withdraw()`. No special privileges are required to trigger this call — it fires whenever a solver fills an order or a user/solver cancels, for any token configured as an intent input/output/fee token. On networks like Tron, non-standard token implementations that return `false` rather than revert on failure (e.g., insufficient balance/allowance edge cases, blacklist rejections, or paused tokens) are plausible, making this reachable in production for at least some listed tokens.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` branch of `onAccept()` with `IERC20(token).safeTransfer(beneficiary, amount)` using the already-imported `SafeERC20` library (as is already done correctly for `safeTransferFrom` in the escrow-in path, and as done in the mainline EVM `IntentGatewayV2.sol`).

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron variant) with an input/fee token whose `transfer()` returns `false` on failure instead of reverting (a realistic pattern for some TRC20/ERC20 tokens, e.g. those with paused/blacklist logic that quietly return `false`).
2. User places an order, escrowing tokens via `placeOrder` (uses `safeTransferFrom`, succeeds normally).
3. Solver fills the order cross-chain; the destination dispatches a `RedeemEscrow` request back to the source chain.
4. A relayer delivers this request; `onAccept` → `withdraw()` executes `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))`. If the token's internal condition makes `transfer` return `false` (e.g., the escrow contract balance or an allowance/blacklist condition is hit) rather than reverting, `success` is still `true` from the low-level call's perspective.
5. `_orders[commitment][token] -= amount;` executes, and `_filled[commitment] = beneficiary;` is set — the order is now permanently marked as settled.
6. The beneficiary's on-chain token balance never increased; funds are stuck in the gateway contract with no accounting entry left to claim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L459-459)
```text
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L484-484)
```text
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
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
