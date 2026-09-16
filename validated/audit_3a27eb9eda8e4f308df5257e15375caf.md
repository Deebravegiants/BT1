### Title
Unauthenticated `CallDispatcher.dispatch()` lets any unprivileged caller drain assets and approvals left in the shared dispatcher - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, permanently-deployed, shared contract used by every `IntentGatewayV2` order (predispatch/postdispatch calldata) and by `HyperFungibleToken`/`WrappedHyperFungibleToken` (destination calldata execution). Its `dispatch()` function has **no access control** — any address can call it directly to make the dispatcher execute arbitrary calls, including ERC20 `approve`/`transfer` calls, as `msg.sender = CallDispatcher`. Because the dispatcher is reused across every order/every bridge transfer rather than being a per-order/per-user escrow, any approval or leftover balance it ever accumulates is reachable by anyone, exactly like the Footium report's "previous owner's unrevoked approval" — except here the "approval owner" is any arbitrary unprivileged caller, not even a former legitimate party.

### Finding Description
`CallDispatcher.dispatch()` is declared `external` with zero caller restriction: [1](#0-0) 

`IntentGatewayV2` (and `HyperFungibleToken`) rely on this same singleton instance to run untrusted, order-supplied `Call[]` payloads while assets are transiently parked on the dispatcher — during `predispatch` (assets are transferred to the dispatcher, `dispatch()` runs the order's calldata, then the resulting balance is swept back) and during `postdispatch`/output execution (`_execute` in `IntentsBase`), where any token not covered by the declared input/output list is never swept and permanently accumulates as "dust": [2](#0-1) [3](#0-2) 

The project's own documentation already flags the danger of leftover approvals on this shared dispatcher: *"Token approvals in the Call[] should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution."* [4](#0-3) 

Because `dispatch()` has no `onlyGateway`/`onlyOwner` guard, this warning understates the real risk: an attacker does not need to rely on some other order-creator leaving behind an unlimited allowance — the attacker can call `dispatch()` themselves at any time to (a) grant themselves an unlimited allowance over any ERC20 the dispatcher will ever hold (`token.approve(attacker, type(uint256).max)`, executed with `msg.sender = CallDispatcher`), and/or (b) directly command the dispatcher to `transfer`/`transferFrom` out any ERC20 or native ETH balance it currently holds — no prior approval even required, since the dispatcher is itself the token owner and can be made to call `transfer` on demand. Any "dust" token that is not part of a given order's declared `inputs`/`output.assets` list (e.g., reward tokens from a predispatch DEX swap, leftover `Call.value` ETH, or residual allowances to intermediate routers) sits in this shared contract indefinitely and is public domain for the first caller to claim.

This is structurally the same bug class as the Footium finding: a shared custodial contract retains state (balances/approvals) across unrelated actors/orders with no mechanism to scope or revoke it, and anything left behind is extractable by someone who was never entitled to it.

### Impact Explanation
Any unprivileged account can permanently steal:
- Any ERC20/native dust that accumulates in `CallDispatcher` from `IntentGatewayV2` predispatch/postdispatch flows or from `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-execution flows (tokens outside the declared input/output list are never swept back).
- Any allowance the dispatcher's own prior legitimate calldata left in place for a router/spender, if that spender is later compromised or if the attacker can otherwise trigger the dispatcher to make further calls.

Since `CallDispatcher` is a single, immortal, shared deployment referenced by `_params.dispatcher` across the whole protocol (not one instance per order), the blast radius covers every order and every HFT bridge transfer that ever routes assets through it — an unauthorized third party can call `dispatch()` to unilaterally move assets out, which is unauthorized app action / concrete theft of protocol/user funds.

### Likelihood Explanation
`dispatch()` requires zero permissions and zero preconditions to invoke — it is a single unauthenticated transaction. The only variable is whether the dispatcher currently holds a nonzero balance of some token/ETH (which happens routinely via dust from swaps/predispatch/postdispatch flows) or whether the dispatcher has an outstanding third-party allowance. Given the frequency of order flow through `IntentGatewayV2` and cross-chain transfers through `HyperFungibleToken`, opportunities for dust to accrue are continuous and easily monitored on-chain by any bot.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the specific, whitelisted app contracts that are supposed to use it (e.g., an `onlyGateway`/`onlyAuthorizedCaller` modifier configured per deployment), and/or make the dispatcher stateless per invocation (e.g., deploy an ephemeral dispatcher/minimal proxy per call, or use `delegatecall`-free single-use contexts) so no balance or approval can ever persist between invocations. Additionally, ensure all "dust" tokens not declared in `inputs`/`output.assets` are still swept (or explicitly disallowed) rather than left indefinitely on the dispatcher.

### Proof of Concept
1. Attacker (no special privileges) submits a transaction calling `CallDispatcher.dispatch(encodedCalls)` directly, where `encodedCalls` decodes to a `Call[]` with `to = <any ERC20 the dispatcher currently holds>`, `value = 0`, `data = abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)`.
2. Since `dispatch()` has no access control (`evm/src/utils/CallDispatcher.sol:44`), this call succeeds and the ERC20 `transfer` executes with `msg.sender = CallDispatcher`, moving any dust/balance currently held by the dispatcher to the attacker.
3. Alternatively, attacker calls `dispatch()` with a `Call` to `token.approve(attacker, type(uint256).max)` ahead of time; whenever the dispatcher subsequently accumulates a balance of that token (e.g., unswept dust from another user's predispatch swap via `IntentGatewayV2.placeOrder`), the attacker calls `token.transferFrom(dispatcher, attacker, amount)` to drain it.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L258-289)
```text
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
