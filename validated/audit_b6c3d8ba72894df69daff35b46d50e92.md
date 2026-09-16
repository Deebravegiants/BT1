### Title
Unchecked raw `IERC20.transfer` return value in `IntentGatewayV2.withdraw()` can silently fail and permanently strand escrowed order funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` imports `SafeERC20` and declares `using SafeERC20 for IERC20;`, and correctly uses `safeTransferFrom` when escrowing order inputs. However, the internal `withdraw()` function — which releases escrowed inputs to a solver (`RedeemEscrow`) or refunds them to the user (`RefundEscrow`), and pays out accumulated transaction fees — bypasses `SafeERC20` entirely and instead performs a raw low-level call with the `IERC20.transfer` selector, only checking that the *call itself* did not revert, never decoding/validating the ABI-encoded boolean return value.

### Finding Description
In `withdraw()`: [1](#0-0) 

```solidity
if (token == address(0)) {
    (bool sent,) = beneficiary.call{value: amount}("");
    if (!sent) revert InsufficientNativeToken();
} else {
    (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
    if (!success) revert TransferFailed();
}
_orders[body.commitment][token] -= amount;
...
(bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
if (!success) revert TransferFailed();
```

`success` only reflects whether the external call reverted, not whether the ERC20 `transfer()` returned `true`. Any token that signals failure by returning `false` instead of reverting (a legal, standard-compliant behavior for ERC20, and common for legacy/non-standard tokens, blacklist/pausable tokens, or tokens with edge-case failure modes) will cause `withdraw()` to treat the transfer as successful even though no tokens moved.

This is precisely the vulnerability class from the referenced report: use `safeTransfer` (which decodes and validates the return data) instead of raw `transfer`/`call`. The rest of the codebase already does this correctly elsewhere — e.g. `IntentsBase._withdraw()` in the standard EVM app uses `IERC20(token).safeTransfer(beneficiary, amount)`: [2](#0-1) 

confirming the Tron variant's raw-call pattern is an inconsistency/regression rather than an intentional design choice.

`withdraw()` is reachable from two unprivileged, message-driven paths:
1. `onAccept()` handling `RedeemEscrow`/`RefundEscrow` requests delivered via a relayed cross-chain ISMP POST (after `authenticate()` against the registered peer instance) — triggered whenever a solver fills a cross-chain order or a user cancels from the destination chain: [3](#0-2) 
2. `onGetResponse()` for the cancel-from-source flow, which also calls `withdraw()`: [4](#0-3) 

Both paths are reachable by any relayer delivering a proof for a normal order lifecycle event — no privileged role required.

### Impact Explanation
When the payout token silently returns `false`:
- `_orders[commitment][token]` is decremented and `_filled[commitment]` is set to the beneficiary regardless of whether tokens were actually delivered.
- `EscrowReleased`/`EscrowRefunded` is emitted, marking the order as settled.
- Because the order is now marked filled/refunded, there is no retry path — the beneficiary's tokens are permanently stuck in the gateway contract while protocol state asserts they were paid out.

This is a permanent freezing/loss of escrowed user or solver funds, directly reachable from the normal intents settlement flow, without any admin or governance involvement.

### Likelihood Explanation
Likelihood depends on the input/output token used in an order behaving in a return-false-on-failure manner (a well-known, non-hypothetical category of ERC20 implementations) combined with a transfer-failure condition (e.g., blacklisting, pausing, insufficient balance from prior dust/fee accounting drift). Given intent gateways are explicitly designed to support arbitrary user-specified ERC20 tokens as order inputs/outputs, and Tron's own USDT (TRC20) historically has had non-standard token semantics, this is a realistic condition rather than a purely theoretical one.

### Recommendation
Replace the raw `token.call(abi.encodeWithSelector(IERC20.transfer.selector, ...))` patterns in `withdraw()` (and the equivalent pattern in the `SweepDust` handling within `onAccept`) with `IERC20(token).safeTransfer(beneficiary, amount)`, consistent with the `SafeERC20` usage already present elsewhere in this same file (`safeTransferFrom`) and in the standard EVM `IntentsBase._withdraw()`.

### Proof of Concept
1. User places a cross-chain order on the source chain with `order.inputs` containing a non-standard ERC20 token `T` whose `transfer()` returns `false` (instead of reverting) when the recipient is blacklisted or the transfer otherwise cannot complete.
2. Solver fills the order on the destination chain; the cross-chain `RedeemEscrow` settlement message is dispatched back to the source chain and delivered by a relayer.
3. On the source chain, `onAccept()` authenticates the message and calls `withdraw(body, false)`: [3](#0-2) 
4. Inside `withdraw()`, if token `T`'s `transfer()` to the solver returns `false` (e.g., solver is transiently blacklisted, or `T` has a bug causing return-false on this transfer), the low-level `call` still succeeds (`success == true`), so no revert occurs: [5](#0-4) 
5. `_orders[commitment][token]` is decremented, `_filled[commitment]` is set, and `EscrowReleased` is emitted — the order is now permanently marked settled even though the solver received zero tokens, with no mechanism to retry or reclaim the escrow.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L631-635)
```text
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L464-477)
```text
            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
        }

        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```
