## Title
Excess native ETH sent for fee-swap dispatch is refunded to `EvmHost` itself instead of the caller, permanently diverting user funds - ([File: evm/src/core/EvmHost.sol])

### Summary
The original report flags a missing slippage guard (`minAmount`) around value-changing operations (mint/burn amounts computed from a mutable curve) that can move between transaction submission and execution, letting a user unknowingly receive less than expected. `EvmHost`'s native-fee dispatch path has the analogous root cause: it performs a Uniswap V2 **exact-output** swap paying with the caller's full `msg.value`, with no mechanism for the leftover/slippage-buffer ETH to make its way back to the original caller.

### Finding Description
`EvmHost.dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` all follow the same pattern when a user pays fees in native token: [1](#0-0) 

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
    }
    ...
``` [1](#0-0) 

`swapETHForExactTokens` is an exact-output swap: the router computes `amounts[0] <= msg.value` needed to buy exactly `post.fee` of the fee token, and per the standard UniswapV2Router02 implementation it refunds any unspent ETH (`msg.value - amounts[0]`) back to `msg.sender`. Because `EvmHost` itself is the caller of the router (`_msgSender()` on the router call is `address(EvmHost)`), that refund lands in `EvmHost`'s own balance — not the original end user who supplied `msg.value` to `dispatch()`. The same pattern repeats in `dispatch(DispatchGet)` and `fundRequest()`: [2](#0-1) [3](#0-2) 

None of these three functions contain any code to return the swap's leftover native token to `_msgSender()`. The docs explicitly instruct integrators that on-chain `quote()`/`getAmountsIn()` figures are only frontend estimates subject to slippage/sandwiching and that real execution price can differ: [4](#0-3) 

Because callers are told to expect slippage but have no on-chain guard, they routinely must send `msg.value` with a safety buffer above the quoted amount to avoid a revert from `EXCESSIVE_INPUT_AMOUNT` when the price moves between quoting and execution. Any such buffer — as well as any accidental overpayment — is silently captured by `EvmHost` rather than returned to the user. That balance subsequently becomes governance-withdrawable "bridge revenue" via `IHostManager.withdraw(WithdrawParams)`, which can send the native token balance to an arbitrary beneficiary: [5](#0-4) 

This mirrors the report's underlying class of bug: a value-sensitive operation (a price-dependent swap) is executed without giving the caller a way to bound their exposure or reclaim unused funds, so ordinary use of the documented flow (send `msg.value` >= quoted cost) results in a loss that is realized as soon as the swap executes.

### Impact Explanation
Every native-token dispatcher of a POST/GET request or `fundRequest` caller who supplies more native token than the exact amount the swap consumes (which the caller cannot know precisely on-chain, and is told off-chain estimates are imprecise) permanently loses the difference to the `EvmHost` contract, which governance can later withdraw. This is a direct, unprivileged loss of user funds reachable by any unprivileged dispatcher/caller of the `IDispatcher.dispatch` interface — the exact "unprivileged message dispatcher" persona in scope.

### Likelihood Explanation
High likelihood in practice: the documented, recommended flow for native-token payment is to call `dispatch{value: msg.value}(post)` after estimating cost off-chain via `quote()`/`getAmountsIn`, which the docs themselves warn is only approximate and subject to slippage. Any user following this guidance who pads their `msg.value` for safety, or whose transaction executes at a slightly different price than quoted, loses the unspent remainder on every single dispatch call.

### Recommendation
Track and refund unspent native token to `_msgSender()` (not `address(this)`) after the Uniswap swap in `dispatch(DispatchPost)`, `dispatch(DispatchGet)`, and `fundRequest()` — mirroring the pattern already used in `IntentGatewayV2.placeOrder`, which computes `msgValue -= amounts[0]` and explicitly refunds the remainder to the caller: [6](#0-5) 

### Proof of Concept
1. Alice calls `EvmHost.dispatch{value: X}(post)` where `X` is `quote()`'s off-chain estimate plus a small buffer to tolerate slippage.
2. `swapETHForExactTokens{value: X}(post.fee, path, address(this), block.timestamp)` executes, spending `amounts[0] < X` and the UniswapV2Router refunds `X - amounts[0]` to `msg.sender`, which is `EvmHost`.
3. `EvmHost` never forwards this refund to Alice; her transaction succeeds but she has permanently paid `X - amounts[0]` more than required, with no mechanism in `dispatch()` to reclaim it.
4. Repeated over many dispatches, this ETH accumulates in `EvmHost` and can be swept out via `IHostManager.withdraw(WithdrawParams)` to any beneficiary the host manager designates.

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

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L236-249)
```text
<Callout type="warning" title="Estimate Fees Off-Chain">
Use the `quote()` view function from your frontend to estimate how much native token users need to send. **Do not call `quote()` in smart contract transactions.** It uses Uniswap's `getAmountsIn`, making it vulnerable to sandwich attacks. Only use it off-chain for frontend fee estimation
</Callout>

### Payment Method Comparison

| Feature | Native Token | FeeToken (Recommended) |
|---------|-------------|------------------------|
| **Gas Cost** | Higher (includes swap) | Lower (no swap) |
| **Slippage** | Yes (Uniswap swap) | No |
| **Fee Calculation** | Approximate (subject to slippage) | Exact |
| **Token Approval** | Not required | Required  |
| **User Convenience** | High (users have native tokens) | Low (users need feeToken) |
| **Best For** | One-off transactions, user-facing apps | Frequent dispatches, cost optimization |
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
