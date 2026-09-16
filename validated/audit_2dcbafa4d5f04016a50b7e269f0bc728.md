### Title
Unsafe ERC20 transfer in Tron IntentGatewayV2 `withdraw`/`SweepDust` accepts non-reverting `false` returns, permanently freezing escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) does not use OpenZeppelin's `SafeERC20`. Instead, its `withdraw()` and the `SweepDust` branch of `onAccept()` release escrowed/dust tokens via a raw low-level `.call()` to the ERC20's `transfer` selector, checking only that the call did not revert (`success`) — never validating the ABI-encoded boolean return value.

### Finding Description
In `withdraw()`:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

and identically for fee redemption: [2](#0-1) 

and in the `SweepDust` handler: [3](#0-2) 

For any ERC20/TRC20 token that returns `false` on failed transfer instead of reverting (a well-known non-standard-but-common ERC20 behavior, and notably including USDT-style tokens which are extremely prevalent on Tron), `success` will be `true` even though no tokens were actually moved. The code proceeds to:
- Decrement `_orders[body.commitment][token] -= amount` (escrow accounting reduced as if paid out),
- Set `_filled[body.commitment] = beneficiary` (order marked settled),
- Emit `EscrowReleased`/`EscrowRefunded`/`DustSwept`.

This is invoked from `onAccept()` for the `RedeemEscrow`/`RefundEscrow` request kinds, which is the terminal settlement step reached after any user calls `placeOrder`, a solver fills the order, and Hyperbridge relays the resulting `RedeemEscrow`/`RefundEscrow` post request cross-chain: [4](#0-3)  This is directly reachable from a single relayed cross-chain intent fill/cancellation — no privileged role is required to trigger the withdrawal path once an order exists.

Contrast this with the canonical/production `IntentsBase._withdraw()` used by the non-Tron `IntentGatewayV2`, which correctly uses `SafeERC20.safeTransfer`, reverting on a `false` return: [5](#0-4)  The Tron contract diverges from this safe pattern and reintroduces the exact "unsafe ERC20 transfer" bug class flagged in the referenced report.

### Impact Explanation
Because escrow accounting (`_orders[...]`) and the `_filled` finalization flag are updated unconditionally on `success == true`, a `false`-returning token transfer permanently and silently "settles" the order without delivering funds to the beneficiary. The tokens remain stuck in the `IntentGatewayV2` contract with no state path left to reclaim them (the commitment is marked filled/refunded, and any escrow tracking has already been decremented). This is a permanent freezing/loss of user or solver funds — a concrete unauthorized-app-state outcome (finalizing a fill/refund without the underlying value transfer occurring) reachable from ordinary Hyperbridge-relayed intent settlement.

### Likelihood Explanation
This is reachable by any user who places an order using an ERC20 whose `transfer` can return `false` without reverting (common among tokens with pausability, blacklists, or non-standard implementations), combined with normal cross-chain fill/cancel flow already supported by the protocol (`RedeemEscrow`/`RefundEscrow`/`SweepDust`). No malicious admin/governance/relayer behavior is required — only a standard token whose contract returns `false` on a disallowed transfer (e.g., blacklisted beneficiary, paused token, or non-compliant implementation), making it a Medium-severity but realistically triggerable condition given the diversity of ERC20/TRC20 tokens intended to be supported by this gateway.

### Recommendation
Replace the raw `.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` + `success`-only check pattern in `withdraw()` (lines 706, 720) and the `SweepDust` handler (line 674) with OpenZeppelin's `SafeERC20.safeTransfer`, matching the pattern already used correctly in `evm/src/apps/intentsv2/IntentsBase.sol`'s `_withdraw()` and `_execute()`. This ensures a `false` return value reverts the whole transaction instead of silently finalizing the order state.

### Proof of Concept
1. Deploy/use an ERC20 (TRC20) token that returns `false` instead of reverting when `transfer` is disallowed (e.g., blacklisted recipient or paused state) — a common real-world token behavior.
2. User calls `placeOrder` escrowing this token in the Tron `IntentGatewayV2`.
3. Order is filled/cancelled cross-chain, and Hyperbridge relays a `RedeemEscrow`/`RefundEscrow` post request to `onAccept()`.
4. `withdraw()` executes `token.call(...transfer...)`; the token contract returns `false` (call itself does not revert) because the beneficiary is blacklisted/paused at that moment.
5. `success == true` is observed by the gateway; `_orders[commitment][token]` is decremented to zero and `_filled[commitment]` is set, `EscrowReleased`/`EscrowRefunded` is emitted — despite the beneficiary receiving nothing.
6. Tokens remain trapped in the gateway contract with no remaining mechanism to redeem them for that commitment, since escrow/finalization state has already been consumed.

### Citations

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L706-708)
```text
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-469)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
