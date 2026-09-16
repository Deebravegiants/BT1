## Title
Unchecked ERC20 `transfer()` return value in `IntentGatewayV2.withdraw()` and `onAccept` SweepDust branch allows silent loss of escrowed funds — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` releases escrowed order funds and dust using a raw low-level `.call` to the token's `transfer` selector, checking only that the call itself did not revert (`success`), but never inspecting the ABI-decoded boolean return value. Non-standard ERC20 tokens that return `false` on failure instead of reverting will cause the contract to believe the transfer succeeded, permanently losing/mis-accounting the escrowed tokens, while the counterpart implementation in the main EVM codebase correctly uses OpenZeppelin's `SafeERC20.safeTransfer`.

### Finding Description
In `withdraw()`, which is invoked from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests, and in the `SweepDust` handling branch of `onAccept`, tokens are transferred via:
```solidity
(bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
if (!success) revert TransferFailed();
``` [1](#0-0) 

This pattern is repeated for both the per-token escrow release loop and the accumulated transaction-fee release inside `withdraw()`, and for the `SweepDust` beneficiary payout inside `onAccept`: [2](#0-1) 

`success` here only reflects whether the low-level call reverted; it does not decode/verify the boolean the ERC20 `transfer()` function is expected to return. Tokens that return `false` on failure (rather than reverting), or tokens with non-standard/missing return data handling quirks, will make this check pass even though no tokens were actually moved. Meanwhile the accounting state (`_orders[body.commitment][token] -= amount;` and `delete _orders[...][TRANSACTION_FEES]`) is unconditionally updated to reflect a successful transfer: [3](#0-2) 

By contrast, the reference implementation for this exact escrow-release logic on the main EVM chains correctly uses `SafeERC20.safeTransfer`, which reverts on a `false` return: [4](#0-3) 

This confirms the Tron contract's raw `.call`-based transfer is a regression from the safe pattern used elsewhere in the protocol, and matches the bug class from the external report (unchecked `ERC20.transfer` result).

### Impact Explanation
This is reachable through the normal, unprivileged intent-fulfillment flow: a user calls `placeOrder` on the source chain with a non-standard-compliant input token, and a filler later calls `fillOrder`/`cancelOrder` on the destination side, which dispatches a `RedeemEscrow`/`RefundEscrow` ISMP request back to this Tron `IntentGatewayV2`. Any relayer can deliver that message; `onAccept` then calls `authenticate()` (source-instance validation) and `withdraw()`. If the escrowed token silently fails to transfer (returns `false` without reverting), the escrow bookkeeping (`_orders[...][token] -= amount`) is decremented and the order can be marked filled/refunded even though the beneficiary never received the funds — permanently freezing/losing the user's or filler's assets with no way to re-claim them, since the escrow slot is already zeroed out.

### Likelihood Explanation
Exploitability depends on the intent gateway being configured to accept a token that does not strictly follow the ERC20 standard (returns `false` instead of reverting on failure, e.g., certain legacy or pausable/blacklistable tokens). Given that Hyperbridge's Token Gateway/Intent Gateway is explicitly designed to support arbitrary registered ERC20 assets across chains (as documented for asset registration), such tokens are a realistic inclusion, making this a credible risk rather than a purely theoretical one.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` pattern in `withdraw()` and the `SweepDust` branch of `onAccept` with OpenZeppelin's `SafeERC20.safeTransfer` (as already done in `evm/src/apps/intentsv2/IntentsBase.sol`), which decodes and validates the returned boolean (or absence of return data per EIP-20 ambiguity) and reverts on failure, guaranteeing escrow accounting is only updated after a real, successful transfer.

### Proof of Concept
1. Register (or have governance register) a non-standard ERC20 token (one that returns `false` on failed `transfer` instead of reverting, e.g. due to a blacklist/pause check) as a valid input asset on `IntentGatewayV2` (Tron).
2. A user calls `placeOrder` escrowing this token.
3. The filler fills the order on the destination chain; the destination gateway dispatches a `RedeemEscrow` request back to the Tron gateway.
4. Before the message is relayed, the token blacklists/pauses the beneficiary address (or otherwise causes its `transfer()` to return `false`).
5. Any relayer delivers the `RedeemEscrow` proof; `onAccept` → `withdraw()` executes `token.call(...)`, which does not revert (the token function returns normally with `false`), so `success == true`.
6. `_orders[commitment][token] -= amount` executes, marking the escrow as released, but the beneficiary's balance never increased — the tokens are permanently stuck in the contract with no accounting path left to reclaim them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L661-682)
```text
        } else if (kind == RequestKind.SweepDust) {
            SweepDust memory req = abi.decode(incoming.request.body[1:], (SweepDust));

            uint256 outputsLen = req.outputs.length;
            for (uint256 i; i < outputsLen;) {
                TokenInfo memory info = req.outputs[i];
                address token = address(uint160(uint256(info.token)));
                uint256 amount = info.amount;

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }
```
