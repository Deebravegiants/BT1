### Title
Unrefunded ETH overpayment permanently locked in `EvmHost` on `dispatch()`/`fundRequest()` native-token fee swaps - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token (`msg.value`) as payment for relayer fees and swap it for the `feeToken` via `swapETHForExactTokens` on the configured Uniswap V2 router. None of these functions verify that `msg.value` is spent exactly, nor do they forward any residual ETH back to the original caller, so any overpayment sent above what the swap consumes is stranded in the `EvmHost` contract forever.

### Finding Description
In `EvmHost.sol`, all three ETH-accepting entrypoints follow the same pattern: [1](#0-0) 

```
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } ...
```

The same pattern repeats for `dispatch(DispatchGet)` [2](#0-1)  and for `fundRequest` [3](#0-2) .

The canonical Uniswap V2 Router's `swapETHForExactTokens(amountOut, path, to, deadline)` refunds any unspent ETH to `msg.sender` of that call — but `msg.sender` in this context is `EvmHost` itself (the router is called by the Host, not by the end user). This means:
1. If the caller sends more native token than needed to buy exactly `post.fee`/`get.fee`/`amount` worth of feeToken, the router refunds the excess ETH to `EvmHost`, not to the original transaction sender.
2. `EvmHost` never captures the `amounts` return value of `swapETHForExactTokens`, never computes any residual, and has no `receive()`/withdrawal path for stray native ETH balance visible in the contract (the only withdrawal path via `IHostManager` is for `feeToken` protocol revenue, not native ETH) [4](#0-3) .
3. There is no `require(msg.value == quotedAmount)` or equivalent check anywhere in these functions, and no refund-forwarding logic, unlike the pattern correctly implemented elsewhere in the codebase.

This is precisely the analog of the reported `buyNFT`/`buyMultipleNFT` bug class: no verification that the payed native amount matches the expected cost, causing the surplus to become permanently stuck with no redemption mechanism.

Contrast this with the codebase's own correct pattern in `evm/src/apps/IntentGatewayV2.sol`, which explicitly tracks and refunds unspent native token after the same kind of swap: [5](#0-4) 

```
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
msgValue -= amounts[0];
...
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
```

`EvmHost.dispatch`/`fundRequest` omit this refund step entirely.

### Impact Explanation
Any caller (end user, `HyperApp`-derived contract, `IntentGatewayV2`, `HyperFungibleToken`, etc.) that dispatches a POST/GET request or funds a request with native token and overestimates the required ETH (which is expected, since the docs explicitly warn that `quote()` is imprecise and vulnerable to sandwiching, and encourage generous overestimation from the frontend) will have the excess ETH permanently locked inside `EvmHost`. This affects every EVM deployment of Hyperbridge that accepts native-token fee payment — a core, frequently used code path (`dispatch`, the primary way apps submit cross-chain requests). Given the volume of dispatch calls across the protocol and the routine overestimation pattern recommended in the docs, this results in continuous, unrecoverable loss of user funds — a permanent freezing/loss-of-funds bug.

### Likelihood Explanation
High likelihood: dispatching with native token is a documented and encouraged usage pattern (`docs/content/developers/evm/messaging/post-requests.mdx`, `get-requests.mdx`), and the docs explicitly instruct developers to estimate fees off-chain via `quote()`, which is inherently imprecise and subject to price movement/slippage — meaning users will routinely send slightly more ETH than the router ultimately consumes. Every such overpayment is silently and irreversibly retained by `EvmHost`.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest`, capture the `amounts` array returned by `swapETHForExactTokens` and refund the difference between `msg.value` and `amounts[0]` back to `_msgSender()` (or `payer`), mirroring the pattern already used in `IntentGatewayV2.sol`:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
    post.fee, path, address(this), block.timestamp
);
uint256 refund = msg.value - amounts[0];
if (refund > 0) {
    (bool success, ) = _msgSender().call{value: refund}("");
    require(success, "refund failed");
}
```

### Proof of Concept
1. Deploy `EvmHost` with a configured `uniswapV2` router and `feeToken`.
2. Caller invokes `dispatch(DispatchPost{fee: 1e18, ...})` sending `msg.value = 5 ether` (a generous overestimate as encouraged by SDK/docs), analogous to the pattern shown in `evm/tests/foundry/EvmHostForkTest.sol` (`testCanDispatchPostRequestWithNative`) but with an inflated `msg.value` instead of the exact `quote()`-derived amount.
3. `swapETHForExactTokens{value: 5 ether}(1e18 feeToken, path, address(this), ...)` only spends the ETH needed to acquire exactly `1e18` feeToken (e.g., 0.01 ETH) and refunds the remaining ~4.99 ETH to `msg.sender`, which is `EvmHost`.
4. `EvmHost`'s ETH balance permanently increases by ~4.99 ETH with no function to withdraw or return it to the caller — confirmed by the absence of any native-ETH withdrawal path in `EvmHost.sol`/`HostManager.sol` (only feeToken revenue withdrawal exists via `IHostManager`).

### Citations

**File:** evm/src/core/EvmHost.sol (L68-80)
```text
/**
 * @title The Host Manager Interface. This provides methods for
 * modifying the host's params or withdrawing bridge revenue.
 *
 * @dev Can only be called used by the HostManager module.
 */
interface IHostManager {
    /**
     * @dev Updates IsmpHost params
     * @param params new IsmpHost params
     */
    function updateHostParams(HostParams memory params) external;

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

**File:** evm/src/apps/IntentGatewayV2.sol (L375-397)
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

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }

        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```
