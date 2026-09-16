## Analog Found

### Title
Unrefunded native-token overpayment permanently traps user funds in `EvmHost` fee-swap paths, exploitable via sandwich-inflated pricing - ([File: evm/src/core/EvmHost.sol])

### Summary
The Hypervisor report flags `pool.swap`/`pool.mint`/`pool.burn` calls that lack slippage/minimum-output protection, letting a sandwicher manipulate the amount of tokens a caller ends up with. `EvmHost.sol` contains the same class of unprotected AMM interaction, but the exploitable consequence is worse: the contract never returns unspent native ETH after the internal `swapETHForExactTokens` call, so any ETH not consumed by the swap is permanently stranded in the contract, and a sandwich attacker can maximize how much of a user's overpayment gets trapped.

### Finding Description
`EvmHost.dispatch(DispatchPost)`, `EvmHost.dispatch(DispatchGet)`, and `EvmHost.fundRequest()` are unprivileged, directly reachable entry points that accept `msg.value` and swap it for the protocol's `feeToken` via UniswapV2: [1](#0-0) [2](#0-1) [3](#0-2) 

In all three functions, `swapETHForExactTokens{value: msg.value}(fee, path, address(this), block.timestamp)` is called with the *entire* `msg.value` as the maximum spend, but:
1. The return value (`amounts`, containing the actual ETH spent) is **discarded** — it is never captured into a local variable.
2. There is **no subsequent refund** of unspent ETH to `_msgSender()`. Unlike UniswapV2Router which refunds excess ETH to the caller of the swap (i.e., to `EvmHost` itself, since `EvmHost` is `msg.sender` of the router call), `EvmHost` has no code path (`_sendValue`, `.call{value:}`, etc.) to forward that refund onward to the actual user.

This is confirmed by comparison with the sibling contract `IntentGatewayV2.sol`, which performs the identical swap pattern but explicitly captures the swap output and refunds the remainder to the caller: [4](#0-3) 

and which has a dedicated regression test proving the refund behaviour, `testPlaceOrder_FeeSwap_RefundsExcessNativeToken`: [5](#0-4) 

No equivalent test or refund logic exists for `EvmHost.dispatch`/`fundRequest`, and no `_sendValue`/refund call exists anywhere in `EvmHost.sol`.

Because `swapETHForExactTokens` computes the required ETH input from the live UniswapV2 reserves at execution time (no `amountInMaximum` slippage cap other than the full `msg.value`), a sandwicher can front-run the user's `dispatch`/`fundRequest` transaction with a buy that shifts the ETH/feeToken price upward, forcing the swap to consume more of the user's `msg.value` than expected (any legitimate user typically over-provisions `msg.value` to survive normal price movement). Whatever ETH is left over after the swap — whether from normal caller headroom or from the attacker's engineered price shift — is silently absorbed by the `EvmHost` contract with no mechanism for the original sender to reclaim it.

### Impact Explanation
Every unprivileged caller of `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, or `fundRequest()` who pays with native ETH is at risk of permanently losing the unspent portion of their `msg.value`. This is a direct, permanent freezing/loss of user funds triggered by a normal user-submitted dispatch transaction — squarely in scope as it is reachable by any message dispatcher/relayer/user interacting with `EvmHost`, the central ISMP dispatch contract. A sandwiching attacker amplifies the loss by manipulating the AMM price immediately before the victim's transaction, maximizing the ETH input consumed by the swap and therefore minimizing/eliminating any residual the victim might otherwise retain, while the true beneficiary of the "stuck" funds is whoever eventually controls or can sweep `EvmHost`'s ETH balance (or the funds are simply unrecoverable). This meets the "permanent freezing of funds" bar from the validation criteria.

### Likelihood Explanation
High. This does not require any privileged role — any user calling `dispatch()`/`fundRequest()` with `msg.value` greater than the exact fee-token cost (a very common and even encouraged practice to tolerate price movement, gas estimation slack, or convenience of round-number payments) triggers fund loss. A sandwicher only needs to observe a pending transaction in the mempool and place a buy order on the same UniswapV2 pool beforehand — standard, well-tooled MEV behavior — to inflate the ETH actually consumed by the exact-output swap, deepening the loss for any given `msg.value`.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()`, capture the `amounts` array returned by `swapETHForExactTokens` and refund `msg.value - amounts[0]` back to `_msgSender()`, mirroring the pattern already implemented in `IntentGatewayV2.sol`. Additionally, consider adding a caller-supplied `amountInMaximum` (rather than implicitly using the whole `msg.value`) to give users explicit slippage control against sandwich manipulation of the swap price.

### Proof of Concept
1. Attacker monitors the mempool for a `EvmHost.dispatch(DispatchPost)` (or `fundRequest`) call sent with `msg.value` set generously above the current quoted ETH cost of `post.fee` fee-tokens (a normal user pattern to tolerate price drift).
2. Attacker front-runs with a buy order on the WETH/feeToken UniswapV2 pool configured in `_hostParams.uniswapV2`, pushing the ETH price of the fee token up.
3. The victim's transaction executes `swapETHForExactTokens{value: msg.value}(post.fee, path, address(this), block.timestamp)`; due to the inflated price, the swap consumes more ETH from `msg.value` than it would have absent manipulation, and the router refunds only the small remainder to `EvmHost` itself.
4. `EvmHost.dispatch` never forwards this remainder to the victim — it is permanently retained by the contract with no user-facing withdrawal path, and no test in the suite (`evm/tests/foundry/*`) verifies or exercises a refund for these three `EvmHost` functions, unlike the equivalent, tested code path in `IntentGatewayV2.placeOrder`.
5. Attacker back-runs with a sell to restore the pool price, pocketing the sandwich profit; the victim's excess ETH remains stuck in `EvmHost`.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L383-397)
```text
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3750)
```text
    /// @notice placeOrder with fee swap refunds unused ETH after swapETHForExactTokens.
    function testPlaceOrder_FeeSwap_RefundsExcessNativeToken() public {
        uint256 inputAmount = 1000 * 1e6;
        uint256 feeAmount = 1 * 1e18; // 1 DAI worth of fees

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(usdc)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 1000 * 1e18});

        PaymentInfo memory output =
            PaymentInfo({beneficiary: bytes32(uint256(uint160(user))), assets: outputAssets, call: ""});

        Order memory order = Order({
            user: bytes32(0),
            source: "",
            destination: host.host(),
            deadline: block.number + 1000,
            nonce: 0,
            fees: feeAmount,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        uint256 userEthBefore = user.balance;

        vm.startPrank(user);
        usdc.approve(address(intentGateway), inputAmount);
        // Send 5 ETH for a fee swap that should cost much less
        intentGateway.placeOrder{value: 5 ether}(order, bytes32(0));
        vm.stopPrank();

        // User should get back most of the 5 ETH — the swap only needed a tiny fraction
        uint256 ethSpent = userEthBefore - user.balance;
        assertTrue(ethSpent < 1 ether, "User should have been refunded most of the 5 ETH");
```
