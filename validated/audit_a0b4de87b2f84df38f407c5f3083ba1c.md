I have enough to build the analog now. The relevant path is `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, all callable by any unprivileged HyperApp/caller, which route native-token payment through an on-chain Uniswap V2 swap with no belief-price/oracle bound and no caller-supplied `amountInMax`/slippage cap — the caller's entire `msg.value` acts as the implicit slippage tolerance.

### Title
Unbounded native-to-feeToken swap in `EvmHost.dispatch`/`fundRequest` enables sandwich extraction of dispatcher's native payment - ([File: evm/src/core/EvmHost.sol])

### Summary
Any unprivileged caller dispatching a message with native-token payment (`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest`) triggers an on-chain `swapETHForExactTokens` against the configured Uniswap V2 pool to acquire the exact `fee`/`amount` of `feeToken`, funded by `msg.value` [1](#0-0) . There is no belief price, oracle bound, or slippage parameter set by the protocol — the only bound on the swap's execution price is whatever headroom the caller happened to include in `msg.value` above the exact fee needed.

### Finding Description
`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` each perform:
```solidity
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
``` [1](#0-0) [2](#0-1) [3](#0-2) 

This is functionally the same permissionless-swap pattern as the Anchor collector's `sweep`: any transaction can trigger an unauthenticated AMM trade with no `belief_price`/oracle check and no explicit max-slippage guard from the protocol side. The docs acknowledge this exact class of risk for the companion `quote()` view function ("uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks... Only use it off-chain") [4](#0-3) , but the on-chain execution path in `dispatch`/`fundRequest` carries the same sandwich exposure without any mitigation — the fee-token deadline is `block.timestamp` (no real deadline enforcement) and the swap's implicit slippage bound is just "whatever ETH the caller sent minus the exact fee."

An attacker can:
1. Observe a pending `dispatch{value: ...}` / `fundRequest{value: ...}` transaction in the mempool.
2. Front-run it with a trade that moves the WETH/feeToken pool price against the victim.
3. Let the victim's `swapETHForExactTokens` execute, consuming more ETH than fair value (up to the full `msg.value` supplied) to obtain the fixed `feeToken` output.
4. Back-run to restore the price and capture the ETH surplus extracted from the victim's transaction.

Because callers typically pad `msg.value` above the exact estimated fee (the docs explicitly warn fee estimation via `quote()` is "Approximate (subject to slippage)" [5](#0-4) ), that padding is exactly the value an attacker can siphon via sandwiching, with any un-consumed ETH refunded to the dispatcher by the router but priced at a manipulated rate.

### Impact Explanation
Every native-token dispatch or fee-top-up transaction on any EVM chain running `EvmHost` is exposed to value extraction proportional to the ETH the caller sends beyond the exact required fee. Since native payment is documented as the primary "user convenience" path for one-off/user-facing dispatches [5](#0-4) , this is a broadly reachable, protocol-level MEV leak that degrades the economics of every unsigned/self-relay-friendly integration using native fee payment, and could be repeatedly exploited against high-volume dispatchers to drain padding funds continuously (not a one-off, since it is unauthenticated and reachable from any transaction).

### Likelihood Explanation
High reachability: no privilege is required, the swap fires on the hot path of the most basic Hyperbridge primitive (`dispatch`), and the vulnerable pools (Uniswap V2 WETH/feeToken) are public and observable in the mempool, making standard sandwich bots directly applicable. Likelihood is bounded only by pool liquidity/gas economics versus the padding amount, same caveat noted by the original Anchor triage ("impact seems reduced" for thin/dust amounts) — but any dispatcher choosing conservative padding to avoid reverts increases attacker profit.

### Recommendation
Do not rely on an unbounded/implicit slippage bound derived purely from `msg.value`. Either:
- Require callers to explicitly pass a `deadline` and `amountInMax` (rather than defaulting to `msg.value` and `block.timestamp`), and validate against a governance-configured maximum acceptable price deviation from an oracle (e.g., Chainlink native/feeToken price, mirroring the pattern already used in `SimplexPaymaster.swapAndDeposit`'s oracle-derived `amountOutMin` with `swapSlippageBps` [6](#0-5) ), or
- Discourage/deprecate native-token payment for `dispatch`/`fundRequest` in favor of `feeToken`-denominated payment, which the docs already recommend for slippage-sensitive cases [5](#0-4) .

### Proof of Concept
1. Attacker monitors mempool for `EvmHost.dispatch{value: V}(post)` where `V` includes padding above the exact fee `post.fee`.
2. Attacker front-runs with a large WETH→feeToken swap on the same Uniswap V2 pool, moving the price so that acquiring `post.fee` feeToken now costs materially more ETH.
3. Victim's `swapETHForExactTokens{value: V}(post.fee, path, address(this), block.timestamp)` executes at the manipulated price, consuming a larger portion of `V` (up to all of it, reverting only if `V` is now insufficient) [1](#0-0) .
4. Attacker back-runs, selling feeToken back for WETH, capturing the price impact as profit — funded by the ETH the victim's dispatch transaction just paid into the pool.

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

**File:** evm/src/core/EvmHost.sol (L974-982)
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
```

**File:** evm/src/core/EvmHost.sol (L1031-1039)
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
```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L509-510)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L240-249)
```text
### Payment Method Comparison

| Feature | Native Token | FeeToken (Recommended) |
|---------|-------------|------------------------|
| **Gas Cost** | Higher (includes swap) | Lower (no swap) |
| **Slippage** | Yes (Uniswap swap) | No |
| **Fee Calculation** | Approximate (subject to slippage) | Exact |
| **Token Approval** | Not required | Required  |
| **User Convenience** | High (users have native tokens) | Low (users need feeToken) |
| **Best For** | One-off transactions, user-facing apps | Frequent dispatches, cost optimization |
```

**File:** evm/src/utils/SimplexPaymaster.sol (L454-468)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

```
