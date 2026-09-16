### Title
Unbounded user-controlled `order.inputs` / `order.output.assets` arrays in `IntentGatewayV2` can cause `placeOrder`, `fillOrder`, `cancelOrder`, and escrow `_withdraw` to run out of gas, permanently freezing escrowed funds - (File: evm/src/apps/IntentGatewayV2.sol, evm/src/apps/intentsv2/IntentsBase.sol, evm/src/apps/intentsv2/IntrinsicIntents.sol, evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
`IntentGatewayV2.placeOrder` accepts an `Order` whose `inputs`, `output.assets`, and `predispatch.assets` arrays have no enforced upper bound — only `order.inputs.length == 0` is rejected. Every downstream code path that operates on an order (`placeOrder`, `fillOrder`/`_intrinsicFill`, `cancelOrder`/`_cancelFromSource`/`_cancelFromDest`/`_cancelSameChain`, and the escrow-release helper `_withdraw`) iterates these same arrays with `for` loops that perform a `safeTransferFrom`/`safeTransfer`/native `.call` per element. A user who places an order with an excessively long `inputs`/`output.assets` array can make these loops exceed the block gas limit (or a relayer's/handler's fixed gas budget), causing the transaction to always revert.

### Finding Description
`placeOrder` only checks that `order.inputs.length` is non-zero, with no maximum: [1](#0-0) 

It then loops over `order.output.assets` for duplicate-detection (twice) and over `order.inputs`/`order.predispatch.assets` for token transfers and escrow crediting, each iteration doing an external token transfer: [2](#0-1) [3](#0-2) 

The same unbounded pattern recurs in the fill path (`IntrinsicIntents._intrinsicFill`, iterating `order.output.assets`) and in cancellation (`ExtrinsicIntents._cancelFromSource`/`_cancelFromDest`, `IntrinsicIntents._cancelSameChain`, iterating `order.inputs`): [4](#0-3) [5](#0-4) [6](#0-5) 

Most critically, the escrow-release function `_withdraw` — which is invoked by `onAccept` when a `RedeemEscrow`/`RefundEscrow` cross-chain message is delivered by Hyperbridge (via the relayer's `HandlerV2.handlePostRequests` call) — loops over `body.tokens` (== `order.inputs`) performing one `IERC20.safeTransfer`/native send per token, with no bound on array length: [7](#0-6) 

Because this loop executes inside a message delivered by a relayer with a fixed/estimated gas budget (see `generate_contract_calls`, which estimates gas per message and applies a buffer), an order with a sufficiently long `inputs` array can make `_withdraw`'s gas cost exceed what any relayer will provide or what fits in a block, permanently blocking delivery of the `RedeemEscrow`/`RefundEscrow` message and freezing the escrowed tokens with no alternate recovery path. [8](#0-7) 

### Impact Explanation
An order creator (or a solver being griefed by a maliciously-crafted counterpart order) fully controls the length of `order.inputs`/`order.output.assets` at `placeOrder` time. If that array is made large enough, later required operations on the same commitment — filling, cancelling, or the escrow release triggered by the cross-chain `RedeemEscrow`/`RefundEscrow` `onAccept` handler — will consistently run out of gas and revert. Because `_withdraw` is the only path that releases escrowed funds (`_orders[commitment][token]`), and it is driven by an ISMP post-request delivered through the fixed-gas relayer/handler pipeline, this can result in permanent freezing of the escrowed input tokens: the order can never be filled (fill loop reverts), never cancelled (cancel loop / `_withdraw` reverts), and the relayer can never successfully deliver the refund/redeem message. This is a fund-freezing DoS reachable from a single `placeOrder` transaction.

### Likelihood Explanation
Likelihood is moderate-to-high: `placeOrder` performs no bound check on `order.inputs.length` or `order.output.assets.length` beyond non-zero, and array elements are cheap to add off-chain (only bounded by calldata size and the caller's own upfront token transfers for legitimate use, but a caller can supply many low/zero-value or duplicate-style entries as long as duplicate-token checks are bypassed with distinct token addresses). No special privilege is required — any unprivileged user can submit such an order via a single transaction.

### Recommendation
Enforce a reasonable maximum on `order.inputs.length`, `order.output.assets.length`, and `order.predispatch.assets.length` in `placeOrder` (mirroring the zero-length check at `evm/src/apps/IntentGatewayV2.sol:195`), sized so that every downstream loop (`_intrinsicFill`, `_cancelFromSource`/`_cancelFromDest`/`_cancelSameChain`, and especially `IntentsBase._withdraw`) is guaranteed to complete within the gas budget the relayer/handler pipeline provides.

### Proof of Concept
1. Call `IntentGatewayV2.placeOrder` with an `Order` whose `inputs` array contains N distinct ERC-20 tokens (N large, e.g. several hundred), each with a minimal balance/allowance to pass `safeTransferFrom`; `placeOrder` has no upper-bound check (`evm/src/apps/IntentGatewayV2.sol:195`) so this succeeds, though gas cost scales with N in the escrow-credit loop (`evm/src/apps/IntentGatewayV2.sol:364-373`).
2. On the destination chain, a solver calls `fillOrder`; `_intrinsicFill`'s loop over `order.output.assets`/inputs (`evm/src/apps/intentsv2/IntrinsicIntents.sol:61-119`) similarly scales with array size — a large enough output array makes the fill transaction exceed the block gas limit and always revert.
3. If the order times out, `_cancelFromDest` dispatches a `RefundEscrow` post-request back to the source chain (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:297-307`). When Hyperbridge relays and delivers this message, `onAccept` invokes `_withdraw` (`evm/src/apps/intentsv2/IntentsBase.sol:451-470`), which loops once per input token performing a token transfer. With N large enough, this loop's gas cost exceeds the gas the relayer estimates/provides (`tesseract/messaging/evm/src/tx.rs:298-315`) or the block gas limit, causing `handlePostRequests` to revert every time it is attempted, permanently preventing the refund and freezing the escrowed tokens.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-196)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
        if (order.inputs.length == 0) revert InvalidInput();

```

**File:** evm/src/apps/IntentGatewayV2.sol (L228-270)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L361-373)
```text
        commitment = keccak256(abi.encode(order));

        // Phase 3: Credit escrow.
        for (uint256 i; i < inputsLen;) {
            address token = address(uint160(uint256(order.inputs[i].token)));
            // Reject duplicate input tokens
            if (_orders[commitment][token] != 0) revert InvalidInput();
            _orders[commitment][token] = reducedInputs[i].amount;

            unchecked {
                ++i;
            }
        }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L61-119)
```text

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

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L159-180)
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
        if (!hasEscrow) revert UnknownOrder();

        WithdrawalRequest memory body =
            WithdrawalRequest({commitment: commitment, tokens: remainingTokens, beneficiary: order.user});

        _withdraw(body, true, true);
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L245-252)
```text
        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
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

**File:** tesseract/messaging/evm/src/tx.rs (L298-315)
```rust
			Message::Request(msg) => {
				let (mmr_proof, leaf_indices) = decode_mmr_proof(&msg.proof.proof)?;
				let mut leaves: Vec<PostRequestLeaf> = msg
					.requests
					.iter()
					.zip(&leaf_indices)
					.map(|(post, &leaf_index)| PostRequestLeaf {
						request: post.clone().into(),
						index: AlloyU256::from(leaf_index),
					})
					.collect();
				leaves.sort_by_key(|l| l.index);
				let proof = build_solidity_proof(&mmr_proof, &msg.proof.height)?;
				let call = contract
					.handlePostRequests(ismp_host, PostRequestMessage { proof, requests: leaves });
				let gas = call.estimate_gas().await.unwrap_or_else(|_| chain_gas_limit / 4);
				(call.calldata().clone(), gas_with_buffer(gas))
			},
```
