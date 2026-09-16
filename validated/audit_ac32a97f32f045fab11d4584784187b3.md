### Title
Excess native token sent to `EvmHost.dispatch()`/`fundRequest()` is not refunded to the caller and is only recoverable by governance, not the payer - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all accept `msg.value` and forward it wholesale to `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(...)`. This router call only spends the exact amount of ETH needed to buy `post.fee`/`get.fee`/`amount` fee tokens, refunding the unspent difference — but the refund goes back to `msg.sender` of the router call, which is `EvmHost` itself, not the original transaction sender. None of these three functions reads the `amounts[0]` (actual ETH spent) returned by `swapETHForExactTokens` or refunds the leftover native balance to the original caller. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Contrast this with `IntentGatewayV2.placeOrder`, which performs the identical Uniswap swap but explicitly tracks `amounts[0]` and refunds the remainder to `msg.sender`: [4](#0-3) 

`EvmHost.dispatch`/`fundRequest` have no equivalent logic — the returned `amounts` array from `swapETHForExactTokens` is discarded entirely, and there is no `_sendValue`/refund step after the swap: [5](#0-4) [6](#0-5) 

Because `UniswapV2Router02.swapETHForExactTokens` refunds unspent ETH to its immediate caller (`msg.sender` from the router's perspective, i.e. `EvmHost`), any native token sent in excess of what is required to buy the exact `fee`/`amount` accumulates permanently on the `EvmHost` contract's balance. The only way to move that ETH back out is via `IHostManager.withdraw()`, which is `restrict(_hostParams.hostManager)` — callable exclusively by cross-chain governance, not by the user who overpaid. [7](#0-6) 

Docs for `HyperApp.sendMessageWithNative` even instruct integrators to send `msg.value` "to cover fees" without any promise of exact-amount consumption, encouraging users/apps to send buffer amounts: [8](#0-7) 

Any caller who cannot perfectly predict the on-chain Uniswap V2 price at execution time (which is essentially guaranteed under any real usage due to slippage/MEV/price movement between quote and execution) will overpay and have the difference permanently stuck in `EvmHost`, unrecoverable except by protocol governance sweeping it to an arbitrary beneficiary — not back to the original depositor.

### Impact Explanation
This is a permanent, protocol-wide loss of funds for any user/app dispatching a POST/GET request or funding a request with native token payment whenever the exact swap amount is smaller than the ETH sent (which is the normal, expected outcome of `swapETHForExactTokens` with any reasonable buffer). Given that native-token payment is a first-class, documented payment path for `dispatch()`/`fundRequest()`, and dispatches happen from a single external transaction with no way for the caller to guarantee `msg.value` exactly equals the swap cost, this is a systemic freezing-of-funds issue reachable by any unprivileged message dispatcher.

### Likelihood Explanation
High likelihood: any caller using the native-token payment path (the officially documented and SDK-supported flow for `dispatch{value: ...}`) that sends slightly more ETH than the router's precise `amountIn` for the exact fee/amount will lose the difference. Since off-chain quoting (`quote()`) is explicitly warned in docs to be approximate/sandwich-able, and users must send some buffer to avoid reverts, overpayment (and thus permanent loss) is the expected common case, not an edge case.

### Recommendation
Capture the `amounts` array returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, and refund `msg.value - amounts[0]` back to `_msgSender()` (or the designated payer), mirroring the pattern already implemented in `IntentGatewayV2.placeOrder`.

### Proof of Concept
1. Caller estimates fee cost off-chain via `EvmHost.quote()` or an SDK helper, then calls `IDispatcher(host).dispatch{value: X}(post)` with `X` slightly padded above the estimate to guard against slippage (standard, encouraged practice — see docs above).
2. Inside `dispatch`, `EvmHost` calls `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)`.
3. The router spends only `Y < X` ETH to acquire exactly `post.fee` fee tokens and refunds `X - Y` ETH to `msg.sender`, which from the router's perspective is `EvmHost`.
4. `EvmHost.dispatch` never reads or forwards this refund; the `X - Y` ETH remains on the `EvmHost` contract balance indefinitely.
5. The original caller has no function to reclaim `X - Y`; only `IHostManager.withdraw()`, restricted to cross-chain governance via `_hostParams.hostManager`, can move that ETH — and only to an arbitrary governance-specified beneficiary, not back to the caller.

### Citations

**File:** evm/src/core/EvmHost.sol (L647-660)
```text
    /**
     * @dev withdraws host revenue to the given address, can only be called by cross-chain governance
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external restrict(_hostParams.hostManager) {
        if (params.token == address(0)) {
            // this is safe because re-entrancy is mitigated before dispatching requests
            (bool sent,) = params.beneficiary.call{value: params.amount}("");
            if (!sent) revert WithdrawalFailed();
        } else {
            IERC20(params.token).safeTransfer(params.beneficiary, params.amount);
        }
        emit HostWithdrawal({beneficiary: params.beneficiary, amount: params.amount, token: params.token});
    }
```

**File:** evm/src/core/EvmHost.sol (L921-959)
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-189)
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
```
