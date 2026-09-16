### Title
Unbounded `order.output.assets`/`order.inputs` array lets an order placer grief solvers into a gas-limit revert with no cap on array length - (File: evm/src/apps/IntentGatewayV2.sol / evm/src/apps/intentsv2/IntrinsicIntents.sol)

### Summary
`IntentGatewayV2.fillOrder` and `IntrinsicIntents._fillSameChain` size their per-asset processing loop directly from the attacker-controlled `order.output.assets.length` (and the matching `order.inputs.length`), with no upper bound enforced anywhere in order placement or filling. A user placing an order can construct an arbitrarily large `output.assets`/`inputs` array — e.g. thousands of dust-value entries plus one attractive large entry — to entice a solver into calling `fillOrder`. The loop performs an external `safeTransferFrom`/native transfer per array element, so a sufficiently large array causes the fill transaction to exceed the block gas limit and revert, burning the solver's gas with no output received and the escrow untouched. This is structurally the same defect as the Juicebox `distributeReservedTokensOf`/`JBSplitsStore.set` bug: an unprivileged party can be lured into calling a permissionless function whose cost is controlled by another user's unbounded array, causing pure gas loss.

### Finding Description
`fillOrder` derives the iteration count from the order itself and only checks length *equality*, never an upper bound: [1](#0-0) 

That count then drives a per-index loop in `_fillSameChain`, where each iteration validates the asset, computes fill/surplus amounts, and executes an external token transfer (`safeTransferFrom` for ERC-20 outputs, or a raw `.call{value:}` for native): [2](#0-1) 

Nowhere in order placement (`placeOrder`, which only validates and emits the order) or in `fillOrder`/`_fillSameChain`/the cross-chain fill path is `order.output.assets.length` (or `order.inputs.length`) capped. A user can therefore submit an order whose `output.assets`/`inputs` arrays contain thousands of entries. A solver evaluating the order sees a profitable net trade (e.g., one large, real payout asset among thousands of dust entries) and calls `fillOrder`. Execution then iterates the full array, doing an external call and multiple storage writes (`_partialFills`, `escrowedInputs`, `outputFills`) per entry, which for a large enough array exceeds the destination chain's block gas limit and reverts the whole transaction — undoing any transfers already made in that same call. The solver has already paid for computing/submitting the transaction (or wasted gas on a revert) and receives nothing, while the order placer risks nothing (no escrow is pulled from them on a failed same-chain fill attempt by the solver, and cross-chain equivalents dispatch calldata built the same way).

This is the direct analog of the Juicebox `JBController.distributeReservedTokensOf` honeypot: an attacker-controlled unbounded array (there: `JBSplit[]`; here: `order.output.assets`/`order.inputs`) is processed in a loop by a function any unprivileged party can call to claim value, with no per-element minimum or overall length cap, letting the array's creator engineer a gas-limit DoS against the caller.

### Impact Explanation
An order placer can grief solvers (unprivileged, permissionless participants explicitly in the reachable threat model — "intent solver or bandwidth purchaser") into losing gas without receiving any of the promised output/escrow. Because the entire transaction reverts atomically when it runs out of gas, the solver's approvals/attempts are wasted and no funds move. Repeated across many orders, this is a systemic griefing vector against solver economics with no cost to the attacker beyond placing an order (which requires no escrow risk to be lost on a reverted fill attempt). This matches the Medium classification given to the original Juicebox report — real, permanent loss of solver gas, no direct fund theft, and severity moderated by solver tooling being able to simulate/estimate gas before submission (analogous to "wallet UI" mitigations noted by the C4 judge).

### Likelihood Explanation
Likelihood is meaningful but not certain to be exploited blindly: sophisticated solvers typically simulate (`eth_call`/gas estimation) before submitting, which would catch an obviously-oversized array before spending real gas. However: (1) an attacker can size the array so that gas usage is just below what naive estimation predicts under variable network conditions (e.g., cold vs warm storage slots for ERC-20 transfers to many distinct token addresses can shift actual gas usage unpredictably vs a simulation run in a different state), and (2) simpler/automatic solver bots (the SDK's `BidManager`/`OrderExecutor` auto-bidding flow shown in the codebase) may not defend against pathologically large arrays. No special privilege is needed by the attacker — placing an order is fully permissionless.

### Recommendation
- Enforce a maximum length on `order.inputs` and `order.output.assets` (and the corresponding `options.outputs`) at `placeOrder` time, rejecting orders whose array length exceeds a conservative, gas-budget-derived cap.
- Alternatively/additionally, bound the total gas the fill loop may consume, e.g., by capping asset count such that worst-case per-asset transfer cost (including cold SSTORE/cold external call overhead) stays well under the target chain's block gas limit with margin.
- Consider requiring a minimum `amount` per asset entry (mirroring Juicebox's suggested `MIN_SPLIT_PERCENT` fix) to make it uneconomical to pad an order with a large number of near-zero-value assets purely to inflate loop length.

### Proof of Concept
1. User calls `placeOrder` with `order.output.assets` (and matching `order.inputs`) containing N entries: N-1 dust ERC-20 outputs (e.g., amount = 1 wei each, distinct token addresses) plus 1 large, genuinely attractive output asset.
2. A solver observes the order, computes that filling it nets a profit from the large asset, and calls `fillOrder(order, options)` with `options.outputs` sized to match.
3. `_fillSameChain` iterates over all N assets: for each of the N-1 dust entries it still performs `IERC20(token).safeTransferFrom(...)`, `_partialFills` storage writes, and array writes to `escrowedInputs`/`outputFills`.
4. With N chosen large enough (each ERC-20 transfer touching a distinct cold contract/storage slot costs on the order of tens of thousands of gas), the total gas required exceeds the destination chain's block gas limit.
5. The transaction reverts in its entirety (all internal transfers rolled back), the solver's gas is spent, and the solver receives none of the escrowed input tokens promised by the order. [3](#0-2) [2](#0-1)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L443-480)
```text
    function fillOrder(Order calldata order, FillOptions calldata options) public payable nonReentrant {
        uint256 blockNumber = _blockNumber();
        if (order.deadline < blockNumber) revert Expired();
        // The solver's own bound on how long its quoted price stands. Zero means unbounded,
        // which is the right default for a solver filling directly — it is only at risk from
        // its own staleness. It matters for a bid signed through the coprocessor, where the
        // order placer chooses the moment of execution and nothing else caps the wait.
        if (options.validUntil != 0 && blockNumber > options.validUntil) revert FillExpired();
        bytes32 commitment = keccak256(abi.encode(order));

        address hostAddr = host();
        bytes32 currentChain = keccak256(IDispatcher(hostAddr).host());
        bytes32 orderSource = keccak256(order.source);
        bytes32 orderDest = keccak256(order.destination);
        bool isSameChain = orderSource == orderDest;

        if (isSameChain && orderSource != currentChain) revert WrongChain();
        if (!isSameChain && orderDest != currentChain) revert WrongChain();

        if (_filled[commitment] != address(0)) revert Filled();

        if (_params.solverSelection) {
            bytes32 storedSelectionHash;
            assembly {
                storedSelectionHash := tload(commitment)
            }

            bytes32 expectedSelectionHash = keccak256(abi.encode(msg.sender, order.session));
            if (storedSelectionHash != expectedSelectionHash) revert Unauthorized();
        }

        uint256 outputsLen = order.output.assets.length;
        if (options.outputs.length != outputsLen) revert InvalidInput();
        if (order.inputs.length != outputsLen) revert InvalidInput();

        if (isSameChain) {
            _fillSameChain(order, options, commitment);
        } else {
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-119)
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
```
