Confirmed: `EvmHost.sol` line 386 explicitly documents this: `receive() external payable {}` with comment `/* @dev receive function for UniswapV2Router02, collects all dust native tokens. */`. This confirms the excess ETH refunded by the Uniswap router from `swapETHForExactTokens` lands in `EvmHost`'s own balance as "dust" — it is not returned to the original caller who overpaid. There's a `withdraw()` function gated by `IHostManager`/`HostManager.onAccept`, but it is only reachable via a cross-chain governance `Withdraw` message from Hyperbridge, sweeping the balance to a beneficiary chosen by governance — not automatically refunding the specific overpaying user. This matches the reported bug class: user-supplied native ETH exceeding what's needed is permanently absorbed by the protocol with no path back to the depositor.

### Title
Excess native-ETH overpayment on `EvmHost.dispatch()`/`fundRequest()` is permanently absorbed by the protocol instead of refunded to the payer - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` are `payable` functions that accept `msg.value` and swap it via `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. Any ETH sent above what is needed to buy the exact `fee`/`amount` of fee token is refunded by the router to `msg.sender` of the swap call — which is `EvmHost` itself, not the original transaction caller — permanently trapping the payer's overpayment in the host contract.

### Finding Description
In `EvmHost.dispatch(DispatchPost memory post)`: [1](#0-0) 
the full `msg.value` is forwarded to `swapETHForExactTokens`, requesting exactly `post.fee` tokens. The recipient of the swapped fee tokens is set to `address(this)` (the host), and any unspent ETH is refunded by the standard Uniswap V2 router logic to its own caller — `EvmHost` — since `EvmHost` is the one invoking the router, not the user. The identical pattern exists in `dispatch(DispatchGet memory get)`: [2](#0-1) 
and in `fundRequest()`: [3](#0-2) 

The contract even documents this behavior explicitly with a `receive()` function labeled as collecting "dust": [4](#0-3) 

There is no logic anywhere in these three functions that computes `msg.value - actualSpent` and forwards the difference back to `_msgSender()`. Any caller who does not send the *exact* amount of native token required to purchase the fee (e.g., due to price movement between fee estimation off-chain and on-chain execution, or by mistake) loses the difference permanently to the protocol's balance. This mirrors the `receiveFunds()` bug class: a `payable` function has non-trivial ETH-consuming logic, but excess ETH supplied by the caller is not returned to that caller.

Recovery is only possible via a privileged cross-chain governance path — `HostManager.onAccept` → `IHostManager(_params.host).withdraw(withdrawParams)` — which sweeps the entire native balance to a beneficiary chosen by Hyperbridge governance, not automatically or verifiably back to the specific user who overpaid: [5](#0-4) 

### Impact Explanation
Any unprivileged dispatcher, relayer-fee funder, or app calling `dispatch()`/`fundRequest()` with slightly more native token than the exact swap requires (a very common occurrence given price slippage between off-chain fee quoting via `getAmountsIn` and actual on-chain execution, or simple user-side rounding/safety margins) permanently loses that excess ETH. It becomes indistinguishable "dust" absorbed into the host's balance, recoverable only by governance sweeping it to an arbitrary treasury address, not back to the user. Over the aggregate of all dispatch calls across a live network this constitutes a systemic, protocol-wide fund loss for legitimate users on every over-estimated fee quote.

### Likelihood Explanation
High. Exact-match funding of `swapETHForExactTokens` is fragile by construction — quoting tools (e.g., `sdk/packages/sdk/src/chains/evm.ts:quoteNative`) compute an *estimate* off-chain before the transaction lands, and any slippage, added safety buffer, or price movement between estimation and execution results in `msg.value > amountIn`. This is not an edge case but the expected common path for a payable fee-dispatch function, so every marginally-imprecise caller loses funds on every call.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, compute the ETH actually consumed (from the returned `amounts[0]`/spent value) and refund `msg.value - amountsIn[0]` directly to `_msgSender()` (or `post.payer`/`get.payer`), rather than allowing the router refund to land in and stay with `EvmHost`.

### Proof of Concept
1. Off-chain, a dApp calls `quoteNative()` to estimate the native ETH needed for a `relayerFee` of `X` fee-token units, adding a small buffer for price movement (standard practice, and demonstrated in the SDK's `quoteNative`). [6](#0-5) 
2. User calls `IDispatcher(host).dispatch{value: quotedAmount}(post)` where `quotedAmount` is slightly above the exact price at execution time (due to normal slippage/buffer).
3. Inside `dispatch`, `swapETHForExactTokens{value: msg.value}(post.fee, ...)` spends only the exact ETH needed to buy `post.fee` fee tokens; the router refunds the remainder to its caller, `EvmHost`. [1](#0-0) 
4. `EvmHost`'s `receive()` silently accepts this refund as host balance ("dust"): [4](#0-3) 
5. The user's overpayment is now part of the protocol's balance and can only be moved out via a Hyperbridge governance `Withdraw` message to a beneficiary of governance's choosing — never automatically credited back to the original user.

### Citations

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

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

**File:** evm/src/core/EvmHost.sol (L974-985)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }
```

**File:** evm/src/core/EvmHost.sol (L1031-1042)
```text
    function fundRequest(bytes32 commitment, uint256 amount) external payable notFrozen {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                amount, path, address(this), block.timestamp
            );
        } else {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), amount);
        }
```

**File:** evm/src/core/HostManager.sol (L144-148)
```text
        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.Withdraw) {
            // This is where governance & relayers can withdraw their revenue.
            WithdrawParams memory withdrawParams = abi.decode(request.body[1:], (WithdrawParams));
            IHostManager(_params.host).withdraw(withdrawParams);
```

**File:** sdk/packages/sdk/src/chains/evm.ts (L746-757)
```typescript
	async quoteNative(request: IPostRequest | IGetRequest, fee: bigint): Promise<bigint> {
		const totalFee = (await this.quote(request)) + fee
		const feeToken = await this.getFeeTokenWithDecimals()
		// Quote against the router the host actually swaps through on dispatch,
		// which may price differently than the canonical Uniswap V2 router.
		const hostRouter = await this.publicClient.readContract({
			address: this.params.host,
			abi: EvmHost.ABI,
			functionName: "uniswapV2Router",
		})
		return this.getAmountsIn(totalFee, feeToken.address, request.source, hostRouter)
	}
```
