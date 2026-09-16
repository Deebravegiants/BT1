## Title
Native-fee dispatch swap in `EvmHost.dispatch` executes at unprotected AMM spot price, enabling sandwich extraction of user-attached relayer fees - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch()` lets any caller pay the relayer fee for a POST request in native ETH instead of the `feeToken`. When `msg.value > 0`, the host performs an on-chain swap through a configurable Uniswap-V2-compatible router/wrapper (`_hostParams.uniswapV2`) using `swapETHForExactTokens`, with the entire `msg.value` implicitly acting as the maximum-input bound and no oracle or deviation check against the AMM's spot price. This mirrors exactly the reported `SponsorVault` bug class: a protocol contract performs an unbounded, spot-priced AMM swap of native token for another asset on every user-triggered transaction, letting a searcher sandwich the swap and extract value from the swap's price impact.

### Finding Description
In the dispatch path: [1](#0-0) 

```solidity
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        address[] memory path = new address[](2);
        address uniswapV2 = _hostParams.uniswapV2;
        path[0] = IUniswapV2Router02(uniswapV2).WETH();
        path[1] = feeToken();
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } ...
```

The call requests an *exact output* of `post.fee` feeToken units, funded by up to the caller's entire `msg.value` of ETH. There is no `amountInMax` distinct from `msg.value`, no comparison against an oracle-derived fair price, and `deadline` is simply `block.timestamp` (no MEV-time protection either). When the configured router is the project's own `UniV3UniswapV2Wrapper`, the actual bound passed to the V3 router is explicitly `msg.value`: [2](#0-1) 

```solidity
IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
    tokenIn: weth,
    tokenOut: path[1],
    fee: _params.maxFee,
    recipient: recipient,
    amountOut: amountOut,
    amountInMaximum: msg.value,
    sqrtPriceLimitX96: 0
});
```

`sqrtPriceLimitX96: 0` disables price-limit protection entirely, and `amountInMaximum` is simply whatever ETH the user attached — not a slippage-bounded quote. The user/SDK determines `msg.value` off-chain by querying the router's *current* spot price via `getAmountsIn`/`quoteNative` before submitting the transaction: [3](#0-2) 

Because the on-chain swap enforces no independent price bound (only "spend up to the entire pre-computed `msg.value`"), a searcher can:
1. Front-run the dispatch transaction, buying feeToken (or selling ETH into the WETH/feeToken pool) to push the spot exchange rate against the user.
2. Let the victim's `dispatch()` call execute, consuming a much larger fraction of `msg.value` than the fair-market cost of `post.fee` feeToken (since `amountInMaximum` was already set to the *entire* attached ETH, there is no independent minimum-output/maximum-price check preventing this).
3. Back-run to restore the pool price and capture the ETH/feeToken spread as profit, extracted directly out of the value the victim attached to pay their relayer fee.

This is architecturally identical to the reported `SponsorVault.reimburseLiquidityFees` finding: a spot-priced AMM swap of native token for another asset, funded from a user-controlled/protocol-controlled balance, with no oracle-based deviation guard, executed inside a state-changing entry point reachable by any address.

### Impact Explanation
Any unprivileged caller of `EvmHost.dispatch()` who elects to pay the relayer fee in native token is exposed to sandwich extraction of the ETH they attach beyond the minimal fair-market swap cost. Because dispatch is the core, unauthenticated message-dispatch entry point of the protocol (used broadly across apps, e.g. via `HyperFungibleToken`/`TokenGateway` when a caller opts to pay in native token), this is a systemic, repeatable value-extraction vector rather than an isolated edge case, and can be triggered on every dispatch call funded with native ETH.

### Likelihood Explanation
High. `dispatch()` is a permissionless, frequently-invoked function; sandwiching is a well-understood, automatable MEV strategy against any transaction performing an unprotected spot-priced swap, and the swap parameters here (`sqrtPriceLimitX96: 0`, `amountInMaximum = msg.value`) impose no independent defense beyond what the user already pre-committed as their total budget.

### Recommendation
Do not rely purely on the live AMM spot price for a state-changing entry point that any address can trigger. Either:
- Require callers to supply an explicit `amountInMax`/slippage-bounded quote separate from `msg.value`, refunding any excess to the original payer (not to the host), and reverting if the executed price deviates materially from a recent quote/oracle price; or
- Compare the router's spot price against a TWAP/oracle price before executing the swap and revert (or clamp) if the deviation exceeds a configurable threshold, consistent with the remediation Connext applied for the analogous `SponsorVault` issue (PR 1595).

### Proof of Concept
1. Attacker monitors the mempool for `EvmHost.dispatch()` calls carrying `msg.value > 0` (native-fee payment path).
2. Attacker front-runs with a large ETH→feeToken (or feeToken→ETH) swap on the pool at `_hostParams.uniswapV2`, moving the spot price so that acquiring `post.fee` feeToken units now costs close to the victim's full `msg.value`.
3. Victim's `dispatch()` executes `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` (or the wrapper's `exactOutputSingle` with `amountInMaximum: msg.value`, `sqrtPriceLimitX96: 0`); it succeeds because the manipulated price is still within `msg.value`, consuming far more ETH than fair value for the same `post.fee` output.
4. Attacker back-runs to reverse the initial swap, realizing a profit equal to the price impact extracted from the victim's over-attached ETH — with no on-chain check ever comparing the executed price to a fair reference price.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L125-133)
```text
        IV3SwapRouter.ExactOutputSingleParams memory params = IV3SwapRouter.ExactOutputSingleParams({
            tokenIn: weth,
            tokenOut: path[1],
            fee: _params.maxFee,
            recipient: recipient,
            amountOut: amountOut,
            amountInMaximum: msg.value,
            sqrtPriceLimitX96: 0
        });
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
