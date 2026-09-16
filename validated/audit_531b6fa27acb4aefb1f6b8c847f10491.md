### Title
Unrestricted `CallDispatcher.dispatch()` lets attacker-supplied calldata mint standing ERC20 approvals on the shared dispatcher, enabling Seneca-style `transferFrom` theft - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher.dispatch()` executes arbitrary attacker-controlled `Call[]` arrays with no caller restriction and no allowlist on target/selector. It is used as a *single shared* execution context by `IntentGatewayV2`/`IntentsBase` (predispatch/postdispatch calldata) and by `HyperFungibleToken`/`WrappedHyperFungibleToken` (`onAccept` calldata execution). Any unprivileged order-placer or cross-chain message sender can embed an `IERC20.approve(attacker, type(uint256).max)` call in their own order/message, executed *as* the dispatcher, leaving a permanent unlimited ERC20 allowance from the dispatcher to an attacker-chosen address. Because the dispatcher is reused by every subsequent order/message across the protocol, any token balance that later transits through it (assets in flight during another user's predispatch/postdispatch sequence, un-swept dust, fee-on-transfer remainders, etc.) becomes stealable by the attacker calling `transferFrom` directly on the ERC20, exactly mirroring the Seneca root cause of an attacker crafting calldata to obtain/exploit a `transferFrom`-enabling approval on a shared contract.

### Finding Description
`CallDispatcher.dispatch` has no access control: [1](#0-0) 

It is invoked with fully attacker-controlled bytes in three attacker-reachable paths:
1. `IntentGatewayV2.placeOrder` — `order.predispatch.call` is dispatched before assets are swept back: [2](#0-1) 
2. `IntentsBase._execute` — `order.output.call` (postdispatch) is dispatched on the same shared dispatcher: [3](#0-2) 
3. `HyperFungibleToken.onAccept` / `WrappedHyperFungibleToken.onAccept` — `message.data`, decoded from a cross-chain POST body, is dispatched after minting/unlocking: [4](#0-3) 

The docs themselves acknowledge the danger of standing allowances left on the dispatcher, but only as advice to integrators, not as an enforced protocol invariant: [5](#0-4) 

Because `dispatch()` executes calls in the dispatcher's own `msg.sender` context (not delegatecall) and is shared by every order/message routed through `_params.dispatcher` / `_dispatcher`, an attacker can submit their own order/message whose `Call[]` performs `token.approve(attacker, type(uint256).max)`. This grants the attacker a persistent, unlimited spending allowance over the dispatcher for that token — independent of whether the attacker's own order ever fully executes or reverts elsewhere. Any subsequent balance the dispatcher temporarily or residually holds for that token (e.g., dust left when `balance < requiredAmount` prevents a full sweep, fee-on-transfer remainders, or assets sitting in the dispatcher mid-transaction for a wholly unrelated legitimate order using the same token) is then directly drainable by the attacker calling `token.transferFrom(dispatcher, attacker, amount)` from an EOA — no further interaction with Hyperbridge contracts required. This is structurally identical to the Seneca bug class: an attacker constructs calldata processed by a shared, approval-bearing contract to obtain/abuse a `transferFrom` path and redirect tokens that were never meant to be spendable by them.

### Impact Explanation
This breaks the isolation assumption between unrelated orders/messages that the "predispatch/postdispatch executes in its own context" security model relies on. Standing infinite approvals left by one malicious actor persist indefinitely on the shared `CallDispatcher`, silently converting any future dust, fee-on-transfer remainder, or timing window of token custody in the dispatcher into stealable funds for that attacker — a concrete theft-of-funds vector across the `IntentGatewayV2` and `HyperFungibleToken`/`WrappedHyperFungibleToken` calldata-execution surfaces, which is High severity under the "concrete theft" acceptance criterion.

### Likelihood Explanation
Reachable with a single unprivileged `placeOrder` call (attacker crafts `predispatch.call`/`output.call`) or a single dispatched cross-chain token-transfer message with adversarial `data` — no special privileges, governance, or relayer collusion required. The only precondition is that the dispatcher later holds/receives a non-zero balance of the approved token, which is realistic given documented dust accumulation and fee-on-transfer edge cases already handled elsewhere in the codebase (`DustCollected` events, `balance < requiredAmount` reverts leaving residue unswept).

### Recommendation
Restrict `CallDispatcher.dispatch` to a strict per-call allowlist derived from the caller's own order/message context, or make the dispatcher non-shared (deploy an ephemeral/one-time dispatcher per order execution) so no standing approvals can outlive a single atomic call. Additionally, revoke any `approve()`-type side effects at the end of every `dispatch()` invocation (e.g., forcibly reset allowances for any token touched) so approvals cannot persist across transactions, and enforce that `Call[]` entries cannot target `approve`/`increaseAllowance` selectors on tokens outside the current order's declared input/output set.

### Proof of Concept
1. Attacker calls `IntentGatewayV2.placeOrder` with `order.predispatch.assets = []` (no funds needed) and `order.predispatch.call = abi.encode([Call({to: USDT, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max)})])`.
2. `placeOrder` transfers zero assets, then calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)`, which executes `USDT.approve(attacker, MAX)` as the dispatcher (`evm/src/apps/IntentGatewayV2.sol:258`).
3. The attacker now holds an unlimited USDT allowance from the shared `_params.dispatcher` address, persisted on-chain indefinitely.
4. Whenever any other order or HFT message transiently leaves USDT balance on the dispatcher (e.g., a legitimate predispatch sequence for a different order using USDT, or unswept dust from a `balance < requiredAmount` short-circuit), the attacker calls `USDT.transferFrom(dispatcher, attacker, USDT.balanceOf(dispatcher))` directly, draining those funds without any further interaction with Hyperbridge contracts.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L234-258)
```text
        uint256 msgValue = msg.value;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-305)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
