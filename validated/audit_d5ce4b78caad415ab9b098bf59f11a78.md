### Title
`EvmHost.dispatch` swaps entire `msg.value` via Uniswap, permanently trapping excess native token overpayment in the host contract - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchPost)` and `EvmHost.dispatch(DispatchGet)` forward the caller's *entire* `msg.value` into `swapETHForExactTokens{value: msg.value}(post.fee, ...)`, but the Uniswap V2 router refunds any unused ETH to `msg.sender` of that inner call — which is `EvmHost` itself, not the original external caller. Any native token sent above the amount strictly needed to purchase `post.fee`/`get.fee` worth of `feeToken` is silently absorbed by the host contract instead of being returned to the user, mirroring the Allo `_createPool` bug where overpayment above `baseFee` gets stuck in the contract. [1](#0-0) [2](#0-1) 

### Finding Description
When an application dispatches a POST or GET request with native token payment, it typically forwards its own `msg.value` unmodified: [3](#0-2) 

Inside `EvmHost`, both `dispatch(DispatchPost)` and `dispatch(DispatchGet)` execute:
```solidity
if (msg.value > 0) {
    ...
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) 

`swapETHForExactTokens` only needs to spend enough ETH to buy exactly `post.fee` (or `get.fee`) worth of `feeToken`; any ETH beyond the calculated `amounts[0]` is refunded by the Uniswap router — but that refund goes to whichever address called the router, which is `EvmHost`, not the app or the end user who originally sent the excess `msg.value` to `EvmHost.dispatch()`. Because `EvmHost` never tracks or forwards this refund back to `_msgSender()`, the excess ETH becomes indistinguishable from the contract's other native balance and is effectively locked from the perspective of the depositor. The same pattern repeats in `fundRequest`: [4](#0-3) 

There is no code path in `dispatch()` or `fundRequest()` that computes the exact native amount required up front (e.g. via `getAmountsIn`) and reverts on insufficient funds while returning the surplus, nor any code that forwards the router's ETH refund back to `_msgSender()`. The only way this trapped ETH can leave `EvmHost` is via the privileged, governance-only `IHostManager.withdraw(WithdrawParams)` path (`token == address(0)` case), which is analogous to Allo's admin-only `recoverFunds`: [5](#0-4) 

This affects every unprivileged caller of `EvmHost.dispatch()` for both POST and GET requests, including all first-party apps built with `HyperApp`/`IntentGatewayV2`/`ExtrinsicIntents`/`HyperFungibleToken` that route native-token dispatch fees through `IDispatcher(_host).dispatch{value: msg.value}(...)` without pre-computing the exact swap input: [6](#0-5) [7](#0-6) 

### Impact Explanation
Because Uniswap swap price varies with market conditions and applications generally overestimate/quote `msg.value` off-chain (the docs explicitly warn `quote()` should only be used off-chain and is subject to sandwich-attack slippage), any client that sends more native token than the exact swap requires loses that surplus permanently to the `EvmHost` contract balance, recoverable only by governance via `withdraw`. This is a direct, protocol-wide loss of user funds (a form of fund freezing/theft from the depositor's perspective) affecting every dispatch of a POST or GET request paid in native token across all EVM deployments of Hyperbridge, not an isolated app bug.

### Likelihood Explanation
High likelihood: this is triggered on the ordinary "happy path" of dispatching any POST/GET request or funding a request with native token, whenever the caller's supplied `msg.value` is not exactly equal to the amount Uniswap needs to buy `post.fee`/`get.fee`/`amount` worth of `feeToken`. Given price volatility between quote time and execution time, and the documented client-side estimation flow, overpayment is the common/expected case rather than an edge case, so the loss occurs routinely with no attacker action required — every user calling any `dispatch` variant with native payment is affected.

### Recommendation
Compute the exact ETH required for the swap up front (e.g., via `getAmountsIn(post.fee, path)`), and either:
1. Revert if `msg.value` does not exactly match the required amount, or
2. Refund any leftover `msg.value` back to `_msgSender()` after the swap (checking the router's actual ETH spent, e.g., via balance delta, and sending the difference back), matching Allo's fix of only requiring `msg.value >= requiredFee` and refunding/crediting the excess to the depositor rather than absorbing it into the contract's balance.

### Proof of Concept
1. Application `A` calls `IDispatcher(host).dispatch{value: 1 ether}(post)` where `post.fee` only requires `0.5 ether` worth of ETH to purchase via `swapETHForExactTokens`.
2. `EvmHost.dispatch` executes `swapETHForExactTokens{value: 1 ether}(post.fee, path, address(this), block.timestamp)`. [8](#0-7) 
3. The Uniswap router spends only `~0.5 ether` and refunds the remaining `~0.5 ether` to `msg.sender` of the swap call, i.e., to `EvmHost`'s own address (since `EvmHost` is the caller of the router).
4. `EvmHost.dispatch` never reads or forwards this refunded ETH to `A` or `_msgSender()`; the request proceeds and completes normally.
5. The `0.5 ether` surplus remains in `EvmHost`'s native balance indefinitely, recoverable only by the privileged `hostManager` via `withdraw(WithdrawParams{token: address(0), ...})`. [9](#0-8)

### Citations

**File:** evm/src/core/EvmHost.sol (L74-96)
```text
interface IHostManager {
    /**
     * @dev Updates IsmpHost params
     * @param params new IsmpHost params
     */
    function updateHostParams(HostParams memory params) external;

    /**
     * @dev withdraws bridge revenue to the given address
     * @param params, the parameters for withdrawal
     */
    function withdraw(WithdrawParams memory params) external;
}

// Withdrawal parameters
struct WithdrawParams {
    // The beneficiary address
    address beneficiary;
    // the amount to be disbursed
    uint256 amount;
    // Withdraw the native token?
    address token;
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L166-187)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L269-274)
```text
        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-271)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
        } else {
```
