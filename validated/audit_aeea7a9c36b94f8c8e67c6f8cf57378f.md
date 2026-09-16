## Analog Found: Unrestricted `CallDispatcher.dispatch()` allows theft of any value/token balance stranded at the dispatcher after HyperFungibleToken/WrappedHyperFungibleToken calldata execution

### Title
Permissionless `CallDispatcher.dispatch()` lets anyone drain residual value/tokens left at the shared dispatcher after token-bridge calldata execution - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The Pickle Finance report flags an "uncontrolled call of functions of another contract on behalf of this contract," reachable by any unprivileged party, where `_target`/`_data` are attacker-controlled and the call is made with the contract's own held value. The direct analog in Hyperbridge is `CallDispatcher.dispatch()`, a permissionless function used by `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` to execute attacker/user-supplied `Call[]` (arbitrary `to`, `value`, `data`) forwarding the dispatcher's own held funds.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` has no access control whatsoever - any address can call it directly: [1](#0-0) 

It is a single, canonical, shared contract address reused across the whole protocol - `HyperFungibleTokenUpgradeable`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` all route bridged/escrowed value through it as `to`/`_dispatcher` and then invoke `dispatch()` with user-supplied `data`.

For the token-bridge apps, an incoming cross-chain message's `data` field is attacker-controlled (set by *any* sender on the source chain calling `send()`), and is forwarded verbatim to the shared dispatcher: [2](#0-1) 

Unlike `IntentGatewayV2`/`IntentsBase._execute`, which explicitly builds sweep calls to return any residual dispatcher balance back to the gateway after executing calldata: [3](#0-2) 

`WrappedHyperFungibleToken.onAccept` and `HyperFungibleTokenUpgradeable.onAccept` perform **no such sweep** - they simply call `ICallDispatcher(_dispatcher).dispatch(message.data)` and return: [4](#0-3) 

The documented composability pattern explicitly encourages routing `Call.value` through routers that can leave a refund at the caller (the dispatcher itself), e.g. `swapETHForExactTokens`, which by design refunds unused ETH to `msg.sender` (the `CallDispatcher`, since it is the one making the call): [5](#0-4) 

Because `dispatch()` is unrestricted, any residual native ETH/token balance that ends up parked at the dispatcher - from a Uniswap refund, slippage, an under-consuming calldata payload, or a stray direct transfer to the well-known dispatcher address - is not exclusively swept back by the app that produced it. Any third party can simply call `CallDispatcher.dispatch()` directly with `Call({to: attacker, value: strandedBalance, data: ""})` (or an ERC20 `transfer` call for token dust) and take it, since nothing about `dispatch()` restricts the caller or the `to`/`data` it is given.

### Impact Explanation
This is a permanent-freezing/theft-of-funds bug: value legitimately bridged for a user (native ETH or ERC-20 output of an on-chain swap triggered by the bridge's own documented "Calldata Execution" feature) can be permanently diverted to any opportunistic caller rather than reaching the intended beneficiary or being recovered by the protocol, because the one contract responsible for holding it in transit (`CallDispatcher`) enforces no access control over who may spend its balance. This is medium/high severity depending on frequency of triggering conditions (slippage-based refunds, under-specified swaps), but is concretely reachable by an unprivileged token bridger simply by using the bridge's advertised feature.

### Likelihood Explanation
Likelihood is moderate: it requires a calldata-execution payload (via `HyperFungibleToken`/`WrappedHyperFungibleToken` `send()` with non-empty `data`, or an `IntentGatewayV2` predispatch/postdispatch call) whose target call leaves value at the dispatcher (e.g. any exact-output swap, a call that doesn't consume its full `msg.value`/allowance, or accidental direct transfers to the dispatcher's well-known address), and a third-party racing to call `dispatch()` before any (non-existent, for the token-bridge apps) sweep occurs. Given `dispatch()` is fully public and the dispatcher address is published in the "contract addresses" docs, an MEV searcher merely needs to watch pending/mined transactions and front-run/immediately follow with a sweeping call.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to a set of authorized callers (e.g. an `onlyAuthorized` allow-list of the HFT/WrappedHFT/IntentGateway contracts), removing the fully permissionless surface.
- Deploy a fresh, single-use `CallDispatcher` (or use a deterministic per-call ephemeral context, e.g. via `CREATE2`/`delegatecall` scoping) per invocation instead of relying on one shared, long-lived contract holding transient balances.
- Add an explicit balance-sweep step after every `dispatch()` invocation in `HyperFungibleTokenUpgradeable.onAccept` and `WrappedHyperFungibleToken.onAccept`, mirroring `IntentsBase._execute`'s dust-collection pattern, so no native/token balance is ever left resident at the dispatcher between calls.

### Proof of Concept
1. A token bridger calls `WrappedHyperFungibleToken.send()` on chain A with `to = CALL_DISPATCHER` and `data` encoding a `Call[]` that calls `UniswapV2Router02.swapETHForExactTokens(...)` with a `Call.value` deliberately larger than what the swap will consume (or simply relying on normal slippage tolerance).
2. On chain B, a relayer delivers the message; `WrappedHyperFungibleToken.onAccept` unwraps/unlocks the bridged asset to `CALL_DISPATCHER` and calls `ICallDispatcher(_dispatcher).dispatch(message.data)`.
3. `UniswapV2Router02.swapETHForExactTokens` refunds unused ETH to `msg.sender`, i.e. back to `CallDispatcher`, since the router treats `CallDispatcher` as the caller.
4. `onAccept` returns without sweeping the dispatcher's residual ETH balance (no such step exists, unlike `IntentsBase._execute`).
5. Any unrelated address (attacker/MEV bot) calls `CallDispatcher.dispatch(abi.encode([Call({to: attacker, value: address(dispatcher).balance, data: ""})]))` directly, draining the stranded ETH that belonged to the original bridging user.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-61)
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
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L309-328)
```text
        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-545)
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

        if (sweepCount > 0) {
            Call[] memory finalCalls = new Call[](sweepCount);
            for (uint256 i; i < sweepCount;) {
                finalCalls[i] = sweepCalls[i];
                unchecked {
                    ++i;
                }
            }
            ICallDispatcher(dispatcher).dispatch(abi.encode(finalCalls));
        }
    }
```

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L164-201)
```text
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
```
