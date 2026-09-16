### Title
CallDispatcher.dispatch() has no access control, letting anyone drain any ETH/token balance or standing allowance the shared dispatcher happens to hold - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, chain-wide singleton contract shared by `HyperFungibleToken`/`WrappedHyperFungibleToken` (mint/unlock + calldata execution) and `IntentGatewayV2`/`ExtrinsicIntents` (predispatch/postdispatch calldata execution). Its `dispatch()` function is `external` with no caller restriction and executes attacker-supplied `Call[]` as the dispatcher itself. Just like the Superfluid QI Vesting incident — where a contract that held standing token approvals exposed a function that could be fed arbitrary calldata, letting the attacker use the vesting contract's own authority (approvals) to drain unrelated user funds — any residual native ETH or ERC20 balance/allowance sitting on `CallDispatcher` between legitimate uses can be swept by an unrelated, unprivileged caller simply by invoking `dispatch()` directly with their own `Call[]`.

### Finding Description
`CallDispatcher.dispatch()` is defined with no modifier and no `msg.sender` check: [1](#0-0) 

It accepts an ABI-encoded `Call[]` and, for every entry, performs `to.call{value: call.value}(call.data)` — i.e., it executes arbitrary calls **as itself**, using whatever balance and whatever ERC20 allowances the `CallDispatcher` address currently holds. There is no restriction limiting who can call `dispatch()`; it is not gated behind the ISMP host, `IntentGatewayV2`, or `HyperFungibleToken`.

The dispatcher also unconditionally accepts native ETH: [2](#0-1) 

Every legitimate integration temporarily routes funds through this shared contract and relies on the caller-contract's own logic (e.g. `_execute` in `IntentsBase.sol`, or the predispatch flow in `IntentGatewayV2.sol`) to sweep the dispatcher clean afterward: [3](#0-2) [4](#0-3) 

However, the sweep logic only accounts for **known** tokens (`order.output.assets`, `order.inputs`) — any token or approval left behind that is not in that enumerated list is never swept. The docs explicitly acknowledge that calls routed through the dispatcher grant allowances from the dispatcher's own address and warn against unlimited approvals precisely because "the dispatcher contract holds tokens temporarily during execution": [5](#0-4) 

Because `dispatch()` itself has zero access control, this "temporary" custody is not actually protected — anyone can call `CallDispatcher.dispatch()` directly, at any time, with their own `Call[]` to:
1. Sweep any native ETH balance left on the contract (e.g. accidentally sent via `receive()`, or leftover from a `Call.value` that wasn't fully consumed).
2. Spend any stale ERC20 allowance the dispatcher granted to a third party during a prior `approve`+`swap` calldata sequence (e.g., a solver's postdispatch calldata approving a router for `amount` but the swap reverting/partial, or an unlimited-approval mistake by an order author) — by directing that spender or by calling `transferFrom` themselves if the dispatcher is `msg.sender`/owner of the allowance.
3. Race a legitimate multi-call sequence: since `dispatch()` calls are not atomic *across* separate transactions, if any transient token balance briefly sits on the dispatcher between two different top-level calls (e.g., predispatch assets transferred in `IntentGatewayV2.placeOrder` before `dispatch(order.predispatch.call)` executes in the same tx — actually atomic — but any dust left after a *reverted* sweep, or ETH sent standalone), an unprivileged actor can front-run/back-run to steal it via their own `dispatch()` call.

This is the same bug class as the Superfluid incident: a shared contract that (a) is granted spending authority/holds funds on behalf of users, and (b) exposes a public entry point that executes attacker-controlled calldata as itself, allowing the attacker to redirect that authority to steal funds that were never theirs.

### Impact Explanation
`CallDispatcher` is deployed once per chain and reused by every `HyperFungibleToken`/`WrappedHyperFungibleToken` deployment and every `IntentGatewayV2`/`ExtrinsicIntents` instance on that chain. Any ETH or token value/allowance that ends up resting on it — even transiently, due to a partial fill revert, an unswept non-enumerated token, or an unlimited-allowance mistake by any order author across the entire protocol — is directly and permanently stealable by an unrelated, completely unprivileged third party with a single transaction. Given the contract is shared infrastructure across all apps and all users on a chain, this is a systemic theft vector, not limited to a single app or user.

### Likelihood Explanation
Likelihood is elevated because: (1) `dispatch()` has literally no caller restriction, so exploitation requires no special privilege, front-running position, or governance compromise; (2) the protocol's own documentation warns integrators against unlimited allowances specifically because of this custody model, implying such approvals are a known, plausible integrator mistake; (3) partial fills, reverted sweeps, or a token not enumerated in `order.output.assets`/`predispatch.assets` occurring while it is nonetheless a side-effect of executed calldata are realistic operational scenarios across many concurrent orders/messages routed through the same shared dispatcher.

### Recommendation
Restrict `CallDispatcher.dispatch()` so it can only be invoked by the specific set of app contracts authorized to route calldata through it (e.g., an allowlist of caller addresses set at deployment/governance, or make each app deploy/own its own dispatcher instance rather than sharing one singleton). Additionally, enforce that the dispatcher never retains standing allowances or balances across transactions — e.g., require any `approve` calls executed via `dispatch()` to be immediately followed, within the same batch, by a revocation to zero, and add a generic sweep-any-residual-ETH/token step that runs at the end of every `dispatch()` invocation regardless of which tokens the caller enumerates.

### Proof of Concept
1. A user places an `IntentGatewayV2` order whose `output.call` (postdispatch calldata, executed via `_execute`) approves a DEX router for `amount` DAI from the `CallDispatcher`'s address, then calls `swapExactTokensForTokens`; the swap call reverts partway through a multi-hop path or the router only partially consumes the allowance.
2. `IntentsBase._execute` sweeps only the `output.assets` tokens it knows about; the residual DAI allowance granted to the router is not revoked and is not one of the swept tokens.
3. An attacker (any EOA, no special role) directly calls `CallDispatcher.dispatch(abi.encode(calls))` with `calls = [{to: routerOrDaiAddress, value: 0, data: <calldata that leverages the stale allowance/balance, e.g. instructing the router or a crafted contract to pull the allowed DAI from CallDispatcher to attacker>}]`.
4. Because `dispatch()` has no access control, the call succeeds, and the attacker extracts value that belonged to the protocol/users, using the `CallDispatcher`'s residual authority — mirroring how the Superfluid attacker fed incorrect calldata to a contract holding user approvals to redirect funds to themselves. [6](#0-5)

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

**File:** evm/src/utils/CallDispatcher.sol (L41-62)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L413-449)
```text
            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);

            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }

            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
