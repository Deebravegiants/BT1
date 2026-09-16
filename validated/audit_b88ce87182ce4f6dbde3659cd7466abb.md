### Title
Unauthenticated `CallDispatcher.dispatch` lets anyone drain any residual token/ETH balance left on the shared dispatcher - (File: `sdk/packages/core/contracts/utils/CallDispatcher.sol` / `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes)` is a fully public, unauthenticated function that performs an arbitrary `to.call{value}(data)` for every entry in a caller-supplied `Call[]` array, exactly the pattern flagged in the JOJO report (attacker-controlled target + attacker-controlled calldata executed by a contract that can hold funds). Unlike JOJO's `JOJODealer`, Hyperbridge's `CallDispatcher` is intentionally designed as the "dumb contract" the JOJO report itself recommends using for this purpose, so it does not hold standing token approvals from users. However, it is a single shared, long-lived contract reused across `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution and `IntentGatewayV2`/`IntentsBase` predispatch/postdispatch execution, and `dispatch()` has no access control (no `onlyX` modifier, no check on `msg.sender`). Any ETH or ERC20 balance that is not fully swept back to the calling app after a batch of calls (dust from partial fills, overpaid `Call.value`, tokens outside the sweep's asset list, or a stray direct transfer to the contract's `receive()`) sits in `CallDispatcher` and can be permanently stolen by any unprivileged address simply by calling `dispatch()` directly with a `Call{to: token, data: transfer(attacker, balance)}` (or, for native ETH, `Call{to: attacker, value: balance}`).

### Finding Description
`CallDispatcher.dispatch` decodes an ABI-encoded `Call[]` and executes each call verbatim: [1](#0-0) 

The only check performed is that `to` has code (`extcodesize`); there is no restriction on `msg.sender`, no restriction on `to`, and no restriction on `data`. Anyone can call this function at will, independent of any order/transfer flow.

`CallDispatcher` is shared infrastructure invoked from multiple apps to run "swap-then-escrow"/"fill-then-act" flows:
- `IntentsBase._execute` sends order output tokens to the dispatcher, calls `dispatch`, then sweeps back only the tokens present in `order.output.assets[0:outputsLen]`: [2](#0-1) 

- The HFT/WrappedHFT calldata-execution flow similarly unlocks/mints tokens to the dispatcher and lets it run an ABI-encoded `Call[]`, as documented for both `HyperFungibleToken` and `WrappedHyperFungibleToken`. [3](#0-2) 

Because the sweep logic only iterates over the tokens explicitly declared in the order/transfer's output-asset list (and for native ETH, only if `address(0)` is one of those declared assets), any token or ETH that ends up on the dispatcher outside that declared set - e.g. an overpaid `Call.value`, a partial swap leaving a different intermediate token, or a stray direct ETH send via the dispatcher's `receive()` — is never swept and remains parked on the contract indefinitely. Because `dispatch()` is callable by anyone with any `to`/`data`, the first party to notice such dust can trivially construct a `Call` that transfers it to themselves.

### Impact Explanation
This is a loss-of-funds vector for whatever residual balance accumulates on the shared `CallDispatcher`: any user/solver-supplied predispatch or postdispatch calldata that leaves unswept tokens (intentionally malformed asset lists, rounding, swap slippage, or an accidental direct transfer to the dispatcher) becomes permanently and publicly stealable, since the drain path (`dispatch()`) requires no privilege at all. Because the contract is shared across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken`, dust from any of these apps' flows funnels into the same publicly-drainable pot.

### Likelihood Explanation
Medium-to-High. `dispatch()` genuinely has zero access control, so exploitation requires no special positioning — any address can front-run/observe a residual balance and immediately call `dispatch()` to sweep it out. The remaining question is how often dust accumulates outside the declared sweep set; this depends on solver/user-supplied predispatch/postdispatch `Call[]` payloads (attacker-influenced in the intent-gateway flow) and on swap slippage/overpayment scenarios, both of which are realistic in normal operation of swap-then-escrow/fill-then-act calldata execution.

### Recommendation
- Restrict `CallDispatcher.dispatch` to be callable only by the authorized app contracts that are expected to use it (e.g. `onlyAuthorizedCaller` allow-list of `IntentGatewayV2`/`HyperFungibleToken`/`WrappedHyperFungibleToken` instances), removing the fully public attack surface.
- After each `dispatch` invocation, have the calling app sweep *all* balances the dispatcher could plausibly hold (not just the declared output-asset list), or have `CallDispatcher` itself refuse to retain any balance after a batch completes (revert if `address(this).balance` or tracked token balances are nonzero post-execution, unless explicitly whitelisted as dust).
- Alternatively, deploy a fresh, single-use dispatcher (e.g., via minimal-proxy/`CREATE2` with self-destruct-equivalent cleanup) per call batch so no shared, long-lived contract accumulates cross-flow dust.

### Proof of Concept
1. A solver constructs an `Order` (or HFT `send`) whose postdispatch/calldata `Call[]` swaps output tokens through a DEX but supplies `Call.value` slightly larger than the swap consumes, or whose swap path yields a small amount of an intermediate token not listed in `order.output.assets`.
2. `IntentsBase._execute` (or the HFT/WrappedHFT equivalent) calls `ICallDispatcher(dispatcher).dispatch(order.output.call)`, then sweeps only the tokens declared in `assets`; the leftover ETH/intermediate token remains on `CallDispatcher`.
3. Any unrelated third party observes the nonzero balance on `CallDispatcher` (a public, well-known singleton address) and calls `CallDispatcher.dispatch(abi.encode(calls))` directly with `calls = [Call({to: leftoverToken, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, leftoverBalance)})]` (or `Call({to: attacker, value: address(dispatcher).balance, data: ""})` for ETH).
4. `dispatch()` executes the attacker's call unconditionally (only checking `to` has code), transferring the dust to the attacker with no authorization check.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-62)
```text
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-533)
```text
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

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L160-203)
```text
### Calldata Execution

Pass a non-empty `data` field to execute arbitrary calls on the destination chain after tokens are unlocked. The `data` must be an ABI-encoded `Call[]` array (see [overview](/developers/evm/hyper-fungible-token/overview#calldata-execution) for the full `Call` struct and security details).

When `isWeth = true`, the WrappedHFT unwraps WETH to native ETH on receive. This example bridges WETH back to the home chain, where it's unwrapped to native ETH and swapped for an exact amount of USDC via UniswapV2. The `Call.value` field forwards the native ETH to the router — demonstrating that the `CallDispatcher` can hold and forward native tokens:

```solidity lineNumbers
import {IUniswapV2Router02} from "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";

