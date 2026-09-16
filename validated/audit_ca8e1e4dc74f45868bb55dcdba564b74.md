### Title
Overpaid native-token dispatch fee in `EvmHost.dispatch()`/`fundRequest()` is refunded to the Host contract itself, not to the sender - ([File: evm/src/core/EvmHost.sol])

### Summary
The reported Cally bug is a class of "unrestricted overpayment where the excess accrues to the wrong party." `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept `msg.value` and forward the *entire* amount into `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(fee, ...)` without first checking that `msg.value` is the exact amount required for the fee, and without a corresponding refund-to-sender step afterward. [1](#0-0) [2](#0-1) 

### Finding Description
`swapETHForExactTokens` on a standard UniswapV2 router refunds any unspent ETH to `msg.sender` of that call. Because `EvmHost` itself is the direct caller of the router (the user only calls `EvmHost.dispatch`/`fundRequest`), any leftover ETH from an overpaid `msg.value` is refunded back into the `EvmHost` contract's own balance rather than to the original transaction sender who overpaid. This is explicitly confirmed by the project's own wrapper test, which asserts that "refund returns to caller" (i.e. the direct caller of the swap function, not the end user): [3](#0-2) 

Unlike `IntentGatewayV2`, which was hardened specifically against this overpayment class — explicitly tracking `msgValue` after the `swapETHForExactTokens` call and sending the unspent remainder back to `msg.sender` via `_sendValue` — [4](#0-3)  `EvmHost.dispatch()` and `EvmHost.fundRequest()` have no such accounting or refund logic at all: [5](#0-4) [6](#0-5) 

`EvmHost` has no mechanism visible in these functions to return this stranded ETH to the original payer — the fee accounting (`_requestCommitments[commitment] = FeeMetadata({sender: post.payer, fee: post.fee})`) only tracks `post.fee` in the fee token, not any excess native ETH sent. [7](#0-6) 

Any relayer, dApp integrator, or end user who over-estimates the ETH needed for the Uniswap swap (e.g., due to slippage buffers, stale quotes, or a naive frontend that sends a "safety margin" of ETH as documented in `post-requests.mdx`'s "User must send enough native tokens to cover fees" guidance) permanently loses the difference into the `EvmHost` contract, with no path to reclaim it.

### Impact Explanation
This is a direct, unrestricted loss-of-funds bug reachable by any unprivileged caller of `dispatch()`/`fundRequest()` (i.e., any HyperApp integrator or any user calling `IDispatcher(host).dispatch{value: msg.value}(...)` per the documented usage pattern [8](#0-7) ). Overpaid ETH becomes permanently stuck in the `EvmHost` contract with no user-facing withdrawal path, constituting a permanent freezing/loss of user funds — the same root cause category as the referenced Cally finding (overpayment captured by the wrong party), except here funds go to the protocol's own core contract balance instead of being refundable, and there is no visible sweep/withdraw function for this ETH in the excerpted code.

### Likelihood Explanation
Likelihood is high in practice: the documented integration pattern explicitly tells app developers to send `msg.value` "to cover fees" via a swap whose exact input cost cannot be known precisely on-chain (the docs themselves warn `quote()` is only safe to use off-chain due to sandwich-attack risk, implying on-chain callers must send a buffer) [9](#0-8) . Any slippage/price movement between quote and execution, or any deliberately generous `msg.value`, results in silently lost funds every single time the swap doesn't consume exactly `msg.value`.

### Recommendation
Mirror the pattern already implemented in `IntentGatewayV2._processInputs`/`placeOrder`: capture the `amounts[0]` actually spent returned by `swapETHForExactTokens`, and refund `msg.value - amounts[0]` back to `_msgSender()` (not swallow it into the host) in `EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()`.

### Proof of Concept
1. Caller invokes `EvmHost.dispatch{value: X}(DispatchPost{fee: F, ...})` where `X > amountRequiredToSwapForF` (e.g., sent with a safety margin, or price moved favorably between quote and execution).
2. Inside `dispatch()`, `swapETHForExactTokens{value: X}(F, path, address(this), block.timestamp)` is called — `address(this)` (`EvmHost`) is `msg.sender` of this router call.
3. The router computes `amountIn < X`, transfers `amountIn` worth of ETH into the swap, and refunds `X - amountIn` back to `msg.sender`, i.e. to `EvmHost`, not to the original caller.
4. `dispatch()` returns; the caller has irreversibly lost `X - amountIn` ETH, and `EvmHost` now holds it with no observed function to return it to the caller. [1](#0-0)

### Citations

**File:** evm/src/core/EvmHost.sol (L921-951)
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
```

**File:** evm/src/core/EvmHost.sol (L1031-1050)
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
```

**File:** evm/tests/foundry/UniV4UniswapV2WrapperTest.sol (L107-108)
```text
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```
