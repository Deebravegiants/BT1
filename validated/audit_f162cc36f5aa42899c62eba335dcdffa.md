### Title
Excess Native Token Overpayment in `EvmHost` Dispatch Functions Is Not Refunded to Callers - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native token payment via `msg.value` and forward the *entire* `msg.value` into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)` as an exact-output swap targeting only `post.fee` (or `amount`) worth of fee tokens.

### Finding Description
In all three functions, the full `msg.value` is passed to `swapETHForExactTokens`, but the swap only needs to acquire exactly `post.fee` (or `amount`) of `feeToken()`: [1](#0-0) [2](#0-1) [3](#0-2) 

Uniswap V2's `swapETHForExactTokens` refunds any unused ETH input to the `msg.sender` of that call — but since `EvmHost` itself is the caller of the router (it invokes the router with `{value: msg.value}`), the router's dust refund lands back in `EvmHost`'s own balance, not the original external caller who sent the overpayment (e.g., a `HyperApp`, `HyperFungibleToken`, `WrappedHyperFungibleToken`, or `IntentGatewayV2`/`ExtrinsicIntents` contract, or ultimately the end user). No code path in these three functions forwards that refunded dust back to `_msgSender()` or `post.payer`. No `withdraw`, `receive`, or sweep function was found in `EvmHost.sol` that would let a caller reclaim this stranded ETH.

This is architecturally analogous to the reported `MerkleReserveMinter.mintFromReserve` issue: a payable entry point accepts more native currency than is strictly required for the operation, and the surplus becomes permanently stuck in the contract with no refund mechanism to the original payer.

Multiple call sites across the app layer rely on the Host to handle exact-output native payment without doing their own pre-swap sizing, e.g. `WrappedHyperFungibleToken.send`, `HyperFungibleToken.send`, `HyperbridgeLzEndpoint.send`, and generic `HyperApp` sample dispatch flows all forward `{value: msg.value}` (or a computed remainder) straight to `dispatch()`: [4](#0-3) [5](#0-4) 

The documentation itself acknowledges users may over-provision native tokens ("2x buffer to absorb...per-byte protocol fee. Excess native is refunded by the uniswap router") relying on the incorrect assumption that the router's refund reaches the original caller: [6](#0-5) 

### Impact Explanation
Any caller (app contract or end user routed through an app) that sends more native token than strictly needed for the Uniswap swap to cover `post.fee`/`get.fee`/`amount` — which is expected practice per the docs' guidance to "estimate fees off-chain" with buffers, and is unavoidable given price movement between quote and execution — permanently loses the difference. The excess accumulates in `EvmHost` with no tracked accounting per-payer and no refund mechanism, i.e., a medium-severity fund-freezing bug reachable by any unprivileged sender who dispatches a message with native-token payment.

### Likelihood Explanation
High likelihood of occurrence in normal operation: the documented pattern for native-token dispatch explicitly instructs users/integrators to send a buffer of ETH above the estimated fee (to avoid reverts from price slippage in `getAmountsIn`), and any such buffer beyond the exact swap output is silently absorbed by the Host rather than returned.

### Recommendation
After calling `swapETHForExactTokens`, compute the unused ETH (e.g., via balance-before/after tracking) and refund it to `_msgSender()` (or an explicit `payer`/`refundTo` parameter) in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, mirroring the refund pattern already used elsewhere in the codebase (e.g., `IntentGatewayV2` / `ExtrinsicIntents` refund unspent `msgValue` back to `msg.sender`): [7](#0-6) 

### Proof of Concept
1. Caller invokes `IDispatcher(host).dispatch{value: X}(post)` where `post.fee = F` and current market price would only require `Y < X` ETH to buy `F` fee tokens (a buffer sent to guard against slippage, as recommended by the docs).
2. `EvmHost.dispatch` calls `swapETHForExactTokens{value: X}(F, path, address(this), block.timestamp)`.
3. The router uses only `Y` ETH for the swap and refunds `X - Y` ETH to its caller, which is `EvmHost` itself (since `EvmHost` invoked the router with `{value: X}`).
4. `EvmHost`'s native balance increases by `X - Y`; the original caller/payer never receives this back and it is not tracked against their address, matching the described "funds sent in excess... not refunded" bug class.

Note: I was unable to locate any Host-level `withdraw`/`receive` function in the indexed portion of `EvmHost.sol` that would let an admin or user later reclaim this stranded balance; if such a function exists elsewhere in the file outside indexed excerpts, it would only mitigate — not fix — the lack of a direct, trustless refund path to the original payer.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-273)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L296-306)
```text
        if (msg.value > 0) {
            IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
            // Fee tokens already transferred to this contract by OFT's _payLzToken.
            // The quoted lzTokenFee includes a buffer above the relayer fee so the
            // legacy deployed host's per-byte protocol fee can be paid out of it;
            // approve our full feeToken balance and let the host take what it needs.
            address feeToken = IDispatcher(_host).feeToken();
            IERC20(feeToken).forceApprove(_host, IERC20(feeToken).balanceOf(address(this)));
            IDispatcher(_host).dispatch(request);
        }
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L214-217)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
