### Title
Excess native `msg.value` sent to `EvmHost.dispatch()`/`fundRequest()` is never refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap the entire `msg.value` for an exact amount of fee token via `swapETHForExactTokens{value: msg.value}(fee, ...)`, but never capture the returned `amounts[0]` (actual ETH spent) nor forward/refund the difference back to the caller. This mirrors the reported "purchase takes more than what is needed" bug class: the check only ensures `msg.value` is *enough* to cover the fee, but any surplus is silently absorbed rather than returned to the payer.

### Finding Description
In `EvmHost.sol`, all three payable entry points that accept native token for fee payment follow the same pattern: [1](#0-0) 

```solidity
function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
    if (msg.value > 0) {
        ...
        IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
            post.fee, path, address(this), block.timestamp
        );
    } else if (post.fee > 0) {
        IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), post.fee);
    }
    ...
}
```

The identical pattern exists in `dispatch(DispatchGet)` [2](#0-1)  and in `fundRequest()` [3](#0-2) .

The standard `IUniswapV2Router02.swapETHForExactTokens` implementation refunds any unused ETH (`msg.value - amounts[0]`) to `msg.sender` of that call — which, in this context, is `EvmHost` itself (since `EvmHost` is the one calling the router with `{value: msg.value}`), not the original caller/app/user who initiated the `dispatch()`/`fundRequest()` transaction. `EvmHost` never captures this returned value and has no code path (`receive()`, `withdraw`, or explicit refund logic) that returns this leftover ETH to the original caller. As a result, any amount sent above the exact swap requirement (`post.fee`/`get.fee`/`amount`) is permanently stranded in the `EvmHost` contract's balance, unlike the pattern correctly implemented elsewhere in the codebase (e.g. `IntentGatewayV2.placeOrder`, which captures `amounts[0]` and refunds the remainder via `_sendValue(msg.sender, msgValue)` — see [4](#0-3)  — and the same pattern's test confirming refund behavior [5](#0-4) ).

Documentation for these dispatch functions explicitly instructs integrators to send `msg.value` for the swap without describing any exact-amount requirement or refund mechanism [6](#0-5) , and the "Estimate Fees Off-Chain" warning even acknowledges the quote is imprecise and subject to sandwich attacks/slippage [7](#0-6) , meaning callers are expected to over-provide native token as a buffer — which is exactly the surplus that gets stuck.

### Impact Explanation
Every unprivileged app contract or end user that dispatches a POST/GET request or funds a pending request using native token payment (a routine, single-transaction operation reachable by anyone) loses any excess ETH/native token sent above the exact fee-swap requirement. Because slippage, price movement between quoting and execution, or an intentional buffer (as explicitly recommended by protocol docs to avoid reverts) will almost always cause `msg.value > amounts[0]`, this is a systematic, protocol-wide fund loss affecting the primary message-dispatch entry point of Hyperbridge (`EvmHost.dispatch`), not an edge case. Funds are permanently locked in the Host contract with no user-facing recovery path — a genuine "permanent freezing of funds" condition for the affected non-refunded surplus.

### Likelihood Explanation
High. This code path is exercised on every native-token-funded `dispatch()` or `fundRequest()` call, which is the standard way of paying protocol fees per the official documentation. Any caller who doesn't send the *exact* quoted amount (which is inherently unstable due to AMM price movement and is explicitly flagged as an approximation in the docs) will trigger the loss on every single call, with no special conditions or attacker required — this is a self-inflicted but unavoidable loss for normal dApp usage patterns.

### Recommendation
Capture the actual amount spent (`amounts[0]`) returned by `swapETHForExactTokens` in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, and refund `msg.value - amounts[0]` back to `_msgSender()` (or `post.payer`/appropriate payer) at the end of each function, mirroring the pattern already correctly implemented in `IntentGatewayV2.placeOrder`/`fillOrder`.

### Proof of Concept
1. Attacker/user calls `EvmHost.dispatch(DispatchPost{...fee: 1e18...})` with `msg.value = 2 ether` (a reasonable buffer given expected slippage, as documented).
2. Internally, `swapETHForExactTokens{value: 2 ether}(1e18, path, address(this), ...)` executes: the router swaps only the ETH needed to yield exactly `1e18` fee tokens (e.g., 1 ether) and refunds the remaining ~1 ether to `msg.sender`, i.e., `EvmHost`.
3. `EvmHost` never reads the return value nor forwards/refunds anything to the original caller; the ~1 ether refund becomes stuck in `EvmHost`'s balance.
4. The caller's transaction succeeds, the request is dispatched with `post.fee = 1e18` recorded correctly, but the caller has permanently lost ~1 ether with no function available to reclaim it.

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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3740-3751)
```text
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
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L48-69)
```text
## Dispatching a POST Request

Here's a complete example of how to dispatch a POST request:

```solidity lineNumbers title="MyApp.sol"
function sendMessage(
    bytes memory message,
    uint64 timeout,
    address to,
    uint256 relayerFee
) public payable returns (bytes32) {
    DispatchPost memory post = DispatchPost({
        body: message,
        dest: StateMachine.evm(1),
        timeout: timeout,
        to: abi.encode(to),
        fee: relayerFee,
        payer: msg.sender
    });

    return IDispatcher(_host).dispatch{value: msg.value}(post);
}
```

**File:** docs/content/developers/evm/messaging/get-requests.mdx (L509-510)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
```
