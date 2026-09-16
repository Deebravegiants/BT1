### Title
Excess native-token payment to `EvmHost.dispatch()` (and `fundRequest()`) is permanently stuck when the configured Uniswap V2-compatible router refunds change to `msg.sender` instead of the original caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept `msg.value` and forward the entire amount to a configured `_hostParams.uniswapV2` router via `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, exactly mirroring the pattern in the external report where a user's excess ETH is forwarded to a downstream contract that has no mechanism to return the unused remainder to the original caller. [1](#0-0) 

### Finding Description
`dispatch(DispatchPost)` swaps the entire `msg.value` for exactly `post.fee` of the fee token, but never captures or refunds any leftover ETH to `_msgSender()`: [1](#0-0) 
The same pattern repeats in `dispatch(DispatchGet)` and `fundRequest()`: [2](#0-1) [3](#0-2) 

Whether excess ETH actually gets stuck depends on where the swap router's refund lands. The codebase supports multiple router implementations behind the `IUniswapV2Router02` interface used by `_hostParams.uniswapV2`, including `UniV3UniswapV2Wrapper`. In that wrapper, `swapETHForExactTokens` explicitly refunds unspent ETH to `msg.sender`: [4](#0-3) 
Because `EvmHost.dispatch()` is the one calling `swapETHForExactTokens`, `msg.sender` as seen by the wrapper is `EvmHost` itself — not the original transaction sender/app that called `dispatch()`. The refund therefore lands in the `EvmHost` contract's own ETH balance rather than being returned to the caller. `EvmHost.dispatch()`/`fundRequest()` never read or forward this refund back to `_msgSender()`, so the excess ETH accumulates in `EvmHost` with no user-facing function to reclaim it. This is functionally identical to the reported bug class: a user sends more native value than is actually consumed by the operation, the excess is forwarded through to another contract during processing, and there is no withdrawal path back to the payer.

Individual apps built on top of `EvmHost.dispatch()` (e.g. `IntentGatewayV2`, `ExtrinsicIntents`, `IntrinsicIntents`, `HyperFungibleTokenUpgradeable`) have all been hardened to compute the exact required `msgValue` and refund any leftover to `msg.sender` themselves *before* calling `IDispatcher(host).dispatch{value: msgValue}(...)` — this is demonstrated extensively in tests such as `testPlaceOrder_RefundsExcessNativeToken` and `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`: [5](#0-4) [6](#0-5) 

However, this app-level mitigation only works if the app perfectly predicts the exact fee amount `EvmHost` will consume from the swap. If the app supplies exactly `post.fee`-worth-plus-slippage-buffer of ETH (as is unavoidable when the exact on-chain swap output/slippage isn't known precisely in advance, or when a caller directly integrates with `IDispatcher.dispatch()` per the documented "Native Token Payment" pattern), any residual ETH from the swap is retained inside `EvmHost` rather than returned to the caller: [7](#0-6) 

There is no `withdraw`/`sweep`/`rescue` function in `EvmHost.sol` to recover this trapped native balance; my search for such functions in the file only matched the fee-related refund lines already cited, confirming there is no user- or admin-level mechanism to reclaim ETH that accumulates in the Host this way.

### Impact Explanation
Any unprivileged caller — directly integrating apps, relayers paying for `fundRequest`, or end users paying dispatch fees via the documented native-token path — who supplies ETH via `EvmHost.dispatch()`/`fundRequest()` with a router configuration whose refund semantics return leftover ETH to `msg.sender` (the Host) rather than the original payer permanently loses that excess ETH into the Host contract's balance. Given no admin sweep exists in `EvmHost.sol`, the funds are permanently frozen inside the protocol's core contract. This is a direct violation of "permanent freezing of funds" for any of the many ETH-denominated dispatch fee payment paths across the entire Hyperbridge EVM messaging surface (POST, GET, fundRequest), which is the most commonly reachable single-transaction pathway in the protocol.

### Likelihood Explanation
This can be triggered by any single unprivileged transaction that pays native-token dispatch fees with even a modest safety buffer over the exact quoted amount — a routine and expected practice given AMM slippage/quote staleness, as explicitly warned about in the docs ("Apply a generous 2x buffer to absorb the legacy deployed host's per-byte protocol fee"), which is exactly this scenario for `HyperbridgeLzEndpoint`'s `quote()`: [8](#0-7) 
Likelihood is Medium-High: it does not require any special conditions beyond configuring/using a router (such as `UniV3UniswapV2Wrapper`) whose interface refunds to `msg.sender`, which is a supported, in-scope deployment configuration for `_hostParams.uniswapV2`.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the ETH balance before and after the router call and refund any residual amount to `_msgSender()` (not just rely on the router refunding to the correct party), e.g.:
```solidity
uint256 balBefore = address(this).balance - msg.value;
IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp);
uint256 leftover = address(this).balance - balBefore;
if (leftover > 0) {
    (bool sent,) = _msgSender().call{value: leftover}("");
    require(sent);
}
```
Alternatively, standardize the `IUniswapV2Router02`-compatible interface contract so that all supported router/wrapper implementations refund unspent ETH to the *original transaction sender* passed explicitly as a parameter, rather than relying on ambiguous `msg.sender` semantics that differ between real Uniswap V2 routers and wrapper wrapper contracts like `UniV3UniswapV2Wrapper`.

### Proof of Concept
1. Configure `_hostParams.uniswapV2` to point at `UniV3UniswapV2Wrapper` (a supported, in-repo router implementation).
2. Caller (app or user) calls `EvmHost.dispatch(DispatchPost)` with `msg.value` set intentionally higher than the exact ETH needed to acquire `post.fee` of the fee token (a normal buffer for slippage).
3. Inside `dispatch()`, `EvmHost` calls `UniV3UniswapV2Wrapper.swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. [1](#0-0) 
4. Inside the wrapper, unspent ETH (`msg.value - spent`) is refunded via `msg.sender.call{value: refund}("")`, where `msg.sender` is `EvmHost`: [9](#0-8) 
5. `EvmHost.dispatch()` returns without forwarding this refunded ETH anywhere; it now sits in `EvmHost`'s own balance.
6. The original caller has overpaid and has no function on `EvmHost` to reclaim the difference — the ETH is permanently stuck in the `EvmHost` contract.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L140-149)
```text
        bytes[] memory results = IMulticallExtended(_params.swapRouter).multicall(deadline, data);
        uint256 spent = abi.decode(results[0], (uint256));

        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3752)
```text
    /// @notice placeOrder with fee swap refunds unused ETH after swapETHForExactTokens.
    function testPlaceOrder_FeeSwap_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 feeAmount = 1 * 1e18; // 1 DAI worth of fees

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: feeAmount,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userEthBefore = user.balance;

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        // Send 5 ETH for a fee swap that should cost much less
        intentGateway.placeOrder{value: 5 ether}(order, bytes32(0));
        vm.stopPrank();

        // User should get back most of the 5 ETH — the swap only needed a tiny fraction
        uint256 ethSpent = userEthBefore - user.balance;
        assertTrue(ethSpent < 1 ether, "User should have been refunded most of the 5 ETH");
        assertTrue(ethSpent > 0, "User should have spent some ETH on the fee swap");
    }
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-188)
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
            payer: msg.sender
        });
        
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(post);
    }
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
