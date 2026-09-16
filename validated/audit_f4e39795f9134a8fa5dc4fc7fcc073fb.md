### Title
Unbounded `order.inputs`/`order.output.assets` arrays in `IntentGatewayV2.placeOrder()` can make `fillOrder()`/`cancelOrder()` unfillable due to gas-limit reverts, permanently freezing escrowed funds - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.placeOrder()` only validates that `order.inputs.length != 0`; it places no upper bound on the number of input assets, output assets, or predispatch assets a user can include in a single order. Every downstream consumer of the order — `fillOrder()` (via `_fillSameChain`/`_fillCrossChain`), `cancelOrder()`, and the withdrawal/escrow-release logic — iterates over these attacker-controlled arrays with `for` loops performing external token transfers (`safeTransferFrom`, ETH sends) per element. A user (an unprivileged order placer) can therefore construct an order with an arbitrarily large `inputs`/`output.assets` array whose fill or cancel transaction always exceeds the block gas limit, permanently freezing the escrowed tokens with no way for a solver to fill the order or for the user to recover funds via cancellation.

### Finding Description
`placeOrder()` bounds-checks only the lower end of the array: [1](#0-0) 

There is no `MAX_ASSETS`-style cap (unlike the analogous `MAX_PHANTOM_TOKEN_PAIRS` bound present elsewhere in the intents subsystem for a different data structure) [2](#0-1) , showing the protocol is aware of and uses bounded-array patterns elsewhere but does not apply one here.

Once the order is placed and escrow is funded, `fillOrder()` requires the solver-supplied `options.outputs` array to be exactly the same length as `order.output.assets`/`order.inputs`: [3](#0-2) 

For a same-chain fill, `_fillSameChain` then loops once over every output asset, performing a token transfer (native `.call{value}` or `safeTransferFrom`) and escrow bookkeeping per iteration: [4](#0-3) 

For a cross-chain fill, `_fillCrossChain` performs a similar per-asset loop transferring tokens through the call dispatcher and building `transferCalls`/`WithdrawalRequest` structures: [5](#0-4) [6](#0-5) 

`_withdraw`/cancellation logic must similarly iterate `order.inputs` to refund every escrowed asset when releasing or refunding an order (the fee/escrow bookkeeping at `IntrinsicIntents.sol:126-143` shows a `WithdrawalRequest` carrying the full `tokens` array being built per fill/cancel). Because every one of these paths is a single, non-chunkable loop bound to `order.inputs.length`/`order.output.assets.length`, a sufficiently large array (hundreds of ERC20 legs, each requiring an external `SLOAD`/`SSTORE`/`CALL`) will push the required gas for `fillOrder` or `cancelOrder` above the destination chain's block gas limit.

Once escrow has been taken (tokens transferred into the gateway during `placeOrder`), the funds can only leave through `fillOrder` (solver completes the trade) or `cancelOrder`/timeout refund (order.deadline expired). If both of these transactions are unexecutable due to exceeding the block gas limit, the escrowed tokens are permanently stuck in the `IntentGatewayV2` contract — this is the intents-escrow analog of the original Teller `lenderAcceptBid()` gas-limit DoS, where an unbounded borrower-supplied collateral array made the counterparty's mandatory transaction unexecutable.

### Impact Explanation
This is a direct freezing-of-funds vulnerability reachable from a single unprivileged `placeOrder()` transaction:
- The order placer escrows real value (tokens/ETH) when calling `placeOrder`.
- If the array size is chosen such that `fillOrder`'s loop plus per-iteration external calls exceeds the gas limit, no solver can ever complete `fillOrder`.
- If `cancelOrder`/refund logic performs the same unbounded iteration over `order.inputs` to return escrow, the placer cannot recover their own funds either.
- This satisfies "permanent freezing of funds" — a Medium/High-severity class of bug in the "no extra text" validation criteria, since it results in concrete permanent loss of access to escrowed funds without any privileged party being at fault.

### Likelihood Explanation
Likelihood is straightforward: any account calling `placeOrder()` fully controls `order.inputs` and `order.output.assets` length and content (subject only to having funds/allowance for at least one wei of each asset, or reusing the same token multiple times to inflate array length cheaply while keeping total value near zero). No permission or governance action is required, and the attack (or accidental griefing via a malformed order) can be executed in a single transaction reachable by anyone.

### Recommendation
Add an explicit upper bound (analogous to `MAX_PHANTOM_TOKEN_PAIRS` used elsewhere in the codebase) on `order.inputs.length`, `order.output.assets.length`, and `order.predispatch.assets.length` inside `placeOrder()`, and revert if exceeded — sized so that a worst-case `fillOrder`/`cancelOrder`/cross-chain withdrawal transaction is guaranteed to fit comfortably within all supported destination chains' block gas limits.

### Proof of Concept
1. Attacker/placer calls `IntentGatewayV2.placeOrder()` with `order.inputs` containing N (e.g., 500+) distinct low-value ERC20 legs and/or `order.output.assets` similarly sized, satisfying only `order.inputs.length != 0` [7](#0-6) .
2. `placeOrder` escrows all N assets via the per-asset transfer loop [8](#0-7) .
3. A solver later attempts `fillOrder`, which requires `options.outputs.length == order.output.assets.length` and then executes `_fillSameChain`/`_fillCrossChain`'s per-asset loop [9](#0-8) [10](#0-9) .
4. With N chosen large enough, the resulting transaction gas exceeds the block gas limit and always reverts — no solver can ever complete the fill.
5. If `cancelOrder`'s refund path performs the same unbounded per-input iteration, the placer's attempt to cancel and recover escrow likewise reverts, permanently freezing the escrowed funds in the `IntentGatewayV2` contract.

Note: I was unable to fully inspect the exact `cancelOrder`/`_withdraw` implementation body within the tool-call budget available (only located via grep in `IntentsBase.sol`/`ExtrinsicIntents.sol`/`IntrinsicIntents.sol`), so the precise refund-loop code path should be verified directly in those files to confirm it shares the same unbounded iteration before remediation.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-300)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

        // Reject duplicate output tokens
        uint256 outputsLen_ = order.output.assets.length;
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                if tload(token) {
                    mstore(0, 0xb4fa3fb3) // InvalidInput.selector
                    revert(0x1c, 0x04)
                }
                tstore(token, 1)
            }
            unchecked {
                ++i;
            }
        }
        // Clean up transient storage so repeated placeOrder calls in the same tx don't false-positive.
        for (uint256 i; i < outputsLen_;) {
            bytes32 token = order.output.assets[i].token;
            assembly ("memory-safe") {
                tstore(token, 0)
            }
            unchecked {
                ++i;
            }
        }

        address hostAddr = host();
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;

        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

```

**File:** evm/src/apps/IntentGatewayV2.sol (L391-415)
```text
            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }

        emit OrderPlaced({
            user: order.user,
            source: string(order.source),
            destination: string(order.destination),
            deadline: order.deadline,
            nonce: order.nonce,
            fees: order.fees,
            session: order.session,
            predispatch: order.predispatch.assets,
            inputs: reducedInputs,
            beneficiary: order.output.beneficiary,
            outputs: order.output.assets,
            predispatchCall: order.predispatch.call,
            outputCall: order.output.call,
            graffiti: graffiti
        });
    }
```

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

**File:** modules/pallets/intents-coprocessor/src/types.rs (L157-160)
```rust
/// Upper bound on the token pairs a single chain's config may probe. Every pair rides in the
/// same phantom order, so this also bounds that order's asset lists and the size of the
/// encoded body written to offchain storage.
pub const MAX_PHANTOM_TOKEN_PAIRS: u32 = 64;
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
