### Title
Native-fee dispatch swaps in `EvmHost.dispatch` overpay/trap excess ETH with no slippage bound, front-runnable via the local Uniswap V2 pool - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept an arbitrary `msg.value` and forward it in full to `swapETHForExactTokens{value: msg.value}(post.fee, ...)` with no check that the amount consumed matches an amount the caller bounded, and any unspent ETH the router refunds lands on the `Host` contract itself rather than being returned to the dispatching caller.

### Finding Description
`dispatch(DispatchPost)` and `dispatch(DispatchGet)` are the primary entry points any app or user reaches to send a cross-chain message and pay for it in native token: [1](#0-0) [2](#0-1) 

Both functions pass `msg.value` wholesale into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee/get.fee, path, address(this), block.timestamp)`. In `swapETHForExactTokens`, `msg.value` acts as the router's `amountInMax`, and the router refunds any leftover ETH to its immediate caller — here, that is `EvmHost` itself (`address(this)`), not the original `_msgSender()` who supplied the value. There is no code after the swap call in either `dispatch` overload that captures or forwards this refund back to the caller.

This differs materially from the pattern used elsewhere in the same codebase for exactly this kind of swap. `IntentGatewayV2`'s fee-swap logic captures the router's returned `amounts[0]` (actual ETH spent) and refunds the caller-tracked remainder at the end of the transaction: [3](#0-2) [4](#0-3) 

`EvmHost.dispatch` has no equivalent tracking or refund step, and no `receive()`/withdraw path was found for recovering stray ETH from the Host — it is a governance-controlled core contract with no user-facing sweep function for accidental native transfers.

The project's own documentation flags the underlying pricing primitive (`quote()`, which also calls the router's `getAmountsIn`) as sandwich-vulnerable and explicitly warns against using it on-chain: [5](#0-4) 

Any caller who follows the documented off-chain "quote-then-dispatch" flow, or who pads `msg.value` for safety margin against gas-price/AMM movement between quoting and submission, will have the excess ETH consumed by the swap call's `amountInMax` semantics only up to what the pool needs at execution time — but that "up to" is computed against whatever price the pool is at when the dispatch transaction lands, which can be pushed unfavorably by a front-runner trading against the WETH/feeToken pair immediately beforehand, and any ETH not spent by the swap is silently retained by the `Host` contract instead of returning to the caller.

### Impact Explanation
This is a direct, on-chain-reachable path to unbacked loss of native token for any single caller (app or EOA) dispatching a POST/GET request and paying with native token, which is the standard path documented for HyperApp/HyperFungibleToken and any custom `IApp` integrator:
- Amounts sent in are unbounded (the docs literally advise sending enough native token to "cover fees" with headroom, and any app that adds a safety buffer or that quotes off-chain and the market moves favorably between quote and execution) — none of that excess is returned.
- The excess is not merely refunded to a wrong address recoverable later; it accumulates as native token stuck in `EvmHost` with no code path to reclaim it for the depositor, constituting a permanent loss of funds for the depositor — matching the "permanent freezing of funds" acceptance criterion.
- Because the swap price is set by the live Uniswap V2 reserves at execution time, a relayer/front-runner watching the mempool can manipulate the WETH/feeToken price just before the victim's `dispatch` call lands (classic sandwich), maximizing the ETH consumed by the fixed-output swap and/or minimizing the leftover refunded to `Host` versus what would have been fair — the caller has no way to bound the maximum native amount actually spent beyond the imprecise, front-runnable off-chain quote.

### Likelihood Explanation
High likelihood: `dispatch(DispatchPost)`/`dispatch(DispatchGet)` are unrestricted, permissionless, externally callable by any single transaction from an app, relayer, or end user, and are the documented default way to pay dispatch fees in native token across HyperApp, HyperFungibleToken, WrappedHyperFungibleToken, and any third-party `IApp`. Every native-fee dispatch is exposed to this pattern; no special conditions or privileged roles are required to trigger the loss — only sending `msg.value` that doesn't exactly match the post-swap consumption, which is the normal, encouraged (buffered) usage pattern per the SDK/docs.

### Recommendation
- After the `swapETHForExactTokens` call, capture the router's returned `amounts[0]` (ETH actually spent) and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`/`get.payer`), mirroring the pattern already implemented in `IntentGatewayV2`/`ExtrinsicIntents`.
- Consider adding an explicit `deadline`/slippage parameter usable by the caller (already implicitly bounded by `msg.value`, but the refund-to-wrong-address bug should be fixed regardless), and add a protocol-level sweep/rescue function for stuck native balance as defense in depth.

### Proof of Concept
1. Alice calls `HyperApp` (or any `IApp`) which calls `EvmHost.dispatch{value: X}(post)` where `post.fee = F` (in feeToken units), sending `X` computed off-chain via `quote()` plus a safety buffer, or simply `X` slightly larger than needed because gas/exchange conditions shifted favorably since the last quote.
2. `EvmHost.dispatch` executes `swapETHForExactTokens{value: X}(F, [WETH, feeToken], address(this), block.timestamp)`.
3. The router consumes `amountIn <= X` ETH to produce exactly `F` feeToken, and refunds `X - amountIn` ETH to its caller, `EvmHost` (`msg.sender` inside the router call), per standard UniswapV2Router02 behavior.
4. `EvmHost.dispatch` does not read the router's return value and has no logic to forward the refunded ETH to Alice; the difference `X - amountIn` remains in `EvmHost`'s balance indefinitely, with no code path in `EvmHost.sol` to return it to Alice.
5. A relayer observing Alice's pending transaction can additionally front-run it with a swap against the same WETH/feeToken pool to shift `amountIn` upward (worsening Alice's rate) before Alice's dispatch executes, since there is no minimum-output/maximum-price bound the caller controls beyond a static `msg.value`. [1](#0-0)

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-390)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L203-217)
```text
        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
