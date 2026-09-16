### Title
Excess native fee paid to `EvmHost.dispatch()` is swept into the host contract instead of being refunded to the caller, permanently trapping overpaid ETH — ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch()` accepts native-token payment for the relayer fee and swaps `msg.value` for the exact fee amount via a Uniswap-V2-style router call made *by the host contract itself*. Any leftover ETH from that swap is refunded by the router to whoever is `msg.sender` of the swap call — which is `EvmHost`, not the original transaction sender or the intermediate application contract that forwarded the value. Overpaid native fees are therefore absorbed into the host contract's own balance rather than returned to the payer, mirroring the core defect in the referenced report: a refund address is computed/derived in a way that does not correspond to the actual party entitled to the refund, so value that should return to the caller is stranded.

### Finding Description
In `dispatch()`: [1](#0-0) 

the host performs:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
```
`swapETHForExactTokens`-style routers refund unspent native value to the caller of the swap function. Here the caller of the router is `EvmHost` (`address(this)` within `dispatch()`), because `EvmHost` is the contract making the external call and forwarding `msg.value`. Consequently, any ETH sent to `dispatch()` in excess of `post.fee`'s equivalent cost does not return to the account that originally called `dispatch()` — it returns to `EvmHost`'s own balance.

This is compounded by application contracts that intentionally overpay when quoting native fees. `HyperbridgeLzEndpoint.quote()` explicitly assumes the excess is refunded back to the caller: [2](#0-1) 

and `send()` forwards the full `msg.value` (computed with this 2x buffer) directly into `dispatch()`: [3](#0-2) 

Because the actual refund recipient is `EvmHost` and not `HyperbridgeLzEndpoint` (or the OApp/user who ultimately funded the transaction), the comment's assumption is false: the ~50% buffer on every native-paid `send()` is not returned to the caller, it is permanently absorbed by the host contract. The same exposure applies to any other integrating contract (`HyperFungibleToken.send()`, `WrappedHyperFungibleTokenUpgradeable.send()`, `ExtrinsicIntents`/`IntentGatewayV2` order fill/cancel flows) that forwards `msg.value` to `dispatch()` without computing the exact required native amount, since any surplus is likewise captured by `EvmHost` rather than refunded to the originating user.

No sweep/withdraw function for native ETH accumulated this way was found in `EvmHost.sol`, so the value is not merely temporarily misdirected but effectively locked in the contract absent a protocol upgrade or governance action to add a recovery path.

### Impact Explanation
Any user or application dispatching a POST/GET request through `EvmHost.dispatch()` (or a downstream app contract that forwards value into it) with native-token payment loses any ETH sent beyond the exact fee-swap requirement. This is directly analogous to the referenced Arbitrum gateway finding: value intended to be refunded to the party who supplied it is instead captured by an unintended address (there, the L2 alias of a contract; here, the host contract itself), and in the absence of a sweep mechanism this constitutes a permanent, protocol-wide loss of user funds on every native-fee dispatch that overpays — which, given quoting buffers like the LayerZero adapter's explicit 2x margin, is the common case rather than an edge case.

### Likelihood Explanation
High. Native-fee dispatch is a normal, unprivileged, single-transaction code path reachable by any user or integrating contract calling `dispatch()` with `msg.value`. The LayerZero endpoint adapter demonstrates that a deployed, in-scope integration relies on and systematically triggers this exact overpayment/no-refund condition on every native-paid message.

### Recommendation
In `EvmHost.dispatch()`, after performing the ETH→feeToken swap, explicitly refund any leftover native balance attributable to this call to `_msgSender()` (or to an explicit `payer`/`refundAddress` parameter on `DispatchPost`), rather than relying on the router to refund `address(this)`. Alternatively, compute the exact native amount required before invoking the router (avoiding any leftover), or add an owner-restricted sweep function paired with per-call refund-to-sender logic to guarantee overpaid value returns to its source.

### Proof of Concept
1. Any application (e.g. `HyperbridgeLzEndpoint.send()`) calls `IDispatcher(_host).dispatch{value: msg.value}(request)` where `msg.value` exceeds the ETH cost of `post.fee` feeTokens (as the LzEndpoint intentionally does, quoting a 2x buffer, see `sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol` lines 337-345 and 296-297).
2. Inside `EvmHost.dispatch()` (`evm/src/core/EvmHost.sol` lines 921-932), `swapETHForExactTokens{value: msg.value}(post.fee, ...)` is called with `EvmHost` as the router's `msg.sender`.
3. The router refunds `msg.value - amountIn` back to `msg.sender`, i.e., to `EvmHost`, not to the original caller of `send()`/`dispatch()`.
4. The excess ETH accumulates in `EvmHost`'s balance with no method found in `EvmHost.sol` to sweep it back to affected users, permanently locking the overpaid amount.

Note: I was unable to inspect the concrete wrapper implementations (`GnosisUniswapV2Wrapper.sol`, `UniV3UniswapV2Wrapper.sol`, `UniV4UniswapV2Wrapper.sol`) that implement `swapETHForExactTokens` for `_hostParams.uniswapV2`, since tool access ended before I could read them. Their exact refund-target logic could theoretically differ from stock Uniswap V2 behavior; confirming the precise refund recipient in those wrapper contracts would strengthen or narrow this finding, and I recommend a follow-up review of those three files to verify the refund destination before remediation.

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L287-297)
```text
        DispatchPost memory request = DispatchPost({
            dest: dest,
            to: abi.encodePacked(address(this)),
            body: body,
            timeout: 0,
            fee: relayerFee(_params.dstEid),
            payer: address(this)
        });

        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L337-345)
```text
        // Apply a generous 2x buffer to absorb the legacy deployed host's
        // per-byte protocol fee (the in-source host has no such markup). Excess
        // native is refunded by the uniswap router; excess feeToken approval is
        // simply unused.
        if (_params.payInLzToken) {
            return MessagingFee({nativeFee: 0, lzTokenFee: request.fee * 2});
        } else {
            return MessagingFee({nativeFee: quote(request) * 2, lzTokenFee: 0});
        }
```
