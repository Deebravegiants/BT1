Based on my research, there is a valid analog in this codebase to the DODO M-12 issue — the same bug class (spot-AMM-priced swap executed atomically inside a state-changing protocol function, with no slippage/price-manipulation protection) is reachable by any unprivileged sender who dispatches a cross-chain message or places an intent order and pays with native token.

### Title
Native-token fee payments are priced off manipulable Uniswap V2 spot reserves inside `EvmHost.dispatch()`/`fundRequest()` and `IntentGatewayV2.placeOrder()`, letting an attacker sandwich the fee swap - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch()`, `EvmHost.dispatch()` (GET variant), `EvmHost.fundRequest()`, and `IntentGatewayV2.placeOrder()` all convert a user-supplied `msg.value` into `feeToken` by calling `IUniswapV2Router02.swapETHForExactTokens()` directly against the configured `uniswapV2` router, using live spot reserves with no price-deviation guard, oracle check, or slippage parameter beyond the caller's own `msg.value` ceiling.

### Finding Description
`EvmHost.dispatch(DispatchPost)` builds a `WETH -> feeToken` path and swaps native token for an *exact* amount of `feeToken` (`post.fee`) using whatever reserves the local Uniswap V2 pair currently holds: [1](#0-0) 

The identical pattern (unbounded input up to `msg.value`, output fixed by protocol logic, priced from the same pair) recurs in the GET dispatch path and in `fundRequest()`: [2](#0-1) [3](#0-2) 

And again in `IntentGatewayV2.placeOrder()` (Tron variant shown, same pattern used on EVM), where the order's fee escrow is funded the same way when the user pays with native token: [4](#0-3) 

`IDispatcher` documents this as intended behavior for every app built on top of `HyperApp`: [5](#0-4) 

The project's own docs independently flag that the *off-chain* `quote()` helper (which also calls `getAmountsIn`) is "vulnerable to sandwich attacks" and must not be used inside a smart-contract transaction: [6](#0-5) 

However, the on-chain code path in `EvmHost` itself performs the analogous operation — an atomic AMM swap priced from the pool's current reserves, with no external price reference, TWAP, or bounded-deviation check — exactly the root cause pattern described in the DODO report (`UniswapV2Library.getAmountsIn()`-derived pricing consumed without manipulation protection). The router call is atomic, so it is not the classic "quote now, swap later" staleness bug, but it is fully exposed to same-block sandwich manipulation of the pair's reserves: an attacker can flash-loan-skew the `WETH/feeToken` pair immediately before the victim's `dispatch`/`fundRequest`/`placeOrder` transaction, then reverse the skew immediately after, extracting the difference between the fair price and the manipulated price that the Host pays out of the victim's `msg.value`.

### Impact Explanation
Any user who dispatches a cross-chain POST/GET request, funds an in-flight request, or places an IntentGateway order using native token as payment is exposed. An attacker who controls (or thinly-liquidity-manipulates) the local `uniswapV2` pair configured in `HostParams.uniswapV2` can:
1. Front-run the victim's `dispatch`/`fundRequest`/`placeOrder` call to skew the pair's reserves, inflating the ETH cost of the fixed `feeToken` output.
2. Let the victim's transaction execute at the skewed price, extracting value from the victim's `msg.value` beyond what the fair-price swap should cost (the classic sandwich profit), or
3. Cause the transaction to revert entirely if the skewed price now requires more ETH than the victim supplied — a denial-of-service on message dispatch (a route unable to deliver messages until the user resubmits with a larger, unpredictable buffer).

This directly affects fee accounting/value transfer on the core dispatch path used by every Hyperbridge app (`HyperApp`-based apps, `IntentGatewayV2`), not a peripheral or off-chain-only surface.

### Likelihood Explanation
Exploitability depends on the depth/manipulability of the specific chain's configured Uniswap V2 `WETH/feeToken` pair (set in `HostParams.uniswapV2` and updatable only by governance/`hostManager`). On chains where this pair is thin or attacker-influenced (e.g., newly deployed chains, chains with custom fee tokens), a single flash-loan-funded front-run transaction is sufficient — no privileged access is required, matching the "unprivileged message dispatcher" reachability requirement.

### Recommendation
Do not perform an unbounded atomic AMM swap priced purely from spot reserves inside `dispatch()`/`fundRequest()`/`placeOrder()`. Options: (1) require callers to pre-quote off-chain and pass an explicit `amountInMax`/slippage bound that is validated against a TWAP or bounded-deviation oracle rather than trusting the router's live spot quote unconditionally; (2) cap the acceptable price deviation between the swap execution price and a reference/TWAP price, reverting rather than executing at a manipulated price; (3) prefer fee-token-denominated payment (`dispatchWithFeeToken`) as the default and treat native-token payment as an explicitly higher-risk, rate-limited path.

### Proof of Concept
1. Attacker identifies the `uniswapV2` router/pair configured in `EvmHost.hostParams().uniswapV2` for a target chain, paired against that chain's `feeToken`.
2. Attacker flash-loans the pair's tokens and swaps to skew reserves immediately before a pending `dispatch{value: msg.value}(post)` / `fundRequest{value: msg.value}` / `placeOrder` transaction is mined.
3. The victim transaction executes `swapETHForExactTokens(post.fee, [WETH, feeToken], address(this), block.timestamp)` at the skewed price — either consuming more of the victim's ETH than the fair price would require (profit siphoned to the attacker via the reversed arbitrage trade) or reverting outright if `msg.value` is insufficient at the new price.
4. Attacker reverses the flash-loan skew in the same block, pocketing the price-impact profit extracted from the victim's ETH.

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

**File:** evm/src/core/EvmHost.sol (L1031-1040)
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-485)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }
```

**File:** sdk/packages/core/contracts/interfaces/IDispatcher.sol (L118-131)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the IHost.feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the IHost.feeToken.
     *
     * @param request - post request
     * @return commitment - the request commitment
     */
    function dispatch(DispatchPost memory request) external payable returns (bytes32 commitment);
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
