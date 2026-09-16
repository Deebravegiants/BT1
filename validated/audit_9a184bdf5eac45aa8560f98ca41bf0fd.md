### Title
Excess native `msg.value` sent to `EvmHost.dispatch()`/`fundRequest()` is silently trapped instead of refunded to the caller - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` all accept native token payment and swap it for the exact fee amount via `IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)`, exactly the pattern flagged in the external report ("no change returned in case of extra fee value").

### Finding Description
In each of the three functions, the entire `msg.value` is forwarded to the configured Uniswap V2-compatible router with `recipient = address(this)` (i.e., the `EvmHost` contract), while only `post.fee` / `get.fee` / `amount` worth of `feeToken` is requested as `amountOut`: [1](#0-0) [2](#0-1) [3](#0-2) 

A standard/compatible `swapETHForExactTokens` implementation refunds unused ETH to `msg.sender` of the swap call. Since `EvmHost` itself is the caller of the router (not the original transaction sender), any refund from an over-supplied `msg.value` lands back on the `EvmHost` contract's own balance rather than being returned to the user or app contract that called `dispatch()`/`fundRequest()`. This is confirmed by the project's own router wrapper implementation, which explicitly refunds the unspent ETH to `msg.sender`: [4](#0-3) [5](#0-4) 

None of the three `EvmHost` functions capture, track, or forward this refund back to `_msgSender()`; there is no local variable capturing the router's return value, and no subsequent transfer back to the caller. By contrast, other parts of the codebase (e.g., `IntentGatewayV2`/`ExtrinsicIntents`) explicitly handle this exact scenario by tracking `msgValue` deltas after the swap and refunding the leftover to the caller: [6](#0-5) [7](#0-6) 

`EvmHost` has no equivalent logic for its own `dispatch`/`fundRequest` paths — it neither reverts on overpayment, refunds the change, nor exposes any documented sweep/withdrawal path for this specific accumulated native-token dust (I was not able to locate a `receive()`/`withdraw`/`sweep` function serving this exact purpose in `EvmHost.sol` within the available index, so any such mechanism, if it exists, is not evident from the reachable code).

### Impact Explanation
Any unprivileged caller (a user or an `IApp`/token-bridge/intent contract on top of `EvmHost`) that supplies `msg.value` greater than the amount needed to purchase the exact `fee` in `feeToken` permanently loses the difference — the ETH is swept into the `EvmHost` contract's balance with no code path returning it to the original payer. This is a fund-loss condition for the caller class explicitly in scope (message dispatcher/relayer/token bridger/intent users interacting with `EvmHost.dispatch`), differing from the fully-mitigated intents flows in the same repo, and matches the bug class described in the report except here it manifests as an actual stuck/lost-funds condition rather than merely "no strict check."

### Likelihood Explanation
Likelihood is high in practice: any integrator or user who overestimates the ETH needed for the Uniswap swap (e.g., due to price movement between quoting and execution, or simply sending a safety margin) will trigger this loss on every affected call to `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()`. No malicious actor is required — normal, good-faith overpayment reliably triggers fund loss, unlike the acknowledged low-severity version of this issue in the referenced report where the team asserted frontend/API guarantees exact values (a mitigation that does not exist at the contract level here and cannot be relied upon for permissionless on-chain callers).

### Recommendation
After the `swapETHForExactTokens` call in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the actual ETH spent (via balance delta or the router's return array) and forward any leftover `msg.value` back to `_msgSender()` using a safe ETH transfer, mirroring the pattern already used in `IntentGatewayV2._depositAsset`/`ExtrinsicIntents` fill logic. Alternatively, require `IUniswapV2Router02` calls to be made with `recipient` refund handling explicitly wired to `_msgSender()`, and add a `require`/exact-value check if refund handling is not desired.

### Proof of Concept
1. Caller A (a user or an `IApp` contract) calls `EvmHost.dispatch(DispatchPost)` with `msg.value = X`, where the router only needs `Y < X` ETH to obtain `post.fee` amount of `feeToken`.
2. `EvmHost` forwards the full `X` as `value` to `swapETHForExactTokens{value: X}(post.fee, path, address(this), ...)`.
3. The router spends `Y` ETH and refunds `X - Y` ETH to its caller, which is `EvmHost` (`msg.sender` in the router's context), landing on `EvmHost`'s own balance.
4. `EvmHost.dispatch` completes and returns the commitment; no logic exists to detect or return the `X - Y` leftover to caller A.
5. Caller A has permanently lost `X - Y` ETH with no way to recover it through `EvmHost`'s external interface.

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

**File:** evm/src/utils/uniswapv2/UniV3UniswapV2Wrapper.sol (L143-149)
```text
        if (spent < msg.value) {
            uint256 refund = msg.value - spent;
            IWETH(weth).withdraw(refund);

            (bool success,) = msg.sender.call{value: refund}("");
            if (!success) revert RefundFailed();
        }
```

**File:** evm/src/utils/uniswapv2/UniV4UniswapV2Wrapper.sol (L91-96)
```text
        uint256 refundETH = address(this).balance - balanceBefore;

        if (refundETH > 0) {
            (bool success,) = msg.sender.call{value: refundETH}("");
            require(success, "ETH refund failed");
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L181-217)
```text
            if (solverAmount < totalRequired) revert InvalidInput();

            (uint256 protocolShare, uint256 beneficiaryShare) =
                _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);

            if (token == address(0)) {
                if (msgValue < solverAmount) revert InsufficientNativeToken();
                uint256 beneficiaryTotal = totalRequired + beneficiaryShare;
                _sendValue(beneficiary, beneficiaryTotal);
                msgValue -= (beneficiaryTotal + protocolShare);
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, totalRequired + beneficiaryShare);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }
            if (protocolShare > 0) emit DustCollected(token, protocolShare);
            outputFills[i] = TokenInfo({token: outputToken, amount: totalRequired});
        }

        _execute(order, outputsLen);

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
