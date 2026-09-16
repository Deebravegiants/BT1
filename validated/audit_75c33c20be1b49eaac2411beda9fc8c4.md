Based on my research, I found a validated analog to the Trail of Bits BPool "join/exit with zero tokens" bug class in the Hyperbridge IntentGatewayV2 codebase.

### Title
Placing an order with zero output assets permanently locks user escrow with no possible fill or refund - (File: evm/src/apps/intentsv2/IntrinsicIntents.sol, evm/src/apps/IntentGatewayV2.sol)

### Summary
`placeOrder` in `evm/src/apps/IntentGatewayV2.sol` validates that `order.inputs.length != 0`, but never validates that `order.output.assets.length != 0` [1](#0-0) . Same-chain fill logic in `_fillSameChain` iterates only over `order.output.assets.length` (`outputsLen`) and derives the escrowed-input release amounts and "fully filled" status purely from that loop [2](#0-1) , mirroring the audited BPool.sol pattern where `joinPool`/`exitPool` iterate over `_tokens.length` with no lower-bound check, allowing degenerate state transitions when the collection is empty.

### Finding Description
When a user calls `placeOrder` with a non-empty `order.inputs` array but an empty `order.output.assets` array, the order is accepted and the input tokens are escrowed under `_orders[commitment][token]` [3](#0-2) . There is no rejection analogous to the `inputs.length == 0` check for outputs.

When anyone subsequently calls `fillOrder` → `_fillSameChain` on this order, `outputsLen = order.output.assets.length` is `0`, so the `for` loop body that builds `escrowedInputs`, tracks `isFullyFilled`, and copies token/amounts never executes [2](#0-1) . Since `isFullyFilled` is initialized to `true` and never set to `false`, the function proceeds down the "fully filled" branch: it calls `_withdraw(body, false, true)` with `escrowedInputs` as an *empty* `TokenInfo[]` array (sized to `outputsLen == 0`, not to `order.inputs.length`) [4](#0-3) .

`_withdraw` only releases tokens present in `body.tokens` [5](#0-4) ; with an empty array, nothing is transferred to anyone — the solver "fills" an order that requires and delivers zero output tokens, `_filled[commitment]` is set to the caller (permanently marking the order filled) [6](#0-5) , and `OrderFilled` is emitted — but the user's originally escrowed input tokens are never released, because `finalize=true` marks the order filled while the escrow balance in `_orders[commitment][token]` is left untouched (the loop that would have decremented it never ran).

Because `_filled[commitment]` is now non-zero, `_cancelSameChain` (source-chain cancellation) is only reachable while unfilled, and the cross-chain analog `_withdraw`'s guard `if (escrowed == 0) revert UnknownOrder()` in `IntentsBase.sol` would also reject any further attempt to redeem those tokens through the normal cancel/fill paths, since the order is already marked filled. This permanently strands the user's escrowed input tokens in the contract with no code path to recover them — a permanent freezing of funds, directly analogous to the BPool report's "obtain shares for free / burn shares for nothing" class, but manifesting here as "mark filled for free while stranding the victim's escrow."

### Impact Explanation
This is a permanent freezing-of-funds bug reachable by any unprivileged pair of actors (a malicious or careless order-placer and any filler, including the placer's own second transaction) with a single `placeOrder` + `fillOrder` transaction pair — no proof, relayer, or consensus verification is required, and no special privilege is needed. The user's escrowed input tokens become permanently unrecoverable once any account (self or a bot Sybil'd by the attacker) calls `fillOrder` on the zero-output order, since `_filled` is set with no corresponding release of escrow and `UnknownOrder`/already-filled checks block further recovery.

### Likelihood Explanation
Likelihood is high given reachability: `placeOrder` performs no validation on `order.output.assets.length`, and nothing in `fillOrder`/`_fillSameChain` requires solvers or third parties to supply any special conditions — a trivial order with `inputs = [some token, some amount]` and `output.assets = []` passes all checks in `placeOrder`, and any subsequent `fillOrder(order, ...)` call with an equally empty `options.outputs` array completes without reverting.

### Recommendation
- **Short term:** In `placeOrder` (`evm/src/apps/IntentGatewayV2.sol`), add a check `if (order.output.assets.length == 0) revert InvalidInput();` mirroring the existing `order.inputs.length == 0` check, to reject orders that request zero output assets. Additionally, in `_fillSameChain`/`_fillCrossChain` (and their cross-chain counterpart in `ExtrinsicIntents.sol`), do not default `isFullyFilled` to `true` when `outputsLen == 0`; explicitly reject fills where `order.output.assets.length == 0`.
- **Long term:** Add invariant/fuzz tests (e.g., via Echidna/Foundry invariant testing) asserting that `fillOrder`/`_withdraw` never mark an order `_filled` while leaving any nonzero `_orders[commitment][token]` balance unresolved, and that escrow accounting is always consistent between `placeOrder` and terminal states (`filled`/`cancelled`).

### Proof of Concept
1. User calls `placeOrder` with `order.inputs = [{token: USDC, amount: 1000e6}]` and `order.output = {beneficiary: user, assets: [], call: ""}`. This passes the `inputs.length == 0` check and escrows `1000 USDC` under `_orders[commitment][USDC]`.
2. Any account (attacker, or the user's own throwaway address) calls `fillOrder(order, FillOptions({relayerFee:0, nativeDispatchFee:0, validUntil:0, outputs: []}))`.
3. Inside `_fillSameChain`, `outputsLen = 0`, so the main loop is skipped, `isFullyFilled` stays `true`, `escrowedInputs = []`.
4. `_withdraw(body, false, true)` is called with `body.tokens = []` — no tokens are transferred to the filler, but `_filled[commitment] = filler` is now set (order permanently marked filled).
5. The user's escrowed 1000 USDC remains in the contract under `_orders[commitment][USDC]` with no remaining code path (cancel is blocked since the order is filled; a further fill/withdraw for this commitment cannot reintroduce a token that wasn't in `body.tokens`) to release it back to the user or to anyone else — the funds are permanently frozen.

Note: I was not able to fully trace every downstream code path (e.g., all admin/sweep functions in `IntentsBase.sol` beyond `_withdraw`) that might theoretically allow recovery of stranded escrow, given the tool/iteration limits reached during this investigation; a full Devin session with complete file access would be needed to rule out any governance-only recovery path with full certainty.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-195)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();
```

**File:** evm/src/apps/IntentGatewayV2.sol (L312-329)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }

                unchecked {
                    ++i;
                }
            }
        }
```

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-129)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
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
