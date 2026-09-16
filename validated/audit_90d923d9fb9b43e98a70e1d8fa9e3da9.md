Confirmed: `withdraw()` is invoked from `onAccept` when an incoming ISMP POST request of kind `RedeemEscrow` or `RefundEscrow` is delivered — i.e., reachable by any relayer submitting a valid cross-chain state proof/message delivery for the counterpart order fill or cancellation. This is a legitimate, unprivileged, protocol-level trigger path.

### Title
Escrow withdrawal uses raw low-level `.call()` for ERC20 transfer without checking return data, allowing silent transfer failure and permanent fund loss - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.withdraw()` and the `SweepDust` handler in `onAccept` release escrowed order tokens to beneficiaries using a raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` and only check that the low-level call did not revert (`success`), without decoding/validating the returned boolean. This is the same unsafe-ERC20-transfer bug class flagged in the external report (TRST-M-4), applied on the receive/withdrawal leg instead of the send leg.

### Finding Description
In `withdraw()`, escrowed tokens are released to the beneficiary as follows: [1](#0-0) 

And the fee-token payout right after it: [2](#0-1) 

The same pattern appears in the `SweepDust` branch of `onAccept`: [3](#0-2) 

`token.call(...)` returns `success = true` as long as the callee doesn't revert, regardless of what boolean value is ABI-encoded in the return data. Per the ERC20 standard, a compliant `transfer` implementation must return `false` (not revert) when a transfer cannot be completed (e.g., paused token, blacklist checks, insufficient balance edge cases in certain implementations). Because the code never inspects `returndata`, such a `false` return is treated identically to a successful transfer: `_orders[body.commitment][token] -= amount;` is executed and the ISMP request is marked handled (`_filled[body.commitment] = beneficiary`), even though the beneficiary received nothing.

This is reachable by any relayer that delivers a valid `RedeemEscrow`/`RefundEscrow` POST request to `onAccept` — a fully permissionless, protocol-level path (order fill confirmation or order cancellation refund), matching the intents-escrow reachability the scan targets.

### Impact Explanation
If the escrowed token silently returns `false` on `transfer` (rather than reverting) under any condition — e.g., a paused/blacklisting token, a token with an internal cap or governance-controlled freeze, or simply a bug/edge case in the token's own `transfer` — the escrowed funds are never delivered to the beneficiary, yet the contract deletes/decrements its internal accounting (`_orders[...]`) and marks the order as filled/refunded. This results in **permanent loss of user/solver funds**: the tokens remain stuck in the `IntentGatewayV2` contract (unrecoverable via `withdraw` again, since `_filled` is already set and `_orders[...]` decremented), while the on-chain state falsely records the order as settled.

### Likelihood Explanation
Likelihood is conditional on the specific ERC20 token used for an order's input assets or the fee token returning `false` instead of reverting — this is a known, real-world pattern for several deployed tokens (pausable/blacklistable stablecoins, some legacy tokens). Given the fee token is described elsewhere in the docs as typically a stablecoin (e.g., DAI/USDC-class assets, some of which implement blacklist/pause logic that returns `false` rather than reverting in edge cases), and given intents-gateway is designed to support arbitrary configured input tokens, this is a realistic, not purely theoretical, trigger — and unlike the original report's team response (which explicitly excludes only tokens that "don't return boolean values," i.e., missing return data), this specific case (tokens that DO return a boolean, but `false`) is not addressed by that stated mitigation strategy at all.

### Recommendation
Replace the raw `.call()` + `success`-only check with OpenZeppelin's `SafeERC20.safeTransfer` (already used correctly elsewhere in this same file for `safeTransferFrom`, e.g. at lines 405/459/484 and in `evm/src/apps/IntentGatewayV2.sol` at line 250), which decodes and validates the boolean return value when present, in addition to checking for call success. This is consistent with the report's own recommended mitigation, and ensures a `false` return is treated as a failed transfer (reverting the whole withdrawal) rather than silently succeeding.

### Proof of Concept
1. Deploy `IntentGatewayV2` and configure an input token whose `transfer` function returns `false` when a per-transaction/blacklist condition is not met (many production tokens implement such logic, e.g., a pausable/blacklistable ERC20).
2. A user places an order with this token as input, funds are escrowed via `_orders[commitment][token]`.
3. A solver fills the order on the destination chain; a relayer delivers the `RedeemEscrow` POST request to the source chain's `IntentGatewayV2.onAccept`.
4. Suppose the token's `transfer` call to the beneficiary returns `false` (e.g., beneficiary momentarily blacklisted, or a token-specific restriction) instead of reverting.
5. `withdraw()` reads `success = true` from the low-level `.call()` (ignoring the `false` returndata), decrements `_orders[commitment][token]`, sets `_filled[commitment] = beneficiary`, and emits `EscrowReleased`.
6. The beneficiary never receives the tokens; the funds are permanently stuck in the `IntentGatewayV2` contract, and there is no remaining code path to retry or reclaim them since the order is already marked filled and the escrow accounting zeroed.

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
