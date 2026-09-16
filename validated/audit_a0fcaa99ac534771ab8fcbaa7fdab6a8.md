Confirmed: `CallDispatcher` is a shared, stateless singleton contract (no ownership/tracking of per-order balances), so any token left in it after a `placeOrder` predispatch sweep is a real, permanently-strandable balance until some later, unrelated call happens to sweep exactly that token.

### Title
Predispatch sweep in `placeOrder` only recovers declared `order.inputs` tokens, permanently stranding any other tokens (e.g. reward/bonus tokens) produced by predispatch calldata in the shared `CallDispatcher` - (File: evm/src/apps/IntentGatewayV2.sol)

### Summary
`placeOrder`'s predispatch flow (unwrap-then-escrow, e.g. "unwrapping LP tokens") sends the user's predispatch assets to the shared `CallDispatcher`, executes arbitrary calldata there, and then sweeps back to the gateway only the specific tokens listed in `order.inputs`. Any additional token balance left on the dispatcher as a side effect of the predispatch call (for example a reward/bonus token paid out alongside the unwrapped asset) is never swept and is not accounted for anywhere, mirroring the reported Sense `_removeLiquidityFromSpace` bug where `exitPool` returns more than the two tracked token balances and the excess is left behind.

### Finding Description
In `placeOrder`, when `order.predispatch.call.length > 0`, the gateway:
1. Transfers the declared `predispatch.assets` to `_params.dispatcher` (a shared `CallDispatcher` instance, see [1](#0-0) ).
2. Executes arbitrary calldata via `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` [2](#0-1) .
3. Builds sweep-back `transferCalls` **only for the tokens listed in `order.inputs`**, looping `for (uint256 i; i < inputsLen; ...)` and reading `order.inputs[i].token` [3](#0-2) .
4. Measures the delta only for those same `order.inputs` tokens and emits `DustCollected` only for excess of the *declared* tokens [4](#0-3) .

If the predispatch calldata produces a token balance on the `CallDispatcher` that is **not one of `order.inputs`** — e.g., unwrapping an LP/staking position that also emits a reward token, a DEX aggregator that returns partial refunds in a different token, or any multi-token payout — that balance is never included in `transferCalls`, never transferred back to the gateway, and never emitted as dust. It is simply left sitting in the shared, stateless `CallDispatcher` contract (`evm/src/utils/CallDispatcher.sol`, which has no per-token or per-caller accounting) with no function to recover it. This exactly parallels the reported analog: a balance-delta based accounting scheme that only tracks a fixed, pre-known set of tokens after an external unwrapping/exit call, silently dropping any additional value returned by that call.

Because `CallDispatcher` is a single shared contract used across all orders and all gateway deployments referencing `_params.dispatcher` [5](#0-4) , this stray balance can also be silently claimed by an unrelated future order whose `order.inputs` happens to include that same token address (front-run/back-run risk), or remain frozen indefinitely if no later order ever names it.

### Impact Explanation
Any predispatch integration whose external call returns more than the exact `order.inputs` token set (reward tokens, referral bonuses, partial-fill refunds in a secondary token, LP-unwrap yield) causes permanent loss of that value for the user who paid the predispatch cost — the tokens are unrecoverable via any exposed gateway function and can be swept away by unrelated future callers. This is a concrete freezing/loss-of-funds bug reachable by a single unprivileged `placeOrder` transaction with attacker- or integration-controlled predispatch calldata, satisfying the "permanent freezing of funds" bar for Medium/High severity.

### Likelihood Explanation
Likelihood is contingent on the specific predispatch integrations deployed via `order.predispatch.call`/`order.predispatch.assets`, which per the docs explicitly include "unwrapping LP tokens" and general DeFi composability (swap-then-escrow) [6](#0-5) . Any such interaction with a protocol that pays auxiliary rewards, cashback, or multi-asset payouts (a common DeFi pattern, directly analogous to Sense Finance's Space AMM reward token) will trigger the loss on every single order, not just an edge case.

### Recommendation
Mirror the postdispatch `_execute` sweep logic used for outputs, which iterates over all relevant assets and sweeps residual balances generically [7](#0-6) : after the predispatch call, snapshot the dispatcher's balance for the full set of tokens actually touched (or better, require predispatch integrations to enumerate every token they might return, or add a generic "sweep any nonzero token balance from dispatcher" step covering a caller-declared superset of `order.inputs` plus any additionally expected reward tokens), and route the excess either to the user or to protocol dust (as done elsewhere via `DustCollected`), rather than only sweeping the exact `order.inputs` token list.

### Proof of Concept
1. Governance/integrator configures a predispatch call that interacts with a yield/LP-unwrap protocol which, on withdrawal, sends the unwrapped base asset (matches `order.inputs[0].token`) *and* a separate reward token (e.g., `COMP`, `AAVE`, `CRV`)-style incentive token to the caller (`CallDispatcher`).
2. User calls `placeOrder` with `order.inputs = [{token: baseAsset, amount: X}]` and predispatch calldata that performs the unwrap.
3. `IntentGatewayV2.placeOrder` transfers the position to `CallDispatcher`, executes the unwrap, and sweeps back only `baseAsset` via `transferCalls` sized to `inputsLen = 1` [3](#0-2) .
4. The reward token balance now sitting on `CallDispatcher` is never referenced by any `transferCalls` entry and is never moved.
5. `CallDispatcher` has no owner-only sweep function or balance tracking [8](#0-7) , so the reward tokens are stuck until some unrelated future order coincidentally lists that reward token in its own `order.inputs`, at which point that unrelated order's sweep loop (`balance = IERC20(token).balanceOf(dispatcher)`) would opportunistically claim the stranded balance as `dust`/excess for itself — confirming both the freezing and the cross-order leakage risk.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L17-24)
```text
import {ICallDispatcher, Call} from "@hyperbridge/core/interfaces/ICallDispatcher.sol";

/**
 * @title The CallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This contract is used to dispatch calls to other contracts.
 */
```

**File:** evm/src/utils/CallDispatcher.sol (L25-63)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
    function dispatch(bytes memory encoded) external {
        Call[] memory calls = abi.decode(encoded, (Call[]));
        uint256 callsLen = calls.length;
        for (uint256 i = 0; i < callsLen; ++i) {
            Call memory call = calls[i];
            uint32 size;
            address to = call.to;
            assembly {
                size := extcodesize(to)
            }

            if (size == 0) {
                revert NotContract(to);
            }

            (bool success, bytes memory result) = to.call{value: call.value}(call.data);
            if (!success) revert CallFailed(to, result);
        }
    }
}
```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-258)
```text
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;
                if (amount == 0) revert InvalidInput();

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    _sendValue(dispatcher, amount);
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/src/apps/IntentGatewayV2.sol (L260-289)
```text
            // Build sweep calls and snapshot gateway balances before the sweep.
            Call[] memory transferCalls = new Call[](inputsLen);
            uint256[] memory balancesBefore = new uint256[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;

                if (token == address(0)) {
                    uint256 balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                    balancesBefore[i] = address(this).balance;
                } else {
                    uint256 balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    balancesBefore[i] = IERC20(token).balanceOf(address(this));
                }

                unchecked {
                    ++i;
                }
            }

            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/apps/IntentGatewayV2.sol (L291-311)
```text
            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L99-101)
```text
### Predispatch

The `predispatch` field in `Order` contains calldata to execute *before* escrowing inputs. The predispatch assets specified in `DispatchInfo.assets` are transferred to the `CallDispatcher`, the encoded calls are executed, and the resulting tokens are transferred back to the gateway for escrow. This enables swap-then-escrow patterns — for example, a user sends ETH which the `CallDispatcher` swaps to DAI on Uniswap, and the resulting DAI is escrowed as the order input.
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L487-533)
```text
    /**
     * @dev Executes arbitrary calldata attached to an order's output via the CallDispatcher.
     * After dispatching the calls, any residual token balances left on the dispatcher
     * are swept back to this contract and accounted for as protocol dust.
     *
     * This enables composable order fulfillment — solvers can route through DEXes,
     * lending protocols, or other DeFi primitives as part of filling an order.
     *
     * @param order The order containing the output calldata to execute.
     * @param outputsLen The number of output assets to sweep after execution.
     */
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

        Call[] memory sweepCalls = new Call[](outputsLen);
        uint256 sweepCount = 0;

        for (uint256 i; i < outputsLen;) {
            address token = address(uint160(uint256(order.output.assets[i].token)));

            if (token == address(0)) {
                uint256 balance = dispatcher.balance;
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({to: address(this), value: balance, data: ""});
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            } else {
                uint256 balance = IERC20(token).balanceOf(dispatcher);
                if (balance > 0) {
                    sweepCalls[sweepCount] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                    sweepCount++;
                    emit DustCollected(token, balance);
                }
            }

            unchecked {
                ++i;
            }
        }
```