address[] memory path = new address[](2);
path[0] = WETH;
path[1] = USDC;

Call[] memory calls = new Call[](1);

// Swap native ETH → exact USDC via UniswapV2
// The CallDispatcher holds the unwrapped ETH and forwards it via Call.value
calls[0] = Call({
    to: UNISWAP_V2_ROUTER,
    // forward the native ETH to the router
    value: amount,
    data: abi.encodeWithSelector(
        IUniswapV2Router02.swapETHForExactTokens.selector,
        usdcAmountOut,
        path,
        recipientAddress,
        block.timestamp
    )
});

IHyperFungibleToken(address(wrapper)).send{value: nativeFee}(
    IHyperFungibleToken.SendParams({
        dest: StateMachine.evm(1),
        // unlock to the CallDispatcher so it receives the unwrapped ETH
        to: abi.encodePacked(CALL_DISPATCHER),
        amount: amount,
        timeout: 3600,
        relayerFee: relayerFee,
        data: abi.encode(calls)
    })
);
```

Tokens are unlocked (or unwrapped for WETH) to `to` first, then the `CallDispatcher` executes each call in sequence. Setting `to` to the `CallDispatcher` address ensures the dispatcher holds the tokens (or native ETH) so subsequent calls can spend them via `Call.value` or ERC20 transfers.
```
