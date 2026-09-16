### Title
`EvmHost.dispatch`/`fundRequest` never refund unused native token from the fee-swap, permanently trapping user overpayment - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` all accept native token payment for Hyperbridge relayer fees by forwarding the *entire* `msg.value` into `swapETHForExactTokens(requiredFee, path, address(this), block.timestamp)`. This is analogous to the CBridge `M-09` bug class: the contract does not enforce that the exact required amount is provided, and — unlike `IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` in the same codebase, which correctly capture the swap's return value and refund unspent `msgValue` back to `msg.sender` — `EvmHost` neither checks the swap's returned `amounts[0]` nor refunds the leftover ETH to the caller.

### Finding Description
In `dispatch(DispatchPost)`: [1](#0-0) 
the full `msg.value` is passed to `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`. The Uniswap V2 router refunds any unspent ETH to its immediate caller, which is `EvmHost` itself (`address(this)`) — not the original transaction sender or the calling application contract. `EvmHost` does not capture the swap's returned amount, nor does it forward any leftover ETH back to `_msgSender()`.

The identical pattern exists in `dispatch(DispatchGet)`: [2](#0-1) 
and in `fundRequest`: [3](#0-2) 

By contrast, the codebase demonstrates the *correct* pattern elsewhere: `IntentGatewayV2.placeOrder` reads the actual `amounts[0]` spent by `swapETHForExactTokens` and reduces `msgValue` accordingly before refunding the remainder to the payer [4](#0-3) , and `ExtrinsicIntents._fillCrossChain` explicitly refunds unspent native value to `msg.sender` after dispatch [5](#0-4) . `EvmHost.dispatch`/`fundRequest`, the lowest-level and most widely used entry point (called directly by `WrappedHyperFungibleToken.send()` [6](#0-5) , by `HyperbridgeLzEndpoint`, and by any app following the documented pattern `IDispatcher(_host).dispatch{value: msg.value}(post)` [7](#0-6) ), lacks this safeguard entirely.

Because the required fee amount (`post.fee`/`get.fee`/`amount`) is denominated in the fee token and its native-token price fluctuates with market conditions, any caller — whether a naive integrator manually estimating `msg.value`, or an app forwarding a conservative overestimate — will routinely overpay. The leftover ETH is not lost to slippage protection or gas; it is silently absorbed into `EvmHost`'s own balance with no accounting linking it back to the depositor.

### Impact Explanation
The excess native token becomes indistinguishable, unbacked balance sitting in the `EvmHost` contract. It is not returned to the payer, and there is no on-chain event or mapping crediting it to them. The only path to move it out of the contract is `IHostManager.withdraw(WithdrawParams)`, restricted to the privileged `hostManager` [8](#0-7) . This means:
- For the depositor, this is a **permanent loss of the overpaid native token** — they have no recovery mechanism.
- The funds are effectively converted into unaccounted protocol-owned balance without governance ever having explicitly authorized or tracked that inflow, silently diverting user funds into the protocol's discretion.

This matches the accepted impact category of permanent freezing/loss of user funds via an unprivileged path (any relayer/message dispatcher paying fees in native token through the standard, documented flow).

### Likelihood Explanation
This is highly likely to occur in normal operation, not an edge case:
- The documented usage pattern explicitly forwards raw `msg.value` to `dispatch()` [7](#0-6) , with no guidance to compute the exact native amount required beforehand (the `quote()` helper referenced elsewhere estimates but exact on-chain price at execution time can differ, requiring users to send a buffer).
- `WrappedHyperFungibleToken.send()` explicitly documents forwarding "the remainder of `msg.value`" as the native fee payment with no exact matching required [9](#0-8) .
- Any integrator following the pattern used by `IntentGatewayV2` (send a generous buffer, expect refund) but calling `EvmHost.dispatch` directly will lose the buffer, since `EvmHost` itself provides no such refund, unlike its own application-layer contracts.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the actual amount spent from `swapETHForExactTokens` (its return value `amounts[0]`) and refund `msg.value - amounts[0]` back to `_msgSender()` via a low-level call, mirroring the pattern already implemented in `IntentGatewayV2` and `ExtrinsicIntents`/`IntrinsicIntents`. Alternatively, enforce that `msg.value` exactly matches the quoted/required native amount and revert otherwise.

### Proof of Concept
1. A relayer or application calls `EvmHost.dispatch{value: X}(post)` where `post.fee = F` (fee-token amount), and `X` (ETH) is a reasonable buffer above the current market-rate cost of `F` fee tokens (e.g., due to price fluctuation between quoting and execution, or because the caller intentionally overpays for safety margin, as is normal/recommended in AMM-fee-based systems).
2. `dispatch` calls `swapETHForExactTokens{value: X}(F, path, address(this), block.timestamp)` [1](#0-0) .
3. The router consumes only `amountIn < X` ETH to acquire exactly `F` fee tokens and refunds `X - amountIn` ETH to its caller, `EvmHost` (`address(this)`), per standard `UniswapV2Router02.swapETHForExactTokens` behavior.
4. `dispatch()` returns normally; the caller receives no refund of `X - amountIn`. This ETH is now permanently part of `EvmHost`'s balance, unreachable by the original payer, and only withdrawable by the privileged `hostManager` via `IHostManager.withdraw` [8](#0-7) .
5. Repeat across many callers/transactions — every native-fee payer who overpays (which is the norm given price volatility and the lack of an exact-amount requirement) contributes permanently lost funds that accumulate silently in `EvmHost`.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L256-281)
```text
     * @notice Locks underlying tokens and dispatches a cross-chain transfer message
     * @dev If `_isWeth` is true and msg.value is sufficient, wraps native tokens via the underlying's WETH
     * deposit function (reverts if the underlying is not WETH). The remainder of msg.value
     * after wrapping is forwarded as native payment for dispatch fees.
     *
     * If `_isWeth` is false, locks ERC20 tokens via safeTransferFrom and pays
     * dispatch fees in the host's fee token (pulled from msg.sender).
     *
     * @param params The send parameters including destination, recipient, amount, and optional calldata
     */
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L52-69)
```text
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
