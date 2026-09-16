### Title
Surplus ETH sent to `EvmHost.dispatch()`/`fundRequest()` is stranded in the contract instead of being refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native token payment and swap it for the fee token via `IUniswapV2Router02.swapETHForExactTokens`. Any excess ETH sent above what the swap consumes is refunded by the Uniswap router to `msg.sender` of the swap call — which is `EvmHost` itself, not the original transaction sender. `EvmHost` never forwards this refund on to the actual caller, so surplus ETH becomes permanently stuck in the host contract.

### Finding Description
In `EvmHost.sol`, all three payable entry points that accept native-token fee payment follow the same pattern: [1](#0-0) 

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

The same pattern repeats for `dispatch(DispatchGet)` and `fundRequest()`: [2](#0-1) [3](#0-2) 

`swapETHForExactTokens` (per standard UniswapV2Router02 semantics, confirmed against this codebase's own wrapper implementations that explicitly document the behavior) refunds any unspent ETH ("dust") to `msg.sender` of the call. Because `EvmHost` itself calls the router (not a delegatecall/forward from the original user), the refund lands back on `EvmHost`'s own balance, not the caller's. `EvmHost` performs no accounting of `msg.value` before/after the swap and issues no refund call to `_msgSender()`/`post.payer`. Consequently, any user who sends more ETH than the swap actually needs (e.g., due to slippage buffers, price movement, or simple overestimation) permanently loses the difference to the contract.

This is the direct analog of the reported `ExchangeProxy.executeSwapDirect()` bug: `require(msg.value >= ethValue, ...)` accepts a surplus but never returns it, and the surplus is not reachable by the original depositor afterward.

Contrast this with the rest of the codebase, where every other native-value-consuming dispatch path explicitly tracks `msgValue` and refunds the excess back to `msg.sender`:
- `IntentGatewayV2.sol` explicitly refunds unspent native tokens after the same swap call: `msgValue -= amounts[0]; ... if (msgValue > 0) { _sendValue(msg.sender, msgValue); }` [4](#0-3) 
- `ExtrinsicIntents.sol` similarly refunds unspent native to the solver. [5](#0-4) 
- `WrappedHyperFungibleToken.sol` computes the remainder of `msg.value` and forwards only that amount onward, so nothing is lost. [6](#0-5) 

`EvmHost.sol` — the core dispatcher that every app in the system relies on — is missing this refund entirely.

The only path to recover stranded native ETH from `EvmHost` is `withdraw(WithdrawParams)`, which is restricted to the `hostManager` and is intended for cross-chain-governance-driven bridge revenue withdrawal to an arbitrary beneficiary, not a mechanism to make a specific over-paying user whole: [7](#0-6) 

### Impact Explanation
Any unprivileged caller of `IDispatcher(host).dispatch{value: msg.value}(...)` or `fundRequest{value: msg.value}(...)` — which includes every `HyperApp` integrator relying on native-token fee payment (documented as a first-class supported flow in `IDispatcher`/`HyperApp` docs) — permanently loses any ETH sent beyond what the Uniswap swap consumes. Because slippage/price-impact makes it hard to send the *exact* required amount, and the documented usage pattern (`dispatch{value: msg.value}(post)`) actively encourages sending a buffer, this loss is systemic rather than a one-off edge case. Funds are not recoverable by the depositor; recovery, if it ever happens, depends on discretionary governance action via `withdraw()`, and even then goes to whatever `beneficiary` governance chooses — not necessarily the original payer.

### Likelihood Explanation
High. Any app/integrator using the documented native-token payment flow for `dispatch()`/`fundRequest()` and sending a reasonable slippage buffer (which is standard and even recommended off-chain, since `quote()` is explicitly warned to be sandwich-attack-prone and unsuitable for exact on-chain sizing) will trigger this loss on essentially every call. No special conditions, races, or malicious actors are required — it happens under normal, expected usage.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture `msg.value` before the swap, subtract the amount actually consumed (`amounts[0]` returned by `swapETHForExactTokens`), and refund any remainder back to `_msgSender()` (or the designated payer), mirroring the pattern already used in `IntentGatewayV2._placeOrder` / `ExtrinsicIntents._fillCrossChain`:

```solidity
if (msg.value > 0) {
    ...
    uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
    uint256 refund = msg.value - amounts[0];
    if (refund > 0) {
        (bool sent, ) = _msgSender().call{value: refund}("");
        require(sent, "refund failed");
    }
}
```

### Proof of Concept
1. Deploy `EvmHost` with a configured `uniswapV2` router and `feeToken`.
2. An app contract calls `IDispatcher(host).dispatch{value: X}(post)` where `post.fee = F`, and `X > amountsIn` needed to obtain `F` fee tokens (e.g., user pads the value by 20% to survive slippage, as recommended in the docs' warning against relying on `quote()` for exact sizing).
3. `swapETHForExactTokens{value: X}` spends only `amountsIn <= X` and refunds `X - amountsIn` — but the refund target is `EvmHost` (the caller of the router), not the original `_msgSender()`.
4. `dispatch()` returns normally; `address(host).balance` increases by `X - amountsIn` with no accounting tying it back to the original caller.
5. The original caller has no function to reclaim this ETH; only cross-chain governance via `withdraw()` can move it, and only to a beneficiary of governance's choosing. [1](#0-0)

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
