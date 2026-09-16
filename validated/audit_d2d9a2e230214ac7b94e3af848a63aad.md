### Title
Unauthenticated `CallDispatcher.dispatch` allows anyone to drain any token/ETH balance held by the shared CallDispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch` is a public `external` function with **no access control** that executes an arbitrary, caller-supplied array of `Call{to, value, data}` structs via raw `.call`. `IntentGatewayV2`/`IntentsBase` and `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` all route funds through this single shared dispatcher during order fulfillment and calldata-execution flows, temporarily transferring tokens/native ETH into it before/while it executes attacker- or solver-supplied calls. This is the same bug class as the reported `VoterProxy.deposit` issue: any unprivileged caller can invoke a privileged, unrestricted "execute-on-behalf-of-me" entry point with arbitrary parameters, letting them act on behalf of the contract that is supposed to be the only legitimate caller.

### Finding Description
`CallDispatcher.dispatch` decodes `Call[]` from raw calldata and executes each call with `to.call{value: call.value}(call.data)`, reverting only if `to` has no code or the call fails — there is no `msg.sender` check tying invocation to the intended caller (e.g. `IntentGatewayV2` or `WrappedHyperFungibleToken`): [1](#0-0) 

The contract also explicitly accepts arbitrary ETH via `receive()`: [2](#0-1) 

This `CallDispatcher` is used as a shared execution sink across multiple call sites:
- `IntentGatewayV2` transfers order input/predispatch assets to the dispatcher and invokes `ICallDispatcher(dispatcher).dispatch(...)` to run solver-supplied `order.predispatch.call` / `order.output.call`, then sweeps balances back: [3](#0-2) 
- `IntentsBase._execute` funds the dispatcher, runs `order.output.call`, then sweeps residual token/ETH balances back as "dust": [4](#0-3) 
- `WrappedHyperFungibleToken.onAccept` invokes the same dispatcher with attacker-controlled cross-chain `message.data` after unlocking tokens to the beneficiary: [5](#0-4) 

Because `dispatch` has no caller restriction, and the dispatcher is a shared, code-having contract that regularly holds token/ETH balances mid-flow (assets pushed in before the "official" dispatch call executes, and any leftover dust or under-swept balances after), anyone can front-run or directly call `CallDispatcher.dispatch` with their own `Call[]` to sweep out whatever balance the dispatcher currently holds to an address of their choosing — exactly analogous to `VoterProxy.deposit` accepting arbitrary `_token`/`_gauge` from any caller and letting them act on behalf of the privileged contract.

### Impact Explanation
Any assets that transiently reside in the `CallDispatcher` (order inputs/predispatch assets pushed by `IntentGatewayV2`/`IntentsBase` before the legitimate `dispatch(order.predispatch.call)` executes, residual "dust" left after imperfect sweeps, or ETH sent via `receive()`) can be stolen by an unrelated third party simply by calling `dispatch` directly with a `Call` that transfers the token/ETH to themselves. This is a direct theft-of-funds vector reachable from a single unprivileged transaction, satisfying "concrete theft ... of funds."

### Likelihood Explanation
`dispatch` is `external` with zero access control (no `onlyGateway`/`onlyHost`/`msg.sender` check), so exploitation requires no special permissions — only observing (via mempool) or timing a transaction that funds the dispatcher, or exploiting any window in which the dispatcher holds residual balance (e.g., dust after `_execute`'s sweep, or funds pushed to the dispatcher as part of `IntentGatewayV2`'s predispatch flow before the sweep-back completes). Given the dispatcher is a single shared, permanently-deployed contract referenced by multiple apps (`IntentGatewayV2`, `IntentsBase`, `WrappedHyperFungibleToken`), the attack surface recurs on every order/transfer that routes funds through it.

### Recommendation
Restrict `CallDispatcher.dispatch` to only be callable by the specific trusted contract instance that is meant to use it (e.g., an immutable `owner`/`gateway` address set at construction and checked via `require(msg.sender == authorizedCaller)`), mirroring the report's recommendation to whitelist/authenticate the caller rather than accepting arbitrary calls from anyone. Alternatively, deploy an ephemeral (per-call, self-destructing or single-use) dispatcher instance per order/transfer so no shared contract balance can ever be targeted by an unrelated caller.

### Proof of Concept
1. Observe (via mempool or on-chain state) that `CallDispatcher` at address `D` currently holds a nonzero ERC20/ETH balance — e.g., mid-flight during an `IntentGatewayV2.fillOrder`/`newOrder` call after assets are transferred to `D` but before `ICallDispatcher(D).dispatch(order.predispatch.call)` completes and sweeps them back [3](#0-2) , or dust left behind after `IntentsBase._execute`'s sweep loop [6](#0-5) .
2. Craft `Call[] calls = [Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]` (or a native-ETH self-call for ETH balance).
3. Call `CallDispatcher(D).dispatch(abi.encode(calls))` directly from any EOA — no permission check in `dispatch` blocks this [1](#0-0) .
4. The dispatcher's balance is transferred to the attacker instead of being returned to the legitimate `IntentGatewayV2`/`WrappedHyperFungibleToken` flow.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L37-39)
```text
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

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

**File:** evm/src/apps/IntentGatewayV2.sol (L244-289)
```text
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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L326-328)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```
