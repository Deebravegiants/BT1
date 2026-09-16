### Title
`_fillCrossChain()` unconditional zero-value output transfer reverts for Revert-on-Zero-Value-Transfer tokens - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`IntentGatewayV2.fillOrder()` routes cross-chain fills to `ExtrinsicIntents._fillCrossChain()`, which transfers each output-leg amount (`totalRequired + beneficiaryShare`) to the beneficiary via `IERC20.safeTransferFrom` without ever checking that the amount is non-zero. Unlike its same-chain counterpart (`IntrinsicIntents._fillSameChain`), which explicitly `continue`s when a leg's required/solver amount is zero, `_fillCrossChain` has no such guard, so a zero-amount output leg for a revert-on-zero-value-transfer ERC20 unconditionally reverts the fill.

### Finding Description
`placeOrder()` in `IntentGatewayV2.sol` validates that every **input** amount is non-zero (`if (order.inputs[i].amount == 0) revert InvalidInput();`), but it performs no equivalent check on `order.output.assets[i].amount`. An order can therefore be placed with a zero-amount output leg for some token. [1](#0-0) 

In `_fillCrossChain`, for each output leg:
```
uint256 totalRequired = order.output.assets[i].amount;
uint256 solverAmount = options.outputs[i].amount;
if (solverAmount < totalRequired) revert InvalidInput();
(uint256 protocolShare, uint256 beneficiaryShare) =
    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
...
} else {
    IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
    ...
}
```
If `totalRequired == 0` and the solver correspondingly supplies `solverAmount == 0` (which is legal, since the only constraint is `solverAmount >= totalRequired`), then `beneficiaryShare` is also `0`, and the code calls `safeTransferFrom(msg.sender, beneficiary, 0)`. For an ERC20 that reverts on zero-value transfers (in-scope token class per the referenced BendDAO finding), this call always reverts.

By contrast, the same-chain fill path explicitly guards against this: [2](#0-1) 
```
uint256 remaining = totalRequired - alreadyFilled;
if (remaining == 0 || solverAmount == 0) {
    if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
    continue;
}
```
`_fillCrossChain` lacks this `continue`, exposing exactly the same bug class as the referenced report's `isolateRedeem()`/`bidFine == 0` issue: a value that can legitimately be zero is transferred unconditionally, and for revert-on-zero-value-transfer tokens this permanently blocks the intended user-facing action.

### Impact Explanation
Any order whose `output.assets` array contains a zero-amount leg denominated in a revert-on-zero-value-transfer ERC20 becomes permanently unfillable via `fillOrder()` on the cross-chain path — every solver's `fillOrder()` call reverts at the `safeTransferFrom` line. The user's escrowed `inputs` on the source chain are then stuck until the order's `deadline` passes and `cancelOrder()`/`_cancelFromSource` can be invoked to unwind the escrow via the GET-request round trip. This is a freezing-of-funds condition (order permanently unfulfillable, escrow inaccessible to both the solver and the beneficiary until deadline-based cancellation), matching the "route unable to deliver messages / permanent freezing until recovery" class called out in the validation criteria.

### Likelihood Explanation
Reachable by any unprivileged user placing an order (order creation has no check preventing a zero-amount output leg) and any solver attempting `fillOrder()`. No special privileges are required; the flaw is triggered purely by ordinary use of the intents system when one of the output tokens is a revert-on-zero-value-transfer ERC20 and the order happens (accidentally or intentionally, e.g. via a buggy or malicious order-encoding integration) to specify a zero amount for that leg.

### Recommendation
Add the same zero-amount skip/guard used in `_fillSameChain` to `_fillCrossChain`, e.g.:
```solidity
if (totalRequired == 0 && beneficiaryShare == 0) {
    // nothing to transfer for this leg
} else {
    IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
    ...
}
```
or reject zero-amount output legs at `placeOrder()` time, mirroring the existing `InvalidInput()` check already applied to `order.inputs`.

### Proof of Concept
1. User calls `placeOrder()` with `order.output.assets = [{token: REVERT_ON_ZERO_TOKEN, amount: 0}, {token: USDC, amount: 100e6}]` (cross-chain order: `order.source != order.destination`), escrowing the corresponding `order.inputs` on the source chain.
2. A solver calls `fillOrder()` on the destination chain, supplying `options.outputs = [{token: REVERT_ON_ZERO_TOKEN, amount: 0}, {token: USDC, amount: 100e6}]` (the only valid solver amount for the zero-required leg is `0`, since `solverAmount < totalRequired` reverts).
3. Execution reaches `IERC20(REVERT_ON_ZERO_TOKEN).safeTransferFrom(msg.sender, beneficiary, 0)` in `_fillCrossChain`, which reverts because the token disallows zero-value transfers.
4. `fillOrder()` reverts for every solver attempt; the order can never be filled, and the escrowed input on the source chain remains locked until `order.deadline` passes and `cancelOrder()` is used to reclaim it.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-199)
```text
    function _fillCrossChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L73-78)
```text
            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
```
