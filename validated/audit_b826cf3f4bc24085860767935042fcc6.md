## Title
`EvmHost.dispatch()` reverts when a fee of zero is paid with native token, permanently bricking any message that legitimately carries `fee == 0` — ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` (and its `DispatchGet` counterpart) swaps `msg.value` for the requested `post.fee` via `swapETHForExactTokens` whenever the caller pays with native token. When `post.fee == 0` but `msg.value > 0`, the swap asks Uniswap V2 for an exact output of `0`, which reverts inside the pair contract (`UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT`). This is the same bug class as TRST-M-4: a zero value that should be a harmless/no-op branch is instead routed into an external AMM call that reverts on zero, and the revert happens deep enough that no fallback/cleanup logic runs — the entire dispatch (and whatever protocol action depended on it) fails.

### Finding Description
`EvmHost.dispatch(DispatchPost)` at [1](#0-0)  does:

```solidity
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } else if (post.fee > 0) {
        IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
    }
    ...
}
```

There is no branch for `post.fee == 0`. If a caller sends any non-zero `msg.value` while `post.fee` is `0` (e.g. self-relay flows, which the protocol's own documentation calls out as valid: "fee: relayerFee, // Optional: set to 0 for self-relay" [2](#0-1) ), the router is asked to produce exactly `0` output tokens for a non-zero ETH input. `swapETHForExactTokens` computes `amounts[amounts.length-1] == 0` and the underlying `UniswapV2Pair.swap` call requires `amount0Out > 0 || amount1Out > 0`, so the entire call reverts. The dispatch, and therefore whatever caller action triggered it (e.g. `cancelOrder`, `_cancelFromSource`/`_cancelFromDest` in the intents apps which call `IDispatcher(hostAddr).dispatch{value: msg.value}(request)` with a possibly-zero `relayerFee`), reverts entirely with no code path to skip the swap.

This exactly mirrors the bug class described in the report: a legitimate zero value (delta=0 / fee=0) should short-circuit to a no-op, but instead falls into a branch that calls an external AMM primitive that reverts on a zero-sized operation, and the calling code has no early-exit for that case.

Relevant call sites that can reach this with attacker/user-controlled zero fee plus non-zero `msg.value`: [3](#0-2) [4](#0-3) 

### Impact Explanation
Any message dispatch (POST or GET) paid for in native token with a zero relayer/protocol fee cannot be sent — the transaction reverts unconditionally at the Uniswap swap. In the intents apps, this directly blocks `cancelOrder`'s cross-chain paths (`_cancelFromSource`, `_cancelFromDest`) when a user sets `relayerFee = 0` (self-relay) but still attaches native value for the dispatch, freezing the escrowed input tokens/fees for that order since the refund-triggering message can never be dispatched via that code path. More broadly, it is a "route unable to deliver messages" condition for any `HyperApp` that dispatches with `fee: 0` and non-zero native `msg.value`, which the protocol's own documentation presents as a supported combination.

### Likelihood Explanation
This requires only a normal, permissionless call to `EvmHost.dispatch()` (or any app function that forwards to it) with `post.fee == 0` and `msg.value > 0` — no privileged role, governance, or malicious actor is needed. Because the documented self-relay pattern (`fee: 0`) is expected to be combined with dispatch calls that are `payable`, ordinary users following documented usage patterns can trigger this.

### Recommendation
Add an explicit branch in `EvmHost.dispatch()` (both `DispatchPost` and `DispatchGet` overloads) for `post.fee == 0`: skip the Uniswap swap entirely (and refund any `msg.value` sent, or simply not require/consume it) rather than calling `swapETHForExactTokens` with a zero output amount.

### Proof of Concept
1. Caller (any address) calls `EvmHost.dispatch(DispatchPost)` with `post.fee = 0` and sends `msg.value = 1 wei` (or any non-zero amount).
2. Execution enters the `msg.value > 0` branch and calls `swapETHForExactTokens(0, path, address(this), block.timestamp)` on the configured Uniswap V2 router.
3. The router computes `amounts[1] == 0` and calls `UniswapV2Pair.swap(0, 0, ...)`, which reverts with `UniswapV2: INSUFFICIENT_OUTPUT_AMOUNT`.
4. The entire `dispatch` call reverts, and any caller (e.g., `ExtrinsicIntents._post` invoked from `cancelOrder`) that relied on this dispatch to release escrow/refund tokens is permanently unable to complete that action while supplying a non-zero native value alongside a zero fee.

### Citations

**File:** evm/src/core/EvmHost.sol (L921-932)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
        }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L96-101)
```text
DispatchPost memory post = DispatchPost({
    // ... other fields
    fee: relayerFee,  // Optional: set to 0 for self-relay
    payer: msg.sender // Receives refund if request times out
});
```
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L254-275)
```text
        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```
