### Title
Unbounded `order.inputs` / `order.output.assets` arrays in `IntentGatewayV2.placeOrder` can make an order permanently unfillable and un-cancellable, freezing escrowed funds - (File: `evm/src/apps/intentsv2/IntentGatewayV2.sol`, `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`placeOrder` accepts an `Order` whose `inputs` and `output.assets` arrays have no length cap, and every downstream path that must process the order — `fillOrder`/`select`, dust-sweep in `_execute`, and cancellation via `_withdraw` — iterates once per array element with external token transfers per iteration. A single unprivileged caller who submits an order with a very large `inputs`/`output.assets` array can make the resulting escrow permanently stuck: no solver can ever fit a full fill inside the block gas limit, and cancellation, which loops over the same arrays, can be pushed past the gas limit as well.

### Finding Description
`placeOrder` only checks `order.inputs.length == 0` [1](#0-0)  before looping over `inputsLen` for fee reduction, escrow crediting, and (optionally) predispatch/call-dispatcher transfers [2](#0-1) . There is no `MAX_INPUTS`/`MAX_OUTPUTS` bound anywhere in this contract family — the same unbounded pattern also exists in the parallel Tron deployment of `placeOrder` [3](#0-2) .

Filling the order (`fillOrder`/`IntrinsicIntents` fill path) must iterate over the same `order.inputs`/`order.output.assets` arrays, performing a `safeTransferFrom` or native transfer per output token and computing escrow release per input token [4](#0-3) . After a full fill, `_execute` additionally loops over `outputsLen` to sweep dust from the `CallDispatcher` back to the gateway, one external balance check and potential transfer per output asset [5](#0-4) .

Because the order placer fully controls the length and shape of `inputs` and `output.assets` (subject only to `inputs.length != 0`), they can construct an order with hundreds or thousands of low-value entries (e.g. many distinct low-decimals ERC-20s or duplicated dust legs where allowed). The escrow step in `placeOrder` still succeeds (it is paid for by the placer, who controls the gas budget of their own transaction and can afford it, e.g. by batching or accepting a high but singular gas cost), but the corresponding `fillOrder` call — which must move funds for every leg in a single atomic transaction, funded by a third-party solver — can be pushed past the block gas limit. No solver can then ever complete the fill, and the escrowed input tokens become permanently stuck in the `IntentGatewayV2` contract, since the *only* other way to reclaim them is cancellation, which itself loops over the same `inputs` array during `_withdraw`/refund and is subject to the identical gas ceiling.

This is the same bug class as the referenced Sherlock report: an actor-controlled, unbounded array embedded in an on-chain order structure that a *different, unprivileged* party must fully iterate over in a single transaction to complete a state transition, with no cap enforced at the point where the array is first accepted.

### Impact Explanation
If the escrow becomes gas-locked, the user's `inputs` tokens (and any `predispatch`/`fees` amounts already pulled into the contract) are permanently frozen: `fillOrder` cannot succeed for solvers within the block gas limit, and cancellation is bounded by the exact same unbounded loop, so refund can also fail. This is a permanent freezing-of-funds condition triggered by a single `placeOrder` transaction from any unprivileged user (potentially self-inflicted, but also weaponizable against solvers who must simulate/execute fills, DoSing solver liquidity or wasting solver gas on reverted fill attempts near the gas boundary).

### Likelihood Explanation
Likelihood is Medium: nothing prevents a user (accidentally, via a buggy off-chain tool, or maliciously to grief solver infrastructure or lock their own funds for reputational/griefing reasons) from submitting an order with a very large `inputs`/`output.assets` array, since `placeOrder` performs no cap check on array length before escrowing.

### Recommendation
Enforce a maximum length (e.g. a small constant such as 8–16) on `order.inputs.length` and `order.output.assets.length` inside `placeOrder`, rejecting orders that exceed it before any tokens are escrowed, in both `evm/src/apps/intentsv2/IntentGatewayV2.sol` and the Tron variant `evm/tron/contracts/apps/IntentGatewayV2.sol`. This bounds the worst-case gas cost of `fillOrder`, `_execute`'s dust sweep, and cancellation's refund loop, ensuring every escrowed order remains fillable or cancellable within the block gas limit.

### Proof of Concept
1. Attacker (or any user) calls `placeOrder` with `order.inputs` containing N (e.g., 500) distinct low-value ERC-20 legs and/or `order.output.assets` containing N output legs, each individually small enough to be economically viable but collectively large.
2. `placeOrder` succeeds: no array-length check beyond non-empty exists [1](#0-0) , and tokens are escrowed per-input in the loop at lines 313-329/364-373.
3. Any solver attempting `fillOrder` must loop over all N output legs (transfers) and N input legs (escrow release) in one transaction [4](#0-3)  plus the `_execute` dust-sweep loop over `outputsLen` [5](#0-4) ; at sufficiently large N this exceeds the block gas limit and every fill attempt reverts.
4. Cancellation is bounded by the same `order.inputs` length in the refund path, so it can likewise fail to execute within gas limits, leaving the escrowed tokens permanently locked in the contract.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-469)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        // Calculate reduced inputs (after protocol fees) for commitment and escrow
        uint256 inputsLen = order.inputs.length;
        // Use destination-specific protocol fee, fallback to source chain fee if zero
        bytes32 destinationHash = keccak256(order.destination);
        uint256 protocolFeeBps = _destinationProtocolFees[destinationHash];
        if (protocolFeeBps == 0) {
            protocolFeeBps = _params.protocolFeeBps;
        }
        TokenInfo[] memory reducedInputs;
        bytes32 commitment;

        if (protocolFeeBps > 0) {
            reducedInputs = new TokenInfo[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                uint256 originalAmount = order.inputs[i].amount;
                uint256 protocolFee = (originalAmount * protocolFeeBps) / 10_000;
                uint256 reducedAmount = originalAmount - protocolFee;
                address token = address(uint160(uint256(order.inputs[i].token)));

                // Emit DustCollected for protocol fee if non-zero
                if (protocolFee > 0) emit DustCollected(token, protocolFee);

                reducedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: reducedAmount});
                unchecked {
                    ++i;
                }
            }

            // Temporarily swap inputs to calculate commitment with reduced amounts
            TokenInfo[] memory originalInputs = order.inputs;
            order.inputs = reducedInputs;
            commitment = keccak256(abi.encode(order));
            order.inputs = originalInputs;
        } else {
            // No protocol fees, use order.inputs directly
            reducedInputs = order.inputs;
            commitment = keccak256(abi.encode(order));
        }

        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L91-119)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }
```
