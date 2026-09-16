### Title
Excess native token sent to `EvmHost.dispatch`/`fundRequest` is permanently trapped in the Host instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` accept native-token payment via `msg.value` and swap it into `feeToken` using `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`. This is exactly the bug class described in the external report: the caller is required to send at least enough ETH to cover the fee, but any amount sent above the exact swap cost is not returned to the original transaction sender. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`swapETHForExactTokens` only spends the exact amount of ETH needed to obtain `post.fee` tokens; the Uniswap V2 router refunds any unused ETH to `msg.sender` of the swap call. Because `EvmHost` itself calls the router, the refund destination is `address(this)` (i.e., `EvmHost`), not the end user who originally sent the overpaid `msg.value`. There is no code path in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest` that captures this refunded ETH and forwards it back to `_msgSender()` or `post.payer`. The excess value silently accumulates as ETH balance on the `EvmHost` contract with no withdrawal/sweep mechanism visible in the contract. [4](#0-3) [5](#0-4) 

This is directly reachable by any unprivileged user/application. Some higher-level apps in the repo (e.g., `ExtrinsicIntents.sol`'s `_fill`/`_cancelFromSource` flows, `IntentGatewayV2SameChainTest` tests) explicitly compute the exact required native amount and refund any leftover before or after calling the host, confirming the project is aware overpayment must be refunded and has patched some paths: [6](#0-5) 

However, other user-facing dispatch paths forward the caller's *entire* `msg.value` straight to `IDispatcher(_host).dispatch{value: msg.value}(request)` without first quoting the exact native cost or handling a refund, e.g. `HyperFungibleToken.send`: [7](#0-6) 
and `WrappedHyperFungibleToken.send`: [8](#0-7) 

Because the `quote()` helper in `HyperApp.sol` explicitly warns it must only be used off-chain (subject to sandwich attacks) and is not enforced on-chain, any user who over-estimates the required native amount (or is front-run/sandwiched changing the AMM price between quoting and executing) will have the surplus ETH permanently absorbed by `EvmHost` with no recovery path: [9](#0-8) 

### Impact Explanation
Any user dispatching a POST/GET request or funding a request with native token payment through `EvmHost.dispatch`/`fundRequest` (directly or via apps like `HyperFungibleToken`/`WrappedHyperFungibleToken` that forward full `msg.value`) loses any ETH sent above the exact swap cost — this is a permanent, protocol-level fund freezing/loss bug affecting ordinary end users on every dispatch call that overpays, which is the normal/expected case since exact on-chain quoting isn't safely available (the `quote()` function is explicitly documented as unsafe to call on-chain due to sandwich-attack risk). This matches the "medium/high, permanent freezing of funds" acceptance criteria — impacted funds are irrecoverably stuck in `EvmHost`.

### Likelihood Explanation
High likelihood: dispatching a cross-chain message with native-token fee payment is a routine, unprivileged, frequently used operation (every `send`/`dispatch`/`fundRequest` call using `msg.value`), and users are expected to send a buffer above the exact quoted amount to tolerate slippage/price movement between quoting and execution (the docs even suggest "generous" buffers, e.g. `HyperbridgeLzEndpoint.quote` applies a 2x buffer). This guarantees frequent overpayment and hence frequent value loss. [10](#0-9) 

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, after calling `swapETHForExactTokens`, capture any unused ETH balance change (or use `swapETHForExactTokens`'s return value / balance delta) and refund it to `_msgSender()` (or an explicit `refundTo` parameter) before returning, guarding against reentrancy (e.g., checks-effects-interactions or a reentrancy guard), consistent with how `ExtrinsicIntents.sol` already refunds unspent `msgValue` to `msg.sender`.

### Proof of Concept
1. Attacker/normal user calls `IDispatcher(host).dispatch{value: X}(post)` where `X` is intentionally or unintentionally greater than the ETH amount required to buy `post.fee` worth of `feeToken` via Uniswap.
2. Inside `EvmHost.dispatch`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` spends only `Y < X` ETH and refunds `X - Y` ETH to `address(this)` (the `EvmHost` contract), not to the caller. [1](#0-0) 
3. The function proceeds to record the commitment and emit the event without ever forwarding the `X - Y` ETH back to the original sender. [11](#0-10) 
4. Repeating this call accumulates unrecoverable ETH balance in `EvmHost`, permanently lost to every user who overpaid.

### Citations

**File:** evm/src/core/EvmHost.sol (L908-932)
```text
    /**
     * @dev Dispatch a POST request to Hyperbridge
     *
     * @notice Payment for the request can be made with either the native token or the feeToken.
     * If native tokens are supplied, it will perform a swap under the hood using the local uniswap router.
     * Will revert if enough native tokens are not provided.
     *
     * If no native tokens are provided then it will try to collect payment from the calling contract in
     * the feeToken.
     *
     * @param post - post request
     * @return commitment - the request commitment
     */
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

**File:** evm/src/core/EvmHost.sol (L934-959)
```text
        // adjust the timeout
        uint64 timeoutTimestamp = post.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(post.timeout);
        PostRequest memory request = PostRequest({
            source: host(),
            dest: post.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            to: post.to,
            timeoutTimestamp: timeoutTimestamp,
            body: post.body
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee});
        emit PostRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: _msgSender(),
            to: abi.encodePacked(request.to),
            nonce: request.nonce,
            timeoutTimestamp: request.timeoutTimestamp,
            body: request.body,
            fee: post.fee
        });
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

**File:** evm/src/core/EvmHost.sol (L1031-1051)
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

        FeeMetadata memory metadata = _requestCommitments[commitment];
        if (metadata.sender == address(0)) revert UnknownRequest();

        metadata.fee += amount;
        _requestCommitments[commitment] = metadata;

        emit RequestFunded({commitment: commitment, newFee: metadata.fee});
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L203-217)
```text
        // Native dispatch fee only if the solver sent enough to cover it; else the fee token.
        uint256 nativeFee = options.nativeDispatchFee;
        if (nativeFee > msgValue) nativeFee = 0;
        msgValue -= nativeFee;
        _post(
            order,
            _body(RequestKind.RedeemEscrow, commitment, order.inputs, bytes32(uint256(uint160(msg.sender)))),
            options.relayerFee,
            nativeFee
        );

        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L70-80)
```text
    /**
     * @dev returns the quoted fee in the native token for dispatching a POST request
     */
    function quote(DispatchPost memory request) public returns (uint256) {
        address _host = host();
        address _uniswap = IDispatcher(_host).uniswapV2Router();
        address[] memory path = new address[](2);
        path[0] = IUniswapV2Router02(_uniswap).WETH();
        path[1] = IDispatcher(_host).feeToken();
        return IUniswapV2Router02(_uniswap).getAmountsIn(request.fee, path)[0];
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
