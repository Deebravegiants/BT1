### Title
`EvmHost.dispatch`/`fundRequest` fail to refund unswapped excess native token to the caller, permanently trapping user funds - (File: `evm/src/core/EvmHost.sol`)

### Summary
When a user pays for a POST/GET dispatch or `fundRequest` with native ETH instead of the fee token, `EvmHost` forwards the *entire* `msg.value` into `swapETHForExactTokens`, requesting only the exact `fee`/`amount` of fee-token output. Any leftover native token that the router refunds after the swap is returned to the router's caller — `address(this)` (the `EvmHost` contract) — not to the original `_msgSender()`/`msg.sender` who overpaid. `EvmHost` never checks its own balance afterward and never forwards the difference back to the user, so overpaid ETH is permanently stuck in the host contract.

### Finding Description
In `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, the pattern is identical: [1](#0-0) 

```solidity
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
    ...
```

The same code shape repeats for `dispatch(DispatchGet)` [2](#0-1)  and for `fundRequest` [3](#0-2) .

The standard `UniswapV2Router02.swapETHForExactTokens` implementation refunds any unspent ETH (`msg.value - amounts[0]`) to `msg.sender` of that call — but the caller of the router here is `EvmHost` itself, not the end user. So the router's "automatic refund" lands back inside `EvmHost`'s own balance, and `EvmHost` has no subsequent logic that measures the delta and forwards it to `_msgSender()`. The comment in a related integration confirms the (incorrect) assumption baked into the design: "Excess native is refunded by the uniswap router" [4](#0-3)  — this is true only for the immediate router caller, which is `EvmHost`, not the transaction originator.

This is the exact bug class from the referenced report: a payable entrypoint accepts `msg.value`, performs a swap/consumption of only part of it, and never returns the unconsumed remainder to the paying user.

Notably, this exact defect was identified and fixed elsewhere in the same codebase: `IntentGatewayV2.placeOrder` explicitly computes `msgValue -= amounts[0]` after `swapETHForExactTokens` and then calls `_sendValue(msg.sender, msgValue)` to refund the caller [5](#0-4) , and is covered by dedicated tests (`testPlaceOrder_FeeSwap_RefundsExcessNativeToken`) [6](#0-5) . `EvmHost.sol`, which is the core dispatch/fee-payment surface reachable by every app and every user dispatching a cross-chain message, is missing this same fix.

### Impact Explanation
Any user or application calling `IDispatcher(host).dispatch{value: msg.value}(...)` for a POST or GET request, or calling `fundRequest{value: ...}`, with more native token than the exact fee-token cost of the swap will have the difference permanently trapped inside `EvmHost`. Given that documentation explicitly instructs integrators to send `msg.value` for native payment without exact-input guarantees (e.g. `IDispatcher(host()).dispatch{value: msg.value}(getRequest)` [7](#0-6) , and similarly for POST [8](#0-7) ), and `quote()` is explicitly a sandwich-vulnerable off-chain estimate, users are structurally likely to send more native token than the router ultimately consumes (due to price movement, slippage buffer, or imprecise off-chain estimation). This is a direct, unbacked loss of user funds with no recovery path — a concrete Medium/High severity issue.

### Likelihood Explanation
High likelihood: this is the documented, sanctioned way to pay dispatch fees in native token, used by every `HyperApp` example and by the wrapped fungible-token bridge (`WrappedHyperFungibleToken.send`, which forwards its own leftover `msgValue` to `dispatch{value: msgValue}` — itself already a remainder computed against a fixed wrap amount rather than a router-consumed amount) [9](#0-8) . Any deviation between the off-chain `quote()` estimate and the on-chain price at execution time (normal, expected, and explicitly warned about in the docs) will cause native overpayment and trigger the loss.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, after calling `swapETHForExactTokens`, capture the returned `amounts` array, compute `msg.value - amounts[0]`, and forward the difference back to `_msgSender()` (mirroring the pattern already implemented in `IntentGatewayV2.placeOrder`'s `_sendValue` refund).

### Proof of Concept
1. User calls `EvmHost.dispatch{value: 2 ether}(DispatchPost{fee: X, ...})` where the current on-chain price only requires 1 ether of ETH to obtain `X` fee-token via `swapETHForExactTokens`.
2. `swapETHForExactTokens{value: 2 ether}(X, path, address(this), block.timestamp)` swaps only the needed 1 ether-equivalent and refunds the remaining ~1 ether to `msg.sender` of the call, which is `EvmHost` (`address(this)` is `recipient` for the output token, but the router's ETH refund goes to whoever invoked it — `EvmHost`).
3. `EvmHost.dispatch` proceeds to build/emit the `PostRequest` without measuring or refunding the leftover ETH; the ~1 ether stays in `EvmHost`'s balance permanently, unattributed to the user, with no user-facing recovery function.

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

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L337-340)
```text
        // Apply a generous 2x buffer to absorb the legacy deployed host's
        // per-byte protocol fee (the in-source host has no such markup). Excess
        // native is refunded by the uniswap router; excess feeToken approval is
        // simply unused.
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

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L457-459)
```text
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(getRequest);
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L184-187)
```text
        // User must send enough native tokens to cover fees
        // The Host will swap native -> feeToken via Uniswap
        return IDispatcher(host()).dispatch{value: msg.value}(post);
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
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
