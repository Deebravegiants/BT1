### Title
Fee Escrow Swap Uses `block.timestamp` as Deadline, Enabling MEV/Sandwich Attacks on `placeOrder` - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
When a user calls `placeOrder` and pays the protocol fee in native token, `IntentGatewayV2` swaps ETH for the exact fee-token amount via `IUniswapV2Router02.swapETHForExactTokens`, passing `block.timestamp` as the `deadline` parameter, mirroring the exact bug class described in the external report (deadline set to `block.timestamp` in a Uniswap swap params struct).

### Finding Description
In the fee-escrow branch of order placement, the contract builds a WETH→feeToken path and calls the router with `deadline: block.timestamp`: [1](#0-0) 

Because `block.timestamp` is evaluated at the time the transaction is *executed* (whichever block it ends up in), not at the time it is *submitted*, this "deadline" imposes no actual constraint — the Uniswap router's `ensure(deadline)` modifier will always pass regardless of how long the transaction sits in the mempool. This is functionally identical to having no deadline at all, exactly as described in the external report for `VaultkaV2GMXHandler.afterWithdrawalExecution`.

This code path is reachable by any unprivileged user submitting a `placeOrder(order, graffiti)` call with `order.fees > 0` and native-token `msg.value` supplied for the fee — no special privileges are required, and the escrow-fee swap parameters (`order.fees` exact-out amount) are fully attacker/user influenced in terms of timing.

The same pattern (fee-swap call with hard-coded `block.timestamp` deadline) also appears to exist for the EVM (non-Tron) `IntentGatewayV2` app logic, referenced in `evm/src/apps/IntentGatewayV2.sol`, though the exact call site there is inherited from `IntrinsicIntents`/`ExtrinsicIntents` base contracts and could not be fully traced within the available index. [2](#0-1) 

### Impact Explanation
An attacker/MEV bot monitoring the mempool can hold or delay inclusion of the `placeOrder` transaction (or bundle it favorably) and manipulate the WETH/feeToken pool price immediately before execution (a classic sandwich attack), since the "deadline" never actually expires. Because this is an exact-output swap (`swapETHForExactTokens`) with `amountInMaximum` effectively bounded only by `msg.value`, the user can be forced to pay a maximal, manipulated ETH price for the fixed `order.fees` amount of fee tokens, resulting in direct value extraction from the user placing the order. This is a fund-loss issue reachable from a standard user-facing entry point (`placeOrder`), fitting the medium-severity classification of the original report.

### Likelihood Explanation
Likelihood is moderate-to-high: any order with `order.fees > 0` paid in native token triggers this swap, and MEV searchers actively monitor mempools for exact-output Uniswap V2 swaps with sandwichable "no-deadline" params. No special permissions or preconditions beyond a normal `placeOrder` call with a native-token fee payment are needed.

### Recommendation
Do not hard-code `deadline: block.timestamp` for on-chain execution. Either:
- Accept a caller-supplied `deadline` parameter as part of the `Order`/fee-payment structure that is verified against `block.timestamp` at submission-time expectations (i.e., a real future deadline the user opted into), or
- Remove the exact-out swap-with-slippage risk entirely by requiring pre-approved fee-token payment instead of on-chain ETH swaps, or
- At minimum, add a maximum-age deadline (e.g., `block.timestamp + MAX_SWAP_WINDOW`) with a corresponding `amountInMaximum`/slippage bound explicitly supplied and validated by the user, so the "deadline" provides genuine protection against delayed execution and sandwiching.

### Proof of Concept
1. User calls `placeOrder` with `order.fees = X` and sends `msg.value` covering `X` fee tokens' worth of ETH.
2. Contract computes `path = [WETH, feeToken]` and calls `swapETHForExactTokens{value: msgValue}(order.fees, path, address(this), block.timestamp)`. [3](#0-2) 
3. An MEV bot observes this pending transaction, front-runs it by buying feeToken (raising its ETH price), lets the victim's exact-output swap execute at the inflated price (paying more ETH than fair value, up to `msgValue`), then back-runs by selling feeToken back — extracting the price difference from the user.
4. Because `deadline = block.timestamp` is satisfied trivially whenever the transaction is mined, there is no time-based protection preventing the transaction from being deliberately delayed or reordered around the attacker's sandwich transactions.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L471-488)
```text
        if (order.fees > 0) {
            // escrow fees
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = IDispatcher(hostAddr).feeToken();
                IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L17-19)
```text
import {IntentsBase} from "./intentsv2/IntentsBase.sol";
import {IntrinsicIntents} from "./intentsv2/IntrinsicIntents.sol";
import {ExtrinsicIntents} from "./intentsv2/ExtrinsicIntents.sol";
```
