### Title
Native funds are lost on Gnosis because `GnosisUniswapV2Interface.swapETHForExactTokens()` sweeps the entire `msg.value` instead of only the required fee - ([File: evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` allow callers to pay the dispatch fee in native token by forwarding `msg.value` to the configured `uniswapV2` router's `swapETHForExactTokens(fee, path, address(this), block.timestamp)` call [1](#0-0) . On chains that use a standard `IUniswapV2Router02`, this function only consumes up to `fee` worth of ETH and refunds any unused `msg.value` back to the caller. On Gnosis, however, the router address is configured to point at `GnosisUniswapV2Interface`, a custom, non-standard implementation deployed via `DeployGnosisWrapper.s.sol` [2](#0-1) .

### Finding Description
`GnosisUniswapV2Interface.swapETHForExactTokens()` only checks that `amountOut <= msg.value`, then wraps and forwards the **entire** `msg.value` (not just `amountOut`/fee) as WXDAI to the caller:

```solidity
function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
    external payable returns (uint256[] memory)
{
    if (amountOut > msg.value) revert MsgValueLessThanExactAmount();
    (bool sent,) = WETH().call{value: msg.value}("");
    if (!sent) revert DepositFailed();
    IERC20(WETH()).safeTransfer(msg.sender, msg.value);
    ...
}
``` [3](#0-2) 

There is no synchronization or reconciliation between the value actually required (`post.fee` / `get.fee`) and `msg.value` supplied by the dispatching contract/user in `EvmHost.dispatch()`:

```solidity
if (msg.value > 0) {
    ...
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) [4](#0-3) 

Unlike a real Uniswap V2 router (which refunds `msg.value - amountUsed` to the caller), the Gnosis wrapper unconditionally consumes and converts the whole `msg.value`, regardless of how small `post.fee`/`get.fee` is. Any excess native token the caller supplied above the actual required fee is silently converted into WXDAI and credited to `EvmHost` itself rather than refunded to the payer (`_msgSender()`/`post.payer`). This is functionally the same root cause described in the reference report: the amount actually charged (`msg.value`) is not checked/synchronized against the intended "volume" (`post.fee`), and any caller mistake or minor overestimation when quoting/paying the fee (e.g. via `quote()`/SDK helpers as documented for `HyperApp.dispatch{value: nativeFee}`) results in permanent loss of the excess native funds.

### Impact Explanation
Any application or end-user dispatching a POST/GET request with native-token fee payment on Gnosis will lose 100% of any `msg.value` sent beyond the actual `post.fee`/`get.fee`. Because slight overestimation is a normal occurrence (fee quoting via `quote()` is time-sensitive and AMM price can shift between quote and execution, or callers pad the value for safety), this is a realistic path for continual loss of native (xDAI) funds for any Gnosis-chain user of `HyperApp`/`IDispatcher.dispatch()` paying with native tokens. This satisfies the Medium bar: concrete freezing/loss of user funds reachable from a single dispatched request.

### Likelihood Explanation
High likelihood on Gnosis deployments: every native-fee-paying dispatch call is affected, not just an edge case. The documentation explicitly instructs users to pay fees via `msg.value` for POST/GET requests [5](#0-4) , and any deviation between the quoted amount and the value actually sent (which is common) triggers the loss deterministically, with no way to recover the swept excess.

### Recommendation
Modify `GnosisUniswapV2Interface.swapETHForExactTokens()` to only wrap/consume `amountOut` and refund the remainder (`msg.value - amountOut`) back to `msg.sender`, matching standard `IUniswapV2Router02` semantics:
```solidity
function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
    external payable returns (uint256[] memory)
{
    if (amountOut > msg.value) revert MsgValueLessThanExactAmount();
    (bool sent,) = WETH().call{value: amountOut}("");
    if (!sent) revert DepositFailed();
    IERC20(WETH()).safeTransfer(msg.sender, amountOut);
    if (msg.value > amountOut) {
        (bool refunded,) = msg.sender.call{value: msg.value - amountOut}("");
        if (!refunded) revert WithdrawFailed();
    }
    ...
}
```
Additionally, `EvmHost.dispatch()` should forward any leftover native balance it receives back to `_msgSender()`/`post.payer` after the swap, so excess native payment is never trapped in the host contract regardless of which router implementation is configured.

### Proof of Concept
1. On Gnosis, `EvmHost.hostParams().uniswapV2` is set to `GnosisUniswapV2Interface` per `DeployGnosisWrapper.s.sol` [6](#0-5) .
2. A user calls `dispatch(DispatchPost)` with `post.fee = 1e18` (1 fee token) but sends `msg.value = 2 ether` (e.g. due to price movement between quoting and executing, or intentional buffer).
3. `EvmHost.dispatch()` forwards the full `msg.value` (2 ether) to `swapETHForExactTokens{value: 2 ether}(1e18, path, address(this), ...)` [1](#0-0) .
4. Inside `GnosisUniswapV2Interface.swapETHForExactTokens`, the check `amountOut > msg.value` passes (1e18 < 2 ether), then the **entire** 2 ether is wrapped to WXDAI and transferred to `msg.sender` (`EvmHost`) [7](#0-6) .
5. The user only needed to pay the equivalent of `1e18` fee tokens but has permanently lost the extra ~1 ether worth of native funds, with `EvmHost` retaining the surplus WXDAI with no refund path back to the payer.

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

**File:** evm/script/DeployGnosisWrapper.s.sol (L10-23)
```text
contract DeployScript is BaseScript {
    using strings for *;

    /// @notice Main deployment logic - called by BaseScript's run() functions
    /// @dev This function is called within a broadcast context
    function deploy() internal override {
        // The Gnosis wrapper is wrap-only: the native gas token (xDAI) is already a
        // dollar stable, so it just wraps xDAI -> WXDAI. No router/quoter/fee config needed.
        GnosisUniswapV2Interface wrapper = new GnosisUniswapV2Interface{salt: salt}();
        vm.stopBroadcast();
        console.log("GnosisUniswapV2Interface deployed at:", address(wrapper));
        // Persist the deployed wrapper address into the UNISWAP_V2 config field.
        config.set("UNISWAP_V2", address(wrapper));
    }
```

**File:** evm/src/utils/uniswapv2/GnosisUniswapV2Wrapper.sol (L39-54)
```text
    function swapETHForExactTokens(uint256 amountOut, address[] calldata, address, uint256)
        external
        payable
        returns (uint256[] memory)
    {
        if (amountOut > msg.value) revert MsgValueLessThanExactAmount();

        (bool sent,) = WETH().call{value: msg.value}("");
        if (!sent) revert DepositFailed();

        IERC20(WETH()).safeTransfer(msg.sender, msg.value);

        uint256[] memory out = new uint256[](1);
        out[0] = msg.value;
        return out;
    }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-180)
```text
### Native Token Payment

For native token payments, dispatch directly and let the Host handle the Uniswap swap:

```solidity lineNumbers title="MyApp.sol"
contract MyApp is HyperApp {
    function sendMessageWithNative(
        bytes memory message,
        bytes memory dest,
        uint64 timeout,
        address to,
        uint256 relayerFee
    ) public payable returns (bytes32) {
        DispatchPost memory post = DispatchPost({
            body: message,
            dest: dest,
            timeout: timeout,
            to: abi.encode(to),
            fee: relayerFee,
```
