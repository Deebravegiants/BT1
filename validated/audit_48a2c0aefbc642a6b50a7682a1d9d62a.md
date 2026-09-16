### Title
Excess native ETH sent to `EvmHost.dispatch()` (POST/GET) is permanently trapped in the host contract instead of being refunded to the caller - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` accept `msg.value` and use the entire amount to call `IUniswapV2Router02.swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), ...)`. The standard UniswapV2Router02 implementation of `swapETHForExactTokens` refunds any unspent ETH to `msg.sender` of that call — which is `EvmHost` itself, not the original caller who supplied `msg.value`. As a result, any ETH sent beyond what's needed to swap into exactly `post.fee`/`get.fee` of the fee token becomes stranded inside `EvmHost`'s balance with no accounting tying it back to the original sender.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 

and identically in `dispatch(DispatchGet)`: [2](#0-1) 

The router call `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)` swaps only enough ETH to obtain exactly `post.fee` of the fee token, and the standard Uniswap V2 router implementation refunds any leftover ETH via `TransferHelper.safeTransferETH(msg.sender, msg.value - amounts[0])`. Since `EvmHost` itself is the caller of the router (not the end user), this refund lands back in `EvmHost`'s own balance rather than being returned to `_msgSender()` (the app/user who called `dispatch`). `EvmHost` does accept arbitrary ETH via its `receive()` function: [3](#0-2) 

but there is no per-caller accounting for this leftover value, and no public/permissionless function to reclaim it. The only path to move ETH out of the contract is the privileged `withdraw()` function restricted to `hostManager` governance: [4](#0-3) 

This is the exact analog of the reported bug class: a function accepts `msg.value >= requiredAmount` (implicitly, since only `post.fee`/`get.fee` worth is consumed) without enforcing exact equality or refunding the excess to the original caller, permanently locking overpaid native tokens in the contract.

Notably, the newer `IntentGatewayV2`/`ExtrinsicIntents` apps that build on top of dispatch explicitly guard against this by tracking `msgValue` and calling `_sendValue(msg.sender, msgValue)` to refund any unspent native token to the original caller after fee swaps: [5](#0-4) 
This confirms the intended, correct pattern is to refund unspent value to the caller — a pattern `EvmHost.dispatch()` itself does not implement.

### Impact Explanation
Any unprivileged caller (a message dispatcher, relayer-facing app, or a user calling `dispatch` directly to pay the request fee in native token) who overestimates the ETH required to cover `post.fee`/`get.fee` — due to slippage between fee quoting and execution, price movement in the configured UniswapV2 pool, or simply sending a safety margin of ETH — will have the excess permanently and irrecoverably locked in `EvmHost`, with no mechanism for the depositor to reclaim it. Funds can only leave via governance-gated `withdraw()`, which has no way to know which caller is owed what amount, effectively turning individual users' overpayments into an unrecoverable loss for those users. This is a direct, permanent freezing/loss of user funds within the core dispatch path of the protocol.

### Likelihood Explanation
`dispatch()` is a core, frequently invoked, permissionless entry point of `EvmHost` used by any app paying fees in native token for POST/GET requests. Because Uniswap V2 swap amounts are quoted off-chain or estimated with some buffer against slippage, sending marginally more ETH than the exact quoted swap input is a routine and expected occurrence, not an edge case, making this readily triggerable in normal operation.

### Recommendation
After the `swapETHForExactTokens` call, capture the returned `amounts[0]` (actual ETH spent) and refund `msg.value - amounts[0]` directly to `_msgSender()` (not rely on the router's refund semantics, which return leftover ETH to `EvmHost` rather than the original caller). Apply the same fix to both `dispatch(DispatchPost)` and `dispatch(DispatchGet)`, matching the refund-to-caller pattern already implemented in `evm/src/apps/intentsv2/ExtrinsicIntents.sol` and `evm/src/apps/IntentGatewayV2.sol`.

### Proof of Concept
1. A caller invokes `EvmHost.dispatch(DispatchPost)` with `msg.value = 1 ETH` while `post.fee` only requires `0.01 ETH` worth of native token to swap into the fee token (e.g. quoted with a safety buffer, or due to slippage/price movement between quote time and tx execution).
2. `EvmHost` calls `IUniswapV2Router02.swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)`.
3. The router swaps only the ~0.01 ETH needed and refunds the remaining ~0.99 ETH via `safeTransferETH(msg.sender, ...)`, where `msg.sender` from the router's perspective is `EvmHost`'s address.
4. `EvmHost.receive()` accepts the ETH into the contract's balance, but this amount is never credited back to, or made claimable by, the original caller.
5. The original caller's 0.99 ETH is now indistinguishable from protocol-owned funds and can only be extracted from the contract via the governance-only `withdraw()` function — the caller has no way to recover it themselves.

### Citations

**File:** evm/src/core/EvmHost.sol (L383-386)
```text
    /*
     * @dev receive function for UniswapV2Router02, collects all dust native tokens.
     */
    receive() external payable {}
```

**File:** evm/src/core/EvmHost.sol (L651-660)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L375-397)
```text

```
