### Title
Front-running/sandwich attack on `EvmHost` native-token fee swap causes user overpayment that is permanently trapped in the contract - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all convert native-token payment into the protocol `feeToken` via a live, on-chain `swapETHForExactTokens` call against the configured Uniswap V2 router at execution time, with no slippage bound and no refund path for any unused native token, exposing every unprivileged caller who pays fees in native token to a front-running/sandwich attack that permanently locks the excess ETH inside `EvmHost`.

### Finding Description
In `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, when `msg.value > 0` the contract performs: [1](#0-0) [2](#0-1) [3](#0-2) 

Each call site invokes `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(exactFeeAmount, path, address(this), block.timestamp)`. This is `_calculateSwapResultByAmountOut`-style logic analogous to the reported `SwapFunctions.sol` issue: the amount of native token actually consumed is determined by the *live* reserve ratio of the WETH/feeToken pool read at the moment the transaction executes, not at the moment the user signed/broadcast it.

Because `deadline` is hardcoded to `block.timestamp` (always satisfied) and there is no `amountInMax`/slippage check beyond the caller's own `msg.value`, an attacker observing a pending `dispatch`/`fundRequest` transaction in the mempool can front-run it with a swap that moves the WETH/feeToken pool price so that more ETH is required to buy the exact `post.fee` (or `amount`) of feeToken. Two exploitable outcomes follow:

1. If the victim supplied enough headroom in `msg.value` to survive the price shift, the router consumes more ETH than the fair-price cost and refunds whatever ETH is left over. Critically, that refund is sent to `msg.sender` of the router call, which is `EvmHost` itself (since `EvmHost` calls the router directly, not via delegatecall) — not to the original dispatcher/payer. `EvmHost` has no bookkeeping or sweep function that returns this leftover native balance to the payer; it becomes indistinguishable protocol-owned ETH.
2. If the price shift exceeds the caller's `msg.value` headroom, `swapETHForExactTokens` reverts, DoS-ing the dispatch until the caller resubmits with a larger `msg.value` (griefing every native-fee payer, and directly incentivized by the attacker's ability to extract value in case (1)).

Either way, any native ETH sent above the exact amount needed for the swap is unrecoverable by the original payer — there is no `receive`/refund flow tying leftover ETH in `EvmHost` back to `_msgSender()` in `dispatch()`, `dispatch(DispatchGet)`, or `fundRequest()`.

### Impact Explanation
This qualifies as **permanent freezing/loss of user funds**: any unprivileged user who dispatches a POST/GET request or funds an existing request using native token (the officially documented and SDK-supported payment path) can be sandwiched to overpay ETH, and that overpaid ETH is trapped inside `EvmHost` with no mechanism to reclaim it — it is absorbed as unaccounted protocol balance rather than refunded. The DoS variant additionally threatens the "route unable to deliver messages" bar, since a griefer can repeatedly force reverts on native-fee dispatches. Given this is reachable by a single submitted transaction from any user of `EvmHost.dispatch`/`fundRequest`, and the docs explicitly warn only about `quote()` being sandwich-prone for *off-chain estimation* — while the actual on-chain swap executed inside `dispatch()`/`fundRequest()` carries the same unprotected exposure — this is a High-severity issue matching the reported bug class (front-running of an unprotected on-chain price/amount calculation).

### Likelihood Explanation
High. `EvmHost.dispatch()` is the primary unprivileged entry point for dispatching ISMP messages, and native-token payment is a first-class, SDK/docs-endorsed flow — every dispatching transaction on any EVM chain with UniswapV2 fee-swap liquidity is exposed. Front-running/sandwiching public mempool transactions against known AMM pools is a standard, automated MEV strategy requiring no privileged access, matching the report's exact "attacker observes pending tx, submits a similar tx with better terms and higher gas" scenario.

### Recommendation
- Add an explicit `amountInMax` parameter (or compute one off-chain and pass it through `DispatchPost`/`DispatchGet`) so the swap can bound acceptable slippage instead of relying on `msg.value` as an implicit ceiling.
- Refund any leftover native token from the swap back to `_msgSender()` (or `post.payer`/`get.payer`) rather than leaving it credited to `address(this)`.
- Consider using `swapExactETHForTokens` with a caller-specified minimum output plus explicit refund logic, or moving the swap off-chain via a signed quote with a deadline that reflects real transaction validity windows rather than `block.timestamp`.

### Proof of Concept
1. Alice calls `EvmHost.dispatch(post)` with `msg.value = X`, expecting `swapETHForExactTokens` to consume `Y <= X` ETH for `post.fee` feeToken, retaining `X - Y` as slack for price movement.
2. Attacker observes Alice's pending transaction in the mempool and front-runs it with a large buy of `feeToken` against the same Uniswap V2 pool used by `EvmHost.uniswapV2`, shifting the WETH/feeToken price so that the ETH cost of `post.fee` feeToken rises to `Y' ` where `Y < Y' <= X`.
3. Alice's transaction still succeeds (since `Y' <= X`), but the router consumes `Y'` ETH instead of `Y`, and refunds `X - Y'` ETH to `EvmHost` (as `msg.sender` of the swap), not to Alice.
4. `EvmHost` has no logic crediting `X - Y'` back to Alice's account or any withdrawal path tied to her request; the value is permanently absorbed into the contract's balance.
5. The attacker profits from the sandwich (selling back the feeToken after Alice's transaction executes), while Alice permanently loses the ETH slack she provided as safety margin.

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
