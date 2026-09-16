### Title
IntentGatewayV2 order placement allows an unprivileged order creator to set a zero-address output beneficiary, causing solver funds to be permanently burned on fill - (File: evm/src/apps/intentsv2/IntrinsicIntents.sol / evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`placeOrder` accepts an arbitrary, caller-supplied `order.output.beneficiary` with no validation that it is non-zero [1](#0-0) . This beneficiary is later used as the destination address for tokens the **solver** transfers when filling the order, both for same-chain fills [2](#0-1)  and cross-chain fills [3](#0-2) . Neither `_fillSameChain`, `_fillCrossChain`, nor `_withdraw` check `beneficiary != address(0)` anywhere in the codebase (no `ZeroAddress`/`InvalidBeneficiary` checks exist in `evm/src/apps/**/*.sol`).

### Finding Description
An order creator calling `placeOrder` fully controls `order.output.beneficiary` (`bytes32`), which is stored as-is in the order and later decoded to an `address` via `address(uint160(uint256(order.output.beneficiary)))`:
- In `_fillSameChain`, this address receives the solver's `safeTransferFrom`/native-value payment directly (`beneficiaryTotal`) [4](#0-3) .
- In `_fillCrossChain`, the solver similarly pays `beneficiary` directly via `safeTransferFrom`/`_sendValue` [5](#0-4) .

If the order creator sets `output.beneficiary = bytes32(0)`, the solver's output payment (the tokens/ETH the solver is compelled to send in order to claim the escrowed input tokens) is sent to `address(0)`, permanently burning it. This is analogous to the reported `TimeLockPool#increaseLock` bug class: an unvalidated, attacker-controlled receiver/beneficiary parameter allows funds belonging to a party other than the caller (here, the solver, not just the order creator) to be irrecoverably destroyed. Unlike the refund/cancel paths, which correctly always route funds back to `order.user` (the escrow refund beneficiary is hardcoded to `order.user`, not `output.beneficiary`) [6](#0-5) , the fill path lets an untrusted, unprivileged order placer dictate an arbitrary destination for the solver's payment with zero validation.

### Impact Explanation
Any unprivileged user can place a same-chain or cross-chain order with `output.beneficiary = 0`. A solver who is unaware of this and fills the order (the contract provides no on-chain or documented protection against it) will have their output tokens (potentially significant value, e.g. matching or exceeding the escrowed input amount) sent to the burn address `0x0`, an irreversible loss of funds for the solver. Because filling an order is a permissionless, automated process (solvers programmatically scan and fill profitable orders), a malicious actor could place a stream of zero-beneficiary orders to systematically burn solver liquidity, or accidentally-formed clients (e.g., off-chain bugs producing a zero beneficiary) could destroy user/solver funds with no recovery path. This satisfies "concrete theft or permanent freezing of funds" from the validation criteria — funds are unrecoverably destroyed.

### Likelihood Explanation
Likelihood is Medium: placing an order with a zero beneficiary requires no special privilege — it's a normal `placeOrder` call reachable by any address, and there's no client-side or on-chain guardrail preventing it. The main mitigating factor is that a rational solver's off-chain matching engine might sanity-check destination addresses before filling, but the on-chain contract offers no protection, so any client bug, malicious actor, or naive solver integration is directly exposed.

### Recommendation
Add validation in `placeOrder` (and/or at the start of `_fillSameChain`/`_fillCrossChain`) that `order.output.beneficiary != bytes32(0)`, reverting with a dedicated error (e.g., `InvalidBeneficiary()`) if it is zero. This mirrors the original report's recommended fix of requiring `_receiver != address(0)` before any operation that transfers funds to a user-controlled receiver.

### Proof of Concept
1. Attacker calls `intentGateway.placeOrder(order, graffiti)` on `evm/src/apps/IntentGatewayV2.sol` with `order.output.beneficiary = bytes32(0)` and legitimate `inputs`/`output.assets` — this succeeds because `placeOrder` never validates `beneficiary` [7](#0-6) .
2. A solver observes the order and calls `fillOrder`, which routes into `_fillSameChain` (same-chain) or `_fillCrossChain` (cross-chain).
3. In `_fillSameChain`, `beneficiary = address(uint160(uint256(order.output.beneficiary)))` evaluates to `address(0)`; the solver's `IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal)` (or native `.call{value: beneficiaryTotal}`) sends the solver's payment straight to the zero address [4](#0-3) .
4. The solver still receives the escrowed input tokens via `_withdraw`, but their own output payment is permanently burned — a net loss with no possibility of recovery, since the tokens sent to `address(0)` cannot be retrieved by any subsequent contract call.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-270)
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
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L59-106)
```text
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L164-196)
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
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L254-255)
```text
        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));
```
