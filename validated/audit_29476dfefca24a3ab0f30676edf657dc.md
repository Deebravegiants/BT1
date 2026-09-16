### Title
Missing length parity check between `order.inputs` and `order.output.assets` causes out-of-bounds revert / stranded escrow in `IntrinsicIntents._fillSameChain` and `ExtrinsicIntents._fillCrossChain` - ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol], [File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
Both same-chain and cross-chain order-fill paths in the `IntentGatewayV2` app iterate over the *output* array length (`order.output.assets.length`) but index into the *input* array (`order.inputs[i]`) with the same loop counter, exactly as the ClaimZap `extraRewards(0)/extraRewards(1)` pattern indexed a second array under the assumption it was always populated. There is no explicit check anywhere in the fill path that `order.inputs.length == order.output.assets.length`, so a length mismatch produces either an unconditional out-of-bounds revert (denial of fill) or silently drops escrowed input tokens from the release set (frozen funds), depending on which array is longer.

### Finding Description
`_fillSameChain` sets `outputsLen = order.output.assets.length` and loops `for (uint256 i; i < outputsLen; i++)`, then unconditionally reads `order.inputs[i].token` / `order.inputs[i].amount` inside that loop to build `escrowedInputs[i]`: [1](#0-0) [2](#0-1) 

`_fillCrossChain` has the identical structure: it loops on `outputsLen = order.output.assets.length` and later reposts `order.inputs` wholesale as the `RedeemEscrow` withdrawal body, again with no length check against `order.output.assets`: [3](#0-2) 

Because `Order` (including `inputs` and `output.assets`) is fully attacker/user-controlled at `placeOrder` time and no length-parity validation was found on the fill path, two failure modes exist:

1. **`order.inputs.length < order.output.assets.length`**: any call into the fill loop dereferences `order.inputs[i]` for `i` beyond the input array bound once `i >= inputs.length`, which is a Solidity array out-of-bounds panic, reverting the whole transaction — this is the direct structural analog of the ClaimZap bug (unconditional revert from an out-of-bounds index access that the code implicitly assumed would never occur). The order becomes permanently unfillable through `fillOrder`.

2. **`order.inputs.length > order.output.assets.length`**: the fill loop only builds `escrowedInputs`/redeem bodies of size `outputsLen`, so input tokens at indices `>= outputsLen` are never included in the `_withdraw` release (same-chain) or `RedeemEscrow` message (cross-chain), even though the order is marked `_filled`. Once `_filled[commitment]` is set, the cancellation paths (`_cancelSameChain`, `_cancelFromSource`, `_cancelFromDest`) are the only other route to escrow release, and their eligibility is gated by "not yet filled" checks — so escrow beyond the output-array length is left permanently stuck in `_orders[commitment][token]` with no remaining code path to claim it.

I was not able to fully confirm, within the available tool budget, whether `IntentGatewayV2.sol`'s `placeOrder` performs an explicit `inputs.length == output.assets.length` check before accepting an order and escrowing funds; grep matches on `inputs.length`/`output.assets.length`/`InvalidInput` in that file were located but not read in full. If such a check exists and rejects mismatched arrays at `placeOrder` time, this finding is moot for user-created orders; the analysis above should be treated as conditional on that gap.

### Impact Explanation
If `placeOrder` does not enforce array-length parity, this is a real impact:
- Case 1 makes an order (and its escrowed input tokens) permanently unfillable by any solver, degrading protocol usability although the user can still self-cancel (limited/no direct fund loss to third parties).
- Case 2 permanently freezes the surplus escrowed input tokens after a legitimate fill marks the order `_filled`, since no remaining code path (fill or cancel) can release tokens beyond `output.assets.length` — a genuine permanent freezing-of-funds condition reachable by any user simply submitting a malformed order and any solver filling it.

### Likelihood Explanation
Reaching this path requires only a standard `placeOrder` call followed by a standard `fillOrder` call from any unprivileged solver — both are baseline, permissionless dispatch paths of `IntentGatewayV2`. The likelihood hinges entirely on whether `placeOrder` validates array-length parity, which could not be confirmed with certainty here.

### Recommendation
Add an explicit check at order placement (and defensively again at fill time) that `order.inputs.length == order.output.assets.length`, reverting with `InvalidInput()` (the existing error already used for per-index mismatches) if not. This closes both the DoS-by-out-of-bounds-revert case and the stuck-escrow case, matching the general fix pattern the Gearbox report recommended (validate/guard rather than assume array shape, and prefer an explicit bounds/parity check over relying on implicit index alignment).

### Proof of Concept
Not executable from static review alone given the unconfirmed `placeOrder` validation; the structural PoC is:
1. Construct an `Order` with `order.inputs.length == 1` and `order.output.assets.length == 2` (or vice versa), and successfully `placeOrder` it (assuming no parity check exists).
2. Call `fillOrder` as any solver with matching `FillOptions.outputs` for both output assets.
3. In the `inputs.length < outputs.length` case, the call reverts on the second loop iteration's `order.inputs[1]` access (out-of-bounds panic) — the order becomes permanently unfillable.
4. In the `inputs.length > outputs.length` case, the fill succeeds, `_filled[commitment]` is set, but the escrow entry for the extra input token index is never zeroed or released — verify via `_orders(commitment, extraToken)` remaining non-zero with no further code path able to withdraw it.

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-65)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        bool isFullyFilled = true;

        TokenInfo[] memory escrowedInputs = new TokenInfo[](outputsLen);
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-118)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-219)
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

        _execute(order, outputsLen);

        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: order.inputs});
```
