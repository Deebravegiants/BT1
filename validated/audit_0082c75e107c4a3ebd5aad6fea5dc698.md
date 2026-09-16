### Title
Excess native ETH sent to `EvmHost.dispatch`/`fundRequest` is refunded to the Host contract instead of the caller, permanently trapping user funds - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest` all accept native-token payment and swap it for `feeToken` via `swapETHForExactTokens{value: msg.value}(fee, ...)`. Just like the Allo `_createPool` bug, callers are structurally forced to overpay `msg.value` (the exact AMM cost cannot be known on-chain and the docs explicitly warn against calling `quote()` on-chain due to sandwich risk, mandating a buffer), but the resulting dust ETH refund from Uniswap is sent to `address(this)` (the Host) rather than back to the original caller, so it is never returned.

### Finding Description
In `dispatch(DispatchPost memory post)`: [1](#0-0) 

`swapETHForExactTokens` is called with `msg.value` as the ETH input and `path`/`to = address(this)` for the token leg. Per UniswapV2Router semantics, any unspent ETH ("dust") from this call is refunded via `TransferHelper.safeTransferETH(msg.sender, msg.value - amountIn)`, where `msg.sender` in that inner call is `EvmHost` itself (since `EvmHost` is the caller of the router). The refunded dust therefore lands in `EvmHost`'s own balance. Nowhere in `dispatch()` after the swap call is any leftover native balance forwarded back to `_msgSender()` (the original caller/app/user).

The identical pattern repeats in `dispatch(DispatchGet memory get)`: [2](#0-1) 

and in `fundRequest`: [3](#0-2) 

The Hyperbridge developer documentation confirms that callers are expected to send `msg.value` directly without any refund handling in the app, and explicitly warns that off-chain quotes ("Do not call `quote()` in smart contract transactions... vulnerable to sandwich attacks") force integrators to send buffer amounts of native ETH: [4](#0-3) [5](#0-4) 

By contrast, the codebase demonstrates that the "correct" pattern is to capture the swap's `amountIn` and refund any unused native value to the original payer, as done by `IntentGatewayV2._fillCrossChain` (which computes `msgValue -= amounts[0]` after swaps and refunds any remainder via `_sendValue(msg.sender, msgValue)`): [6](#0-5) [7](#0-6) 

`EvmHost.dispatch`/`fundRequest` implement none of this refund logic — the exact bug class described in the Allo report (forced overpayment of native value with no credit-back), but here at the base protocol layer that every app (`HyperApp`, `IntentGatewayV2`, `HyperFungibleTokenUpgradeable`, LayerZero endpoint adapters, etc.) and any unprivileged end user relies on when dispatching messages with native-token payment.

### Impact Explanation
Any unprivileged user or contract that dispatches a POST/GET request or funds a pending request by sending `msg.value` in excess of the AMM's exact input requirement (which is unavoidable in practice given price-fluctuation risk and the explicit guidance against on-chain quoting) permanently loses the excess ETH — it is retained in the `EvmHost` contract's balance with no visible sweep/withdraw path back to the payer. This is a direct, protocol-wide loss of funds for any relayer, app, or end user using native-token payment for dispatch, and it also breaks integrations that assume standard "refund excess msg.value" semantics (matching the "could also break integrations of other systems / contracts" impact called out in the original report).

### Likelihood Explanation
High likelihood: this triggers on every native-token-funded `dispatch()` or `fundRequest()` call where the sender doesn't send the *exact* wei amount required by the Uniswap swap at execution time — which is essentially guaranteed in practice since callers must estimate off-chain (per the documentation's own guidance) and add a safety buffer to avoid reverts from price movement between quoting and execution (sandwich/slippage risk). No privileged role or special conditions are needed; this is reachable by any external caller dispatching a single message with native value.

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the `amounts` array returned by the router and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`/`get`'s payer) via a low-level ETH transfer, mirroring the pattern already implemented in `IntentGatewayV2._fillCrossChain` and `ExtrinsicIntents._post`/`_fillCrossChain`.

### Proof of Concept
1. Caller A (e.g., an app built on `HyperApp`, following the documented pattern) calls `EvmHost.dispatch{value: X}(post)` where `X` is a generous buffer above the exact wei needed to swap for `post.fee` amount of `feeToken` (as recommended by the docs since on-chain quoting is unsafe).
2. Inside `dispatch`, `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes; suppose the actual required input is `Y < X`.
3. The Uniswap router refunds `X - Y` ETH to `msg.sender` of the swap call — which is `EvmHost`, not caller A.
4. `dispatch()` returns without ever forwarding the `X - Y` dust back to caller A.
5. Caller A's excess ETH is now stuck in `EvmHost`'s balance permanently, with no corresponding accounting or withdrawal mechanism returning it to caller A.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-187)
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
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-238)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>
```

**File:** evm/src/apps/IntentGatewayV2.sol (L375-389)
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
