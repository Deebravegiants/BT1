### Title
Same-chain fill incorrectly indexes `order.inputs` by the output loop counter, releasing wrong/mismatched escrow when `inputs.length != output.assets.length` - (File: `evm/src/apps/intentsv2/IntrinsicIntents.sol`)

### Summary
`_fillSameChain` loops over `order.output.assets` using index `i` bounded by `outputsLen = order.output.assets.length`, but inside that same loop it also indexes `order.inputs[i]` — a logically separate array — to compute and release escrow. This mirrors the Renzo H-08 pattern: the outer loop's index is used to access an array whose natural indexing bound is different, producing wrong values (or an out-of-bounds revert) whenever the two arrays' lengths diverge.

### Finding Description
In `_fillSameChain`: [1](#0-0) 

the loop bound is `outputsLen = order.output.assets.length`, yet the escrow-release amount is computed from `order.inputs[i]`: [2](#0-1) 

`order.inputs` and `order.output.assets` are independent, caller-controlled arrays inside the `Order` struct placed by the user via `placeOrder`. I could not find any validation in `IntentGatewayV2.placeOrder` (or elsewhere) that enforces `order.inputs.length == order.output.assets.length`; `placeOrder` only checks `order.inputs.length == 0` and separately guards against duplicate tokens within `order.output.assets` and computes escrow per `order.inputs[i]` on its own loop bound (`inputsLen`). Because `Order` fields are hashed into `commitment` and are otherwise unconstrained relative to each other, a user can freely place an order with, e.g., 1 input token and 3 output legs (or vice versa).

When `order.output.assets.length > order.inputs.length`, `_fillSameChain`'s loop will read `order.inputs[i]` out of bounds once `i >= order.inputs.length`, reverting the whole fill transaction (denial of fill / griefing the intent). When `order.output.assets.length < order.inputs.length`, only a subset of `order.inputs` is ever escrow-released even on `isFullyFilled`, because `escrowedInputs` is sized to `outputsLen` and the loop never visits the remaining `order.inputs` entries — those remaining tokens stay escrowed in `_orders[commitment][token]` and become unrecoverable through the normal fill path once `_filled[commitment]` is set (full fill marks the order filled; a subsequent cancel is blocked since the order is no longer "not expired"/unfilled), permanently freezing the residual escrowed input tokens. This is a fund-freezing analog of the Renzo TVL indexing bug: wrong loop index used against a differently-sized array causes systematically incorrect accounting.

### Impact Explanation
This directly affects the `IntentGatewayV2` same-chain intents path reachable by any user submitting an order via `placeOrder` (no privileged role needed) and any solver calling the fill function. Depending on the input/output array length mismatch:
- Legitimate orders can become permanently unfillable (revert due to out-of-bounds array access), denying users/solvers the ability to complete the intent.
- On a full fill, escrowed input tokens beyond `outputsLen` are never released to the solver and remain stuck in the contract's `_orders` mapping after `_filled[commitment]` has already been set, permanently freezing user funds since the order can no longer be cancelled or re-filled through the normal escrow-release path.

This qualifies as concrete permanent freezing of user funds / broken accounting in the reachable intents/escrow module, matching the "Medium/High" acceptance bar.

### Likelihood Explanation
Likelihood is high: `order.inputs` and `order.output.assets` are both fully user-supplied arrays with independent lengths, requiring no special preconditions beyond calling `placeOrder` with mismatched array sizes — a routine, permissionless action for any intent creator.

### Recommendation
Enforce `order.inputs.length == order.output.assets.length` in `placeOrder` (or explicitly design and validate `_fillSameChain`'s escrow computation to be independent of `outputsLen`), or refactor `_fillSameChain` to release input escrow via a separate loop bounded by `order.inputs.length`, mirroring the correct pattern already used for the sizing loop that computed `escrowedAmount` in `_cancelSameChain` (which correctly uses `inputsLen = order.inputs.length`).

### Proof of Concept
1. User calls `placeOrder` with `order.inputs.length = 1` (e.g., one input token) and `order.output.assets.length = 2` (two output legs), and no length-equality check rejects it.
2. A solver calls the same-chain fill function providing `options.outputs` matching the 2 output legs.
3. `_fillSameChain` iterates `i` from `0` to `1` (`outputsLen = 2`); at `i = 1` it accesses `order.inputs[1]`, which is out of bounds for a length-1 array, reverting the entire fill and permanently blocking the order from ever being filled through this path — a concrete denial-of-fill.
4. Conversely, with `order.inputs.length = 2` and `order.output.assets.length = 1`, on a full fill only `order.inputs[0]` is escrow-released via `_withdraw`; `order.inputs[1]`'s escrowed balance remains in `_orders[commitment][token]` forever since `_filled[commitment]` is now set and normal cancel/fill paths are closed, permanently freezing those tokens. [3](#0-2)

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-173)
```text
    function _cancelSameChain(Order calldata order, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        uint256 inputsLen = order.inputs.length;
        TokenInfo[] memory remainingTokens = new TokenInfo[](inputsLen);
        bool hasEscrow = false;
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            uint256 escrowed = _orders[commitment][token];
            if (escrowed > 0) hasEscrow = true;
            remainingTokens[i] = TokenInfo({token: order.inputs[i].token, amount: escrowed});
            unchecked {
                ++i;
            }
        }
```
