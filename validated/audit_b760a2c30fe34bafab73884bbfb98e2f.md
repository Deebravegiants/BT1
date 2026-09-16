## Finding

### Title
Unprotected `CallDispatcher.dispatch()` allows any caller to drain tokens/ETH resident in the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is a fully public, unauthenticated entry point with no restriction on the caller and no restriction on the function selector or target of the encoded `Call[]` it executes. It is a canonical, shared singleton reused across `IntentGatewayV2` (predispatch/postdispatch flows) and `HyperFungibleToken`/`WrappedHyperFungibleToken` (calldata-execution on receive). Any address that ever comes to rest in this shared contract — dust, unconsumed swap residue, or an accidental transfer — can be swept out by any third party simply by calling `dispatch()` themselves.

### Finding Description
`dispatch()` has no access-control modifier at all: [1](#0-0) 

It decodes an arbitrary `Call[]` and, for each entry, performs `to.call{value: call.value}(call.data)` with the `CallDispatcher` itself as `msg.sender` in the downstream call — the only check is that `to` has code (`extcodesize`). There is no check on `msg.sender` of `dispatch()`, and no restriction on which function selector is invoked on `to`. This is precisely the pattern described in the reference report: an unprotected call to a custom/target contract with no function-selector validation, letting an attacker instruct the privileged caller (here, the dispatcher itself) to invoke arbitrary functions such as `transfer`/`transferFrom` on any asset the dispatcher happens to hold.

The dispatcher is a single shared deployment reused by all callers and apps rather than per-order/per-message:
- `IntentGatewayV2`/`IntentsBase` reference one dispatcher address for all users' predispatch and postdispatch calls, transiently routing user tokens through it: [2](#0-1) 
- `HyperFungibleToken`/`WrappedHyperFungibleToken` mint or unlock bridged tokens directly to the dispatcher address and then forward arbitrary attacker/sender-supplied calldata to it, with no sweep-back step afterward: [3](#0-2) 
- The `IntentsBase._execute` sweep only recovers the balances of tokens explicitly listed in `order.output.assets`, using the dispatcher's *entire current balance* of each listed token — any token (or ETH) not in that list, or left over from unconsumed swaps/approvals/rounding, is never swept and remains resident indefinitely: [4](#0-3) 

Because the dispatcher is shared and its `dispatch()` function is callable by anyone, any balance that is not perfectly swept back in the same atomic transaction (dust from Uniswap slippage/fees in HFT calldata swaps, accidental transfers, reward tokens from DeFi interactions triggered by calldata, or ETH sent via the `receive()` fallback) becomes permanently exploitable: an attacker simply calls `CallDispatcher.dispatch()` with a `Call` targeting that token/ETH, e.g. `IERC20(token).transfer(attacker, IERC20(token).balanceOf(dispatcher))`, executed as the dispatcher itself, moving the funds straight to the attacker.

### Impact Explanation
Any token or native-asset balance temporarily or permanently resident in the shared `CallDispatcher` — arising from normal usage across `IntentGatewayV2` predispatch/postdispatch flows and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-on-receive flows — can be stolen outright by any unprivileged third party. This is concrete theft of user/protocol funds (dust, unconsumed swap remainders, accidentally-sent assets) with no privileged position required by the attacker, satisfying the High-severity bar for unprotected calls to custom/target contracts.

### Likelihood Explanation
High. Exploitation requires only a single unauthenticated call to a public function (`dispatch`) with attacker-chosen `Call[]` data; no whitelist, signature, or state precondition gates it. The dispatcher's documented usage pattern (users setting `to` = `CallDispatcher` for HFT calldata execution, and predispatch/postdispatch flows in `IntentGatewayV2`) makes non-trivial residual balances a routine occurrence (e.g., swap slippage, `minAmountOut` leaving remainder, or tokens outside the swept `output.assets`/`inputs` list), giving attackers frequent, low-effort opportunities to drain them.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the trusted apps that are expected to use it (e.g., an `onlyAuthorizedCaller` allowlist maintained by governance, or make each app deploy/own its own dispatcher instance instead of sharing one canonical singleton). Additionally, ensure any residual balance is swept back to a safe owner at the end of every `dispatch()` invocation rather than relying on each calling contract's own bespoke sweep logic, and add checks preventing dangling ERC20 approvals from `CallDispatcher` to arbitrary attacker-supplied spenders.

### Proof of Concept
1. Wait for (or trigger, e.g. via an HFT cross-chain calldata-swap that leaves slippage residue) any non-zero token/ETH balance to sit in the shared `CallDispatcher` contract.
2. As any unprivileged address, call `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(token).balanceOf(dispatcherAddress))})]))`.
3. Since `dispatch()` has no access control, the call succeeds; the dispatcher itself calls `token.transfer(attacker, balance)`, moving the balance to the attacker. [1](#0-0)

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-502)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-533)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L326-328)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
