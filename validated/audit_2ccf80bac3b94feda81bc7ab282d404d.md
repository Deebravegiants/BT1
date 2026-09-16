### Title
`cancelOrder`'s same-chain route accepts `msg.value` but never uses or refunds it, permanently trapping user ETH - ([File: evm/src/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.cancelOrder()` is declared `payable` and dispatches to three internal routes depending on whether the order is same-chain or cross-chain. The cross-chain routes (`_cancelFromSource`, `_cancelFromDest`) genuinely consume `msg.value` to pay the Hyperbridge dispatch fee. The same-chain route, `_cancelSameChain`, does neither: it only reads escrow amounts and calls `_withdraw`, with no reference to `msg.value` anywhere in the function or its callees. Any ETH a user attaches when cancelling a same-chain order is silently absorbed by the contract with no refund path, mirroring the reported `requestERC20Service` bug class (payable function that does nothing with the ETH it receives). [1](#0-0) 

### Finding Description
`cancelOrder` is marked `payable` unconditionally, even though only two of its three routes actually spend `msg.value`:

- `_cancelFromSource` forwards `msg.value` to `IDispatcher(hostAddr).dispatch{value: msg.value}(request)` to pay for the ISMP GET dispatch fee. [2](#0-1) 
- `_cancelFromDest` forwards `msg.value` into `_post(..., msg.value)` to pay for the RefundEscrow dispatch fee. [3](#0-2) 
- `_cancelSameChain`, however, only verifies the caller is `order.user`, reads remaining escrow via `_orders[commitment][token]`, and calls `_withdraw(body, true, true)`. There is no read of `msg.value`, no forwarding to any dispatcher, and no refund of unspent native tokens (unlike `_fillSameChain` and `placeOrder`, which explicitly refund any leftover `msgValue` via `_sendValue`). [4](#0-3) 

Because `cancelOrder` is a single `payable` entrypoint that branches internally, the contract cannot reject ETH sent along a same-chain cancel at the ABI level — a caller who mistakes `cancelOrder` for `fillOrder`/`placeOrder` semantics (both of which do use and refund `msg.value`), or who reuses boilerplate that always attaches a native fee, will have that ETH accepted by `receive() external payable {}` and left with no code path that returns it. The receiving contract has a `receive()` fallback specifically to accept ETH for escrow/fee purposes, so the ETH is not rejected — it is accepted and stuck. [5](#0-4) 

The comparison across the codebase's own SDK/docs shows the intended usage is `value: 0n` for a same-chain cancel and `relayerFee`/native fee only for cross-chain cancels — confirming same-chain cancel was never meant to carry value, yet the contract signature does not enforce this. [6](#0-5) 

### Impact Explanation
Any ETH sent with a same-chain `cancelOrder` call becomes permanently locked in the `IntentGatewayV2` contract. There is no user-facing withdrawal function for arbitrary stuck ETH; the only outward-flowing native paths are `_withdraw` (escrow refunds tied to specific order commitments) and governance-only `SweepDust` (dispatched only by Hyperbridge itself via `onAccept`). A user's mistakenly attached ETH is not tied to any order commitment and can never be recovered by that user — a permanent loss of funds for the caller, matching the "permanent freezing of funds" bar for a valid finding.

### Likelihood Explanation
This is directly reachable by any unprivileged order owner cancelling their own same-chain order — no privileged role, relayer, or cross-chain proof is required. The likelihood of the mistake occurring depends on off-chain client behavior (e.g., mis-estimating a "relayer fee" value for a same-chain cancel, or reusing calldata patterns from `fillOrder`/`cancelOrder`-cross-chain paths that do require value), but nothing in the contract prevents or reimburses it, unlike the deliberate refund logic present in `placeOrder` and `_fillSameChain`.

### Recommendation
Either:
1. Make `cancelOrder` non-payable and require callers to send fees only via a separate, cross-chain-specific path, or
2. Keep `cancelOrder` payable for the cross-chain fee-paying routes, but add an explicit refund of any unspent `msg.value` in `_cancelSameChain` (mirroring the pattern already used in `_fillSameChain` and `placeOrder`), e.g. call `_sendValue(msg.sender, msg.value)` when the same-chain branch is taken.

### Proof of Concept
1. User places a same-chain order via `placeOrder` (`order.source == order.destination`).
2. User calls `intentGateway.cancelOrder{value: 1 ether}(order, cancelOptions)` where `currentChain == orderSource == orderDest` (same-chain branch).
3. Execution routes to `_cancelSameChain`, which never reads `msg.value`; the 1 ETH remains in the contract's balance, credited to no order and refundable to no one via any existing user-callable function.
4. Compare with the cross-chain routes (`_cancelFromSource`/`_cancelFromDest`), where an equivalent `value:` param is consumed by `dispatch{value: msg.value}(...)`/`_post(..., msg.value)` — confirming the same-chain branch is the one lacking any use of the attached ETH. [7](#0-6)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L76-82)
```text

    /**
     * @dev Allows the contract to receive native tokens (ETH/DOT/etc).
     * Required for escrow deposits with native tokens and for receiving
     * swept balances from the CallDispatcher.
     */
    receive() external payable {}
```

**File:** evm/src/apps/IntentGatewayV2.sol (L505-537)
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

        if (isSameChain) {
            // Checked here rather than inside `_cancelSameChain`, which used to re-read `host()`,
            // re-query the host's state machine id and re-hash `order.source` to reach the same
            // answer this function already has. Same check, one external call fewer.
            if (currentChain != orderSource) revert WrongChain();
            _cancelSameChain(order, commitment);
        } else if (currentChain == orderSource) {
            _cancelFromSource(order, options, commitment);
        } else if (currentChain == orderDest) {
            _cancelFromDest(order, options, commitment);
        } else {
            revert WrongChain();
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L269-275)
```text
        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L297-307)
```text
    function _cancelFromDest(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.deadline >= _blockNumber()) {
            if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();
        }

        _filled[commitment] = address(uint160(uint256(order.user)));

        _post(
            order, _body(RequestKind.RefundEscrow, commitment, order.inputs, order.user), options.relayerFee, msg.value
        );
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

**File:** sdk/packages/sdk/src/protocols/intents/OrderCanceller.ts (L219-231)
```typescript
		if (isSameChain) {
			const data = encodeFunctionData({
				abi: IntentGatewayV2ABI,
				functionName: "cancelOrder",
				args: [transformOrderForContract(order), { relayerFee: 0n, height: 0n }],
			}) as HexString

			const signedTransaction = yield {
				status: "AWAITING_CANCEL_TRANSACTION" as const,
				data,
				to: intentGatewayAddress,
				value: 0n,
			}
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L513-525)
```text
        // User cancels order before deadline (same-chain allows this)
        vm.startPrank(user);
        CancelOptions memory cancelOpts = CancelOptions({height: uint64(block.number), relayerFee: 0});

        // `OrderCancelled` announces the cancel, `EscrowRefunded` closes it — in that order,
        // so a consumer applying statuses in log order settles on the refund.
        vm.expectEmit(true, false, false, true, address(intentGateway));
        emit IntentsBase.OrderCancelled(keccak256(abi.encode(order)), user);
        vm.expectEmit(true, false, false, false, address(intentGateway));
        emit IntentsBase.EscrowRefunded(keccak256(abi.encode(order)), inputs);

        intentGateway.cancelOrder(order, cancelOpts);
        vm.stopPrank();
```
