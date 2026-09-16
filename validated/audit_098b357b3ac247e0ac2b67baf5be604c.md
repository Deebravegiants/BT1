## Title
Unsafe raw `token.call` transfer checks in `IntentGatewayV2.withdraw`/`SweepDust` ignore ERC20 return values, enabling silent transfer failures - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron deployment of `IntentGatewayV2` pays out escrowed order funds, transaction fees, and dust sweeps using a raw low-level `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only checks the boolean `success` returned by the *call itself*, never inspecting or decoding the ERC20 return data. This is the same bug class as the reported `Multipool._safeTransfer`/`_safeTransferFrom` issue — a hand-rolled "safe transfer" that fails to validate that the token's `transfer` actually returned `true`.

### Finding Description
In `withdraw()` and the `SweepDust` branch of `onAccept()`, all outbound ERC20 payouts use: [1](#0-0) [2](#0-1) [3](#0-2) 

`success` from a low-level `.call` is `true` as long as the callee doesn't revert — it says nothing about the encoded return value. Unlike even the flawed report pattern (`data.length == 0 || abi.decode(data, (bool))`), this code doesn't decode the return data at all, so it accepts:
- Tokens that return `false` on failure instead of reverting (some TRC20/ERC20 variants),
- Tokens with non-standard return encoding,

as a successful transfer. Immediately after, escrow accounting is decremented unconditionally regardless of whether tokens actually moved: [4](#0-3) 

Note that inbound transfers elsewhere in this same contract correctly use OpenZeppelin's `SafeERC20.safeTransferFrom` (e.g. `evm/tron/contracts/apps/IntentGatewayV2.sol:405,459`), so the outbound payout path is inconsistent and represents the unsafe pattern specifically.

### Impact Explanation
`withdraw()` is reached from `onAccept()` when a `RedeemEscrow`/`RefundEscrow` message is delivered via a relayed ISMP proof — an unprivileged, attacker/relayer-reachable path (any relayer can submit the proof once the request commitment exists on the source/hub chain). If the escrowed token silently fails to transfer (returns `false`, doesn't revert), the function still marks `_filled[body.commitment] = beneficiary`, decrements `_orders[commitment][token]`, and emits `EscrowReleased`/`EscrowRefunded`, permanently closing the order's accounting while the beneficiary never receives funds — resulting in permanent loss of escrowed user funds. The same applies to `TRANSACTION_FEES` payout and to `SweepDust`, which is also reachable only from hyperbridge but touches shared contract funds.

### Likelihood Explanation
Likelihood depends on the ERC20/TRC20 tokens configured for use with this Tron gateway; several tokens (including some TRC20 tokens deployed on Tron) are known to return `false` rather than revert on failure, and any protocol/relayer-supplied token address that behaves this way will trigger silent fund loss with no attacker action beyond normal, permissionless order lifecycle delivery.

### Recommendation
Replace the raw `token.call(...)` + `success`-only check in `withdraw()` (escrow token payout and fee payout) and in the `SweepDust` branch of `onAccept()` with OpenZeppelin's `SafeERC20.safeTransfer`, consistent with the `safeTransferFrom` already used elsewhere in the same contract for inbound transfers.

### Proof of Concept
1. A non-standard token that returns `false` (without reverting) on a failed `transfer` (e.g., insufficient balance edge cases, blacklist checks, or a deliberately malicious token registered as an order's `TokenInfo.token`) is used as an order's escrowed asset.
2. Hyperbridge relays a `RedeemEscrow` message; `onAccept` calls `withdraw(body, false)`.
3. `token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount))` returns `(true, abi.encode(false))` — `success` is `true` since the call didn't revert.
4. `if (!success) revert TransferFailed();` passes; `_orders[body.commitment][token] -= amount;` executes and `EscrowReleased` is emitted, even though the beneficiary received zero tokens — funds are permanently stuck/unaccounted in the gateway with escrow marked as settled.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L674-676)
```text
                    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, req.beneficiary, amount));
                    if (!success) revert TransferFailed();
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L700-710)
```text
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L719-722)
```text
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
```
