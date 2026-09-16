Based on the investigation, the closest analog to the Notional H-4 pattern — "a full-exit/finalize path checks only one balance and finalizes state while trusting that other escrowed obligations were already handled" — is in `IntrinsicIntents._fillSameChain`, which uses the number of *output* legs to drive both the completion flag and the withdrawal request, while indexing into the *input* array by the same loop counter.

### Title
Same-chain `fillOrder` can finalize an order and permanently freeze un-iterated input escrow when `order.inputs.length` exceeds `order.output.assets.length` - ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
`_fillSameChain` determines `isFullyFilled` and builds the `WithdrawalRequest.tokens` array (`escrowedInputs`) by looping `outputsLen = order.output.assets.length` times and reading `order.inputs[i]` at the same index [1](#0-0) . It assumes a strict 1:1 correspondence between the input array and the output array. If an order has more escrowed input tokens than output legs, the loop never touches the trailing input entries, yet a full fill of every *output* leg still sets `isFullyFilled = true` and calls `_withdraw(body, false, true)` with `finalize = true` [2](#0-1) .

### Finding Description
`_withdraw` is the function that performs the Notional-style "full exit": when `finalize` is true it immediately marks the order as permanently settled (`_filled[body.commitment] = beneficiary`) before it even walks the token list it was given [3](#0-2) . It then only decrements/transfers the tokens present in `body.tokens` [4](#0-3) . Exactly like the Notional bug — where the vault redemption path checks only the primary debt is zero and "simply trusts" the vault handled secondary debt — this code checks only that the iterated output legs are fully satisfied and trusts that `escrowedInputs` (built off the *output* array's length) represents the *complete* set of escrowed balances for the order. Any input token whose index is `>= order.output.assets.length` is never included in `escrowedInputs`, never decremented from `_orders[commitment][token]`, and never transferred out — but the order is finalized anyway.

Once `_filled[commitment]` is non-zero, every other entry point that could reach that escrow (`fillOrder` via `if (_filled[commitment] != address(0)) revert Filled()` in `cancelOrder`, and the same guard reused by `fillOrder`) is permanently blocked [5](#0-4) . The leftover `_orders[commitment][token]` balance for the un-iterated input token becomes unreachable code forever — it is neither refundable (order shows as filled) nor claimable by a solver (no withdrawal path references that token/commitment pair again).

### Impact Explanation
This is a permanent freezing of user funds: any input token whose array index falls outside the output array's length is escrowed at `placeOrder` but can never be withdrawn once the order is marked filled through this path, matching the "unable to deliver"/permanent-freezing class explicitly accepted by the rules. Because same-chain orders are user-supplied structs, no privileged action is needed to trigger it — an ordinary user or a malicious order-builder (to grief their own funds, or a UI bug) can construct such an order.

### Likelihood Explanation
This requires only that `IntentGatewayV2.placeOrder` (and the surrounding validation in `evm/src/apps/IntentGatewayV2.sol`) does not enforce `order.inputs.length == order.output.assets.length`. I was not able to conclusively confirm from available context whether such a length-equality check exists elsewhere in `placeOrder`'s validation path before the escrow is taken — this is the key open question that determines whether the path is actually reachable. If no such check exists, the bug is trivially reachable by any user submitting an order with more inputs than outputs.

### Recommendation
Add an explicit invariant check when placing (or filling) an order that `order.inputs.length == order.output.assets.length` for same-chain orders (or otherwise decouple the finalize/isFullyFilled decision and the swept-token list from `order.output.assets.length`, instead always sweeping the full `order.inputs` array — the same defensive pattern the Notional fix used: verify *all* balances are cleared, not just the ones the local loop happened to touch, before finalizing state).

### Proof of Concept
1. User calls `placeOrder` with `order.inputs = [USDC: 1000, DAI: 500]` and `order.output.assets = [ETH: 1]` (same-chain order, `inputs.length (2) > output.assets.length (1)`).
2. Solver calls `fillOrder` providing `1 ETH`; `_fillSameChain` loops once (`outputsLen = 1`), releases the full USDC escrow (`order.inputs[0]`), sets `isFullyFilled = true` since the single output leg is satisfied.
3. `_withdraw(body, false, true)` is called with `body.tokens = [USDC]` only; it sets `_filled[commitment] = solver` and emits `OrderFilled`.
4. The 500 DAI escrowed under `_orders[commitment][DAI]` remains in the contract, but any future `cancelOrder`/`fillOrder` call for this commitment reverts with `Filled()` — the DAI is permanently stuck. [6](#0-5) [7](#0-6) [5](#0-4)

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-137)
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
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }

            if (totalRequired > amountFilled) isFullyFilled = false;
            if (protocolShare > 0) emit DustCollected(token, protocolShare);

            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
        }

        // Orders carrying output calldata must be filled completely in a single fill.
        // The attached call is only executed on a full fill, so a partial fill would
        // leave the intended side effect unexecuted while releasing proportional escrow.
        if (order.output.call.length > 0 && !isFullyFilled) revert PartialFillNotAllowed();

        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);

        if (isFullyFilled) {
            _execute(order, outputsLen);
            emit OrderFilled({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: escrowedInputs});
        } else {
            delete _filled[commitment];
            emit PartialFill({commitment: commitment, filler: msg.sender, outputs: outputFills, inputs: escrowedInputs});
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

**File:** evm/src/apps/IntentGatewayV2.sol (L505-522)
```text
    function cancelOrder(Order calldata order, CancelOptions calldata options) public payable nonReentrant {
        bytes32 commitment = keccak256(abi.encode(order));

        if (_filled[commitment] != address(0)) revert Filled();

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        // Emitted here, once, rather than from each of the three routes below. Every check those
        // routes make — Unauthorized, NotExpired, UnknownOrder — reverts, and a revert discards
        // logs, so an early emit can never announce a cancellation that did not happen. Emitting
        // before the branch also keeps `EscrowRefunded` the last log on the same-chain route, where
        // the refund is processed in this same transaction. Three emit sites cost bytecode this
        // contract does not have: it sits within ~100 bytes of the EIP-170 limit.
        emit OrderCancelled({commitment: commitment, canceller: msg.sender});
```
