### Title
Overpaid native `msg.value` in `EvmHost.dispatch`/`fundRequest` is permanently stranded, unlike in `IntentGatewayV2` and `WrappedHyperFungibleToken` which correctly refund it - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native `msg.value` and swap it for the exact `feeToken` amount required (`post.fee`/`amount`) via the configured Uniswap-V2-style router, but never refund the unspent remainder to the caller. Any user or app that overestimates the required native fee and sends excess `msg.value` permanently loses the difference, which is the same bug class as the referenced `WRAP_CODE` report where `msg.value` exceeding `amountIn + executionPrice` is stranded on the router.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

the entire `msg.value` is forwarded to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. Real `UniswapV2Router02` (and this repo's own drop-in wrappers used on chains without a native V2 deployment, `UniV3UniswapV2Wrapper` and `UniV4UniswapV2Wrapper`) refund any unspent ETH to whoever called the swap function — in this case that caller is `EvmHost` itself (`address(this)` is the recipient of the swapped tokens, but the *refund* target inside the router/wrapper is `msg.sender` of the swap call, i.e. the `EvmHost` contract), not the original `_msgSender()` who supplied the native value: [2](#0-1) 

A test in the repo explicitly documents this refund-to-immediate-caller semantic: [3](#0-2) 

The identical pattern (no `require`, no diff-refund) repeats in `dispatch(DispatchGet)`: [4](#0-3) 

and in `fundRequest()`: [5](#0-4) 

By contrast, the codebase demonstrates the correct pattern elsewhere: `IntentGatewayV2._placeOrder` explicitly tracks `msgValue -= amounts[0]` after the swap and refunds the leftover to `msg.sender`: [6](#0-5) 

and `WrappedHyperFungibleToken.send`/`WrappedHyperFungibleTokenUpgradeable.send` deliberately size `msg.value` sent onward to the dispatcher precisely (`params.amount` wrapped, remainder forwarded as fee) rather than over-forwarding: [7](#0-6) 

`EvmHost.dispatch`/`fundRequest`, however, have no such accounting — the full `msg.value` is spent on the swap call with no tracking of `amounts[0]` actually consumed and no refund path for the remainder. Because `EvmHost` also has no `receive()`/native-withdrawal function (unlike the utility wrappers such as `GnosisUniswapV2Wrapper` which expose `receive() external payable {}` purely to accept WETH-unwrap proceeds mid-call), any native ETH refunded into `EvmHost`'s balance by the router/wrapper becomes permanently inaccessible — it is not tracked by any accounting variable and there is no owner/governance function to sweep stray native balance from `EvmHost`.

### Impact Explanation
`dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` are `external payable` and directly reachable by any unprivileged caller — an EOA, a relayer, or any `IApp` (including `WrappedHyperFungibleToken`, `HyperbridgeLzEndpoint`, or third-party integrators) that dispatches a cross-chain message and estimates the native fee slightly high (e.g., due to slippage buffering or price movement between quote and execution). Every such overpayment is permanently and irrecoverably locked in `EvmHost`, meeting the "permanent freezing of funds" bar for a valid finding.

### Likelihood Explanation
Any caller providing native `msg.value` for fee payment who adds even a small slippage/safety buffer above the tight quote (a very common integration pattern, matching the `nativeFee` buffering shown in the SDK docs example `IHyperFungibleToken(address(wrapper)).send{value: amount + nativeFee}(params)`), or any caller who round-trips a stale quote, will trigger fund loss on every such call. This is a routine operational condition, not an edge case, making likelihood high.

### Recommendation
Mirror the pattern already used in `IntentGatewayV2._placeOrder`: capture the actual amount spent (`amounts[0]`) returned by `swapETHForExactTokens`, compute the unspent remainder of `msg.value`, and refund it to `_msgSender()` (or the designated `payer`) at the end of `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`.

### Proof of Concept
1. A user calls `EvmHost.dispatch(DispatchPost{..., fee: 100 units of feeToken})` with `msg.value = 1 ether`, where only `0.4 ether` is actually needed to buy `100` units of `feeToken` via the configured router.
2. `swapETHForExactTokens{value: 1 ether}(100, path, address(this), deadline)` executes, spending `0.4 ether` and refunding the remaining `0.6 ether` back to `msg.sender` of that call, which is `EvmHost` itself.
3. `dispatch` returns normally, having granted the request commitment; the user has been correctly debited `1 ether` from their wallet but only `0.4 ether` worth of value went to fee payment.
4. The `0.6 ether` now sits in `EvmHost`'s native balance with no accounting entry crediting it to the user and no function in `EvmHost` or `HostManager` to withdraw stray native ETH — it is permanently lost to the user.

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

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L87-96)
```text
        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
        }
```

**File:** evm/tests/foundry/UniV4UniswapV2WrapperTest.sol (L82-108)
```text
    function testSwapETHForExactTokensV4() public {
        address[] memory path = new address[](2);
        path[0] = address(0);
        path[1] = DAI;

        uint256 amountOut = 1000 * 1e18;
        uint256 maxEthIn = 2 ether;

        vm.deal(WHALE, 100 ether);
        uint256 initialEthBalance = WHALE.balance;
        uint256 initialDeployerBalance = DEPLOYER.balance;

        uint256 deadline = block.timestamp + 1 hours;

        vm.prank(WHALE);
        uint256[] memory amounts = wrapper.swapETHForExactTokens{value: maxEthIn}(amountOut, path, WHALE, deadline);

        uint256 newEthBalance = WHALE.balance;
        uint256 newDeployerBalance = DEPLOYER.balance;

        console.log("Max ETH sent:", maxEthIn);
        console.log("ETH actually spent (returned):", amounts[0]);
        console.log("WHALE ETH spent:", initialEthBalance - newEthBalance);
        console.log("DAI received:", amounts[1]);

        assertEq(initialEthBalance - newEthBalance, amounts[0], "WHALE spent exactly the consumed amount");
        assertEq(newDeployerBalance, initialDeployerBalance, "Deployer received no refund (refund returns to caller)");
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-309)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```
