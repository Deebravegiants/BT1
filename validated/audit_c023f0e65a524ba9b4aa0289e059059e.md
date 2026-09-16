## Title
Unrestricted `CallDispatcher.dispatch()` allows any unprivileged caller to force the shared dispatcher to execute arbitrary calls, enabling theft of tokens/ETH the dispatcher is transiently holding for other users' orders/transfers - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a single, shared, chain-wide utility contract used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` to execute attacker/solver/order-creator supplied `Call[]` payloads (approve+swap, sweep, etc.) while it transiently custodies tokens/ETH mid-transaction. Its `dispatch(bytes)` entrypoint has **no access control whatsoever** - any address, not just the apps that are supposed to invoke it, can call it directly at any time with an arbitrary `Call[]`. This mirrors the LooksRareProtocol bug class where an unconstrained "call an arbitrary selector on an arbitrary target" primitive was reachable and could be pointed at victims' approved/held tokens - except here the reachable actor is any unprivileged address, not the protocol owner.

### Finding Description
`CallDispatcher.dispatch` is declared with no modifier and no caller check: [1](#0-0) 

It decodes an arbitrary `Call[]` and, for each entry, performs `to.call{value: call.value}(call.data)` with `msg.sender == address(CallDispatcher)`. Any address on-chain can invoke `dispatch` directly (i.e., without going through `HyperFungibleToken.onAccept`, `WrappedHyperFungibleToken.onAccept`, or `IntentGatewayV2._fillOrder`/`_execute`). All three legitimate call-sites treat the dispatcher as their own private scratch space and rely on the assumption that only they will ever invoke `dispatch` while it is holding funds:

- `HyperFungibleToken.onAccept` / `WrappedHyperFungibleToken.onAccept` mint/unlock tokens to `to` (which callers are told to set to the `CallDispatcher` address) and then call `ICallDispatcher(_dispatcher).dispatch(message.data)`: [2](#0-1) 
- `IntentGatewayV2`/`IntentsBase` transfer predispatch/postdispatch assets into the dispatcher, call `dispatch(order.predispatch.call)` / `dispatch(order.output.call)`, and only afterward sweep the residual balance back out: [3](#0-2) 
- The docs explicitly acknowledge the dispatcher "holds tokens temporarily during execution" and recommend exact-amount approvals rather than unlimited ones as a mitigation for this custody window: [4](#0-3) 

Because `dispatch` is public and un-gated, any unprivileged party can race a legitimate flow (front-run in the same block, or reenter from within an attacker-controlled `Call.to` target that a solver/order-creator is permitted to specify in `order.predispatch.call` / `order.output.call` / HFT `message.data`) and issue their own `dispatch()` call while the shared dispatcher is holding another user's tokens/ETH mid-transaction, redirecting them to an attacker-chosen recipient before the legitimate sweep/transfer-back executes. `IntentGatewayV2` guards its own entrypoints with `ReentrancyGuardTransient`, but that guard does not protect `CallDispatcher` itself, since it is an external, unrestricted contract that anyone (including code invoked as part of `order.predispatch.call`/`order.output.call`) can call independently of the gateway's reentrancy lock: [5](#0-4) 

This is structurally the same class of bug as the LooksRare report: a generic "execute an arbitrary call against an arbitrary target" primitive with no restriction on who can invoke it or what state it can act on, reachable while the contract is holding third-party value.

### Impact Explanation
Any unprivileged actor able to observe or trigger a pending cross-chain delivery or intent fill that routes through the shared `CallDispatcher` (which is a single deployment per chain, shared by every HFT/WrappedHFT instance and by `IntentGatewayV2`) can drain the tokens/ETH the dispatcher is transiently holding for that operation by calling `dispatch()` directly with a `Call[]` that transfers the dispatcher's current balance of the relevant token to themselves, ahead of the legitimate sweep-back call. This is a concrete theft-of-funds vector affecting ordinary users' bridged tokens and intent settlement amounts, not merely a resource/DoS issue.

### Likelihood Explanation
High reachability: `dispatch` requires no privilege, no proof, and no state beyond calling the function; the only prerequisite is that the dispatcher currently holds value belonging to an in-flight operation, which happens on every HFT calldata-execution transfer and every `IntentGatewayV2` predispatch/postdispatch fill that uses calldata. An attacker can trivially monitor the mempool/pending relayer deliveries and front-run/reenter the sweep step.

### Recommendation
Restrict `CallDispatcher.dispatch` to only the authorized caller for a given invocation (e.g., pass and verify the intended caller, or deploy per-caller/per-operation dispatcher instances instead of a single shared singleton), and/or add a reentrancy guard plus an explicit allow-list of callers (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2` instances) so unrelated third parties cannot invoke `dispatch()` while it is holding another operation's funds.

### Proof of Concept
1. Wait for (or trigger) a legitimate cross-chain HFT delivery or `IntentGatewayV2` fill whose `data`/`predispatch.call`/`output.call` mints/transfers tokens into the shared `CallDispatcher` address before the app's own follow-up `dispatch()` call sweeps them back out.
2. In the same block (front-run) or via a reentrant call from a target contract referenced in the order's/message's own `Call[]`, call `CallDispatcher.dispatch(encoded)` directly, where `encoded` decodes to `Call[]{ to: <token>, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, IERC20(token).balanceOf(dispatcher)) }`.
3. Because `dispatch` has no caller restriction, this succeeds and transfers the dispatcher's current token balance (belonging to the victim's in-flight transfer/order) to the attacker before the legitimate sweep executes.

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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-527)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** evm/src/apps/IntentGatewayV2.sol (L60-60)
```text
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
```
