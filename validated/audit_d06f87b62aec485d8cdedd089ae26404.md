### Title
Unrestricted, callerless `CallDispatcher.dispatch` lets anyone drain any token allowance granted to the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch(bytes memory encoded)` executes an arbitrary, caller-supplied `Call[]` batch against any target address with the `CallDispatcher` itself as `msg.sender`, and it has **no access control at all** — not even an owner/role check like the `isOwnerOfProfile` gate in the reported `Anchor.execute` analog. Because `CallDispatcher` is a single, shared, well-known contract instance used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` for "calldata execution," and the documented usage pattern for these features explicitly requires users/protocols to grant ERC20 **approvals to the `CallDispatcher` address**, any such approval becomes a permanent, publicly-exploitable allowance: anyone can call `dispatch()` directly with a `Call` encoding `token.transferFrom(victim, attacker, amount)`, and since `CallDispatcher` is the approved spender, the call succeeds regardless of who invoked `dispatch`.

### Finding Description
`CallDispatcher.dispatch` is defined as: [1](#0-0) 

There is no `onlyX`/`restrict` modifier, no `msg.sender` check, and no reentrancy guard — literally any address can call this function with any ABI-encoded `Call[]`.

This contract is the shared execution primitive advertised for "Calldata Execution" across multiple apps:
- `HyperFungibleToken.onAccept` executes `ICallDispatcher(_dispatcher).dispatch(message.data)` after minting tokens to the beneficiary. [2](#0-1) 
- `WrappedHyperFungibleToken.onAccept` does the same after unlocking/unwrapping tokens. [3](#0-2) 
- `IntentGatewayV2.placeOrder` sends predispatch assets to the dispatcher and calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`. [4](#0-3) 

The official documentation explicitly instructs users to grant approvals to this shared dispatcher for swap-style calldata (e.g. "Approve UniswapV2 router" calls executed from the dispatcher's context), and separately warns:

"Token approvals in the Call[] should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution." [5](#0-4) 

That warning implicitly acknowledges the dispatcher can hold approvals/tokens, but nowhere addresses the actual root cause: `dispatch()` itself is unauthenticated. Since `CallDispatcher` is deployed once per chain and shared across all these apps (its address is published on the "contract addresses" pages), *any* approval a user grants to that address — for a HyperFungibleToken swap-and-bridge flow, a WrappedHyperFungibleToken calldata flow, or an IntentGatewayV2 predispatch flow — remains spendable by that address indefinitely (or until the approval is used/revoked). Because `dispatch` doesn't check who is calling it, an attacker doesn't need to wait for any legitimate flow to run at all: they can call `CallDispatcher.dispatch()` directly, at any time, with a `Call` such as `{to: token, value: 0, data: abi.encodeWithSelector(IERC20.transferFrom.selector, victim, attacker, amount)}`, and it will succeed as long as `victim` has ever approved the dispatcher for `amount` of `token` — exactly the pattern the docs tell users/integrators to use.

### Impact Explanation
This allows outright theft of ERC20 tokens from any account (user or protocol) that has an outstanding approval to the shared `CallDispatcher` contract, which is the documented, expected integration pattern for the HyperFungibleToken/WrappedHyperFungibleToken "Calldata Execution" feature and the IntentGatewayV2 predispatch/postdispatch feature. Since `CallDispatcher` also has a `receive()` and can hold native ETH transiently (e.g. during `IntentGatewayV2.placeOrder`'s predispatch native-asset transfer window), any ETH balance briefly resident in the dispatcher can also be swept out by an unrelated third party by racing/observing pending state. This is concrete, permanent loss of funds reachable by any unprivileged third party — no special role, ownership, or privileged position required — matching and exceeding the severity of the reported `Anchor.execute` analog (which at least required actual profile ownership).

### Likelihood Explanation
High. `CallDispatcher.dispatch` is a plain, unauthenticated `external` function on a publicly known, shared, permanently-deployed contract address. Exploitation requires no special timing, front-running, or governance compromise — merely observing (or knowing) that a victim has an outstanding token approval to the dispatcher (which is the intended integration pattern encouraged by the docs) and submitting a single transaction calling `dispatch()` with the appropriate `Call[]`.

### Recommendation
Restrict `CallDispatcher.dispatch` so it can only be invoked by the set of authorized app contracts that are meant to drive it (e.g. an allowlist of `HyperFungibleToken`/`WrappedHyperFungibleToken`/`IntentGatewayV2` instances, or a per-call authorization token verified atomically), and/or redesign the approval model so approvals are never left standing against the shared dispatcher (e.g. use `permit`-based single-use approvals scoped to a specific call, or have the dispatcher pull funds only via a signed, single-use authorization tied to the specific `Call[]` being executed). At minimum, add a caller restriction (`onlyRegisteredApp`) and a reentrancy guard to `dispatch`.

### Proof of Concept
1. A user (or protocol) follows the documented pattern and grants `IERC20(token).approve(CALL_DISPATCHER, amount)` so that a future HyperFungibleToken/WrappedHyperFungibleToken/IntentGatewayV2 calldata-execution flow can pull `amount` of `token` from them via the dispatcher.
2. Before that legitimate flow executes (or even if it never does), an attacker calls:
```solidity
Call[] memory calls = new Call[](1);
calls[0] = Call({
    to: token,
    value: 0,
    data: abi.encodeWithSelector(IERC20.transferFrom.selector, victim, attacker, amount)
});
CallDispatcher(CALL_DISPATCHER).dispatch(abi.encode(calls));
```
3. `CallDispatcher.dispatch` has no caller check, decodes the `Call[]`, and executes `token.transferFrom(victim, attacker, amount)` with `msg.sender == CallDispatcher` (the approved spender), succeeding and transferring `victim`'s tokens directly to `attacker`, entirely independent of any legitimate cross-chain message or order flow.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L299-305)
```text
        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-328)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
