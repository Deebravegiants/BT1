### Title
Excess ETH sent to `EvmHost.dispatch(DispatchPost)`/`dispatch(DispatchGet)`/`fundRequest` is refunded to the Host contract instead of the caller, permanently trapping user overpayment - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest` accept native token payment and swap it for the exact fee-token amount needed via Uniswap V2's `swapETHForExactTokens`. Uniswap's router refunds any unspent ETH to `msg.sender` of the swap call — but that caller is `EvmHost` itself, not the original transaction sender. Any ETH sent above the exact quoted amount is therefore not returned to the user/app who called `dispatch`; it is stranded in the `EvmHost` contract's balance.

### Finding Description
In `dispatch(DispatchPost)`:
```solidity
if (msg.value > 0) {
    address[] memory path = new address[](2);
    address uniswapV2 = _hostParams.uniswapV2;
    path[0] = IUniswapV2Router02(uniswapV2).WETH();
    path[1] = feeToken();
    IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
        post.fee, path, address(this), block.timestamp
    );
}
``` [1](#0-0) 

The same pattern recurs in `dispatch(DispatchGet)` and `fundRequest`: [2](#0-1) [3](#0-2) 

Uniswap V2's `swapETHForExactTokens` implementation refunds any leftover ETH (i.e., `msg.value - amountIn`) back to `msg.sender` — but from the router's perspective, the caller of this function is `EvmHost`, since `EvmHost` itself invokes the router with `{value: msg.value}`. This means overpaid ETH sent by a user/app calling `dispatch{value: msg.value}(post)` is refunded by Uniswap into `EvmHost`'s own balance, not back to the transaction's originating `msg.sender`.

This is confirmed by contrast with the pattern used correctly elsewhere in the codebase: `IntentGatewayV2` and `ExtrinsicIntents` explicitly capture the `amounts[0]` actually spent by the swap and manually refund the remainder to the original caller:
```solidity
uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
    order.fees, path, address(this), block.timestamp
);
msgValue -= amounts[0];
...
if (msgValue > 0) {
    _sendValue(msg.sender, msgValue);
}
``` [4](#0-3) [5](#0-4) 

`EvmHost.dispatch`/`fundRequest` do not perform this same explicit refund step; they rely (incorrectly) on Uniswap's automatic refund reaching the true caller, which it does not.

There is no publicly documented function on `EvmHost` for reclaiming trapped native ETH balance by ordinary users; the only withdrawal path (`IHostManager.withdraw`) is restricted to the privileged `hostManager` and disburses "bridge revenue," not user overpayments [6](#0-5) .

### Impact Explanation
Any unprivileged app/user dispatching a POST or GET request with native token payment (the exact reachable path documented for `IDispatcher.dispatch{value: msg.value}(post)`) that sends slightly more ETH than the exact quoted swap amount permanently loses the excess — it accumulates in `EvmHost`'s balance and is not recoverable by the sender. Given ETH price volatility between quote time and execution, and the fact that developers are told to "estimate fees on the client side" (inherently imprecise) [7](#0-6) , overpayment is a realistic and expected occurrence for every native-token dispatch. This is a direct loss of user funds with no recovery mechanism, matching a Medium-severity fund-loss class.

### Likelihood Explanation
High likelihood of occurrence: the native-token dispatch path is a first-class, documented feature (`dispatchWithNative`/`sendMessageWithNative` patterns) [8](#0-7) , reachable directly by any unprivileged caller with a single transaction. Since exact ETH pricing at the moment of the swap can't be known precisely in advance by callers, sending a safety margin above the estimated fee is standard practice, guaranteeing repeated small losses.

### Recommendation
In `EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest`, capture the `amounts[0]` returned by `swapETHForExactTokens` and explicitly refund `msg.value - amounts[0]` to `_msgSender()` (mirroring the pattern already used correctly in `IntentGatewayV2` and `ExtrinsicIntents`).

### Proof of Concept
1. A user's app calls `EvmHost.dispatch{value: 5 ether}(post)` with `post.fee` requiring only a small fraction of fee-token, expecting only the necessary ETH to be spent (as advertised: "Will revert if enough native tokens are not provided" implies excess should be safe/refunded, matching behavior in `IntentGatewayV2.placeOrder` tests) [9](#0-8) .
2. Inside `dispatch`, `swapETHForExactTokens{value: 5 ether}(post.fee, path, address(this), block.timestamp)` executes; Uniswap V2 router computes `amountIn < 5 ether` and refunds the difference to `msg.sender` of the swap call, which is `EvmHost`.
3. `EvmHost`'s ETH balance increases by the refunded amount; the original caller's balance decreases by the full 5 ether (minus gas), with no logic in `dispatch` to forward the difference back to them.
4. No public/unprivileged function exists on `EvmHost` to reclaim this stranded balance; it is either permanently locked or claimable only via the privileged `hostManager.withdraw` path, which was never designed to compensate the user for their lost overpayment.

### Citations

**File:** evm/src/core/EvmHost.sol (L81-96)
```text
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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L162-189)
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
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L190-201)
```text
### Estimating Fees

When building user-facing applications, estimate fees on the client side before users submit transactions:

```typescript lineNumbers title="client.ts" icon="typescript"
import { createPublicClient, http, parseEther } from 'viem'
import { mainnet } from 'viem/chains'

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http()
})
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3713-3752)
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
        assertTrue(ethSpent > 0, "User should have spent some ETH on the fee swap");
    }
```
