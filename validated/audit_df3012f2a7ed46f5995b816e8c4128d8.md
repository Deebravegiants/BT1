## Title
Excess native token sent to `EvmHost.dispatch()`/`fundRequest()` is not refunded to the caller - permanently trapped in the host - (File: `evm/src/core/EvmHost.sol`)

## Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` accept native token payment and swap it for the exact `feeToken` amount required via Uniswap, but never return any leftover ETH to the original caller. This is the same bug class as the referenced Allo.sol `_fundPool` finding: a payable entrypoint that swaps/consumes only part of `msg.value` and drops the remainder instead of returning it to `msg.sender`.

## Finding Description
In each of the three payable functions, the native-token branch is: [1](#0-0) 

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
    } ...
```

The same pattern repeats for `dispatch(DispatchGet)` [2](#0-1)  and `fundRequest` [3](#0-2) .

`IUniswapV2Router02.swapETHForExactTokens(amountOut, path, to, deadline)` is only guaranteed to consume exactly the ETH needed to produce `amountOut` fee tokens for the `to` address (here `address(this)`, i.e. `EvmHost`); any unused portion of the attached `msg.value` is refunded by the *router* to its immediate caller (`msg.sender` from the router's perspective, which is `EvmHost`, not the original user). None of these three functions capture that refund and forward it back to `_msgSender()`/`post.payer`.

This is materially different from every other native-token-consuming code path found in the same repository, all of which explicitly account for and refund unspent `msg.value`:
- `IntentGatewayV2._createPool`/`placeOrder` refunds unspent value after the fee-token swap: [4](#0-3) 
- `ExtrinsicIntents._fillCrossChain` explicitly refunds any unspent native tokens to the solver: [5](#0-4) 
- The custom `UniV4UniswapV2Wrapper.swapETHForExactTokens` even goes out of its way to refund unused ETH to its caller: [6](#0-5) 

`EvmHost` is the only reachable, unprivileged, native-value-accepting dispatch entrypoint that omits this refund step entirely.

Any ETH that lands back in `EvmHost` from the router's own refund becomes indistinguishable protocol-owned balance; the only path to move native ETH out of `EvmHost` is the privileged, governance-only `IHostManager.withdraw` / `WithdrawParams` flow driven by `HostManager.onAccept`, which is not something an ordinary user can trigger for their own refund: [7](#0-6) .

## Impact Explanation
Any unprivileged user or app contract calling `IDispatcher(host).dispatch{value: msg.value}(post)` (as documented and recommended for native-token payment: [8](#0-7) ) with `msg.value` even slightly greater than the ETH needed to swap for `post.fee` permanently loses the difference. This applies to every app built on `HyperApp`/`IDispatcher.dispatch{value: ...}`, including `HyperFungibleToken.send`, `WrappedHyperFungibleTokenUpgradeable.send`, `HyperbridgeLzEndpoint.send`, and any third-party integrator following the documented native-payment pattern. The lost ETH is not stolen by an attacker but becomes stuck host-owned balance recoverable only by protocol governance, which meets the "permanent freezing of funds" criterion for this scan.

## Likelihood Explanation
High likelihood of occurrence in practice: the ETH cost of a Uniswap swap is inherently variable (dependent on pool price at execution time), so callers must estimate `msg.value` generously to avoid reverts, and the documented usage pattern (`dispatch{value: msg.value}(post)`) provides no client-side mechanism to compute the exact required amount ahead of time. Overpayment is the expected common case, not an edge case.

## Recommendation
Track `msg.value` and the actual amount consumed by the swap (as `IUniswapV2Router02.swapETHForExactTokens` returns `amounts[0]`, the ETH actually spent), then refund the difference to `_msgSender()` (or `post.payer`/`get.payer` where applicable) at the end of `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, mirroring the pattern already used in `IntentGatewayV2` and `ExtrinsicIntents`:

```solidity
if (msg.value > 0) {
    ...
    uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
    uint256 refund = msg.value - amounts[0];
    if (refund > 0) {
        (bool ok,) = _msgSender().call{value: refund}("");
        require(ok, "refund failed");
    }
}
```

## Proof of Concept
1. User calls `EvmHost.dispatch{value: 5 ether}(post)` with `post.fee = 1000` (fee-token units), intending to cover the swap cost plus a safety margin as recommended by the documented usage pattern.
2. `EvmHost.dispatch` calls `swapETHForExactTokens{value: 5 ether}(1000, [WETH, feeToken], address(this), deadline)`.
3. The router only needs, e.g., 0.2 ETH to produce 1000 fee-token units for `address(this)` (`EvmHost`); it refunds the remaining 4.8 ETH to its caller, `EvmHost`.
4. `EvmHost.dispatch` returns without forwarding that 4.8 ETH back to the user; the user's transaction only shows 5 ETH leaving their balance and no corresponding refund event/transfer.
5. The 4.8 ETH now sits in `EvmHost`'s balance, retrievable only via the privileged `IHostManager.withdraw` governance flow — not by the user who overpaid.

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

**File:** evm/src/core/EvmHost.sol (L1031-1043)
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

**File:** evm/src/apps/IntentGatewayV2.sol (L394-397)
```text
        // Refund any unspent native tokens to the user.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L214-217)
```text
        // Refund any unspent native tokens to the solver.
        if (msgValue > 0) {
            _sendValue(msg.sender, msgValue);
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L83-96)
```text
        // Snapshot standing balance (excluding inbound msg.value) so the refund is the swap-call delta only,
        // immune to any ETH that lands on the wrapper from outside the router (e.g., selfdestruct, coinbase).
        uint256 balanceBefore = address(this).balance - msg.value;

        IUniversalRouter(_params.universalRouter).execute{value: msg.value}(
            abi.encodePacked(bytes1(uint8(Commands.V4_SWAP))), inputs, deadline
        );

        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
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
