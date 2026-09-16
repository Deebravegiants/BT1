### Title
Reentrancy in `IntentGatewayV2.placeOrder()` (Tron variant) via predispatch calldata — escrow credited before tokens are actually swept, and no reentrancy guard - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The mainline EVM `IntentGatewayV2`/`IntentsBase`/`IntrinsicIntents`/`ExtrinsicIntents` contracts already apply the CEI (checks-effects-interactions) pattern that the external report recommends: `_filled[commitment]` is set before any external call in `_fillSameChain`, `_fillCrossChain`, and `_withdraw`, and this is backed by a dedicated `IntrinsicIntentsReentrancyTest.sol` test suite. `placeOrder()` in the mainline contract (`evm/src/apps/IntentGatewayV2.sol`) is additionally protected by `nonReentrant`. However, the Tron fork of the contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) reimplements `placeOrder()` without the `nonReentrant` guard, and structures the predispatch flow so that escrow accounting is written to storage in an order that is unsafe relative to the external call that actually moves the tokens.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol::placeOrder()`, when an order carries `predispatch.call` (arbitrary attacker-supplied calldata executed via the `CallDispatcher`), the function:

1. Transfers the predispatch assets to the `CallDispatcher`.
2. Calls `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` — this executes **caller-controlled** calls in the `CallDispatcher`'s context [1](#0-0) .
3. Builds `transferCalls` to sweep the resulting balances from the dispatcher back to the gateway, and in the **same loop**, credits `_orders[commitment][token] += reducedInputs[i].amount` for escrow accounting [2](#0-1) .
4. Only afterwards actually executes the sweep: `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` [3](#0-2) .

This means the `_orders` escrow mapping — the storage that other functions (`fillOrder`, `cancelOrder`, `withdraw`) rely on as proof that tokens are actually held by the gateway — is populated *before* the tokens have actually been transferred back into the gateway. Crucially, unlike the mainline `evm/src/apps/IntentGatewayV2.sol::placeOrder()`, which carries a `nonReentrant` modifier [4](#0-3) , the Tron variant's `placeOrder()` has **no reentrancy guard**: `function placeOrder(Order memory order, bytes32 graffiti) public payable {` [5](#0-4) .

This is the same class of bug as the analog report: a multi-step "installation" (here, order placement/escrow bookkeeping) is split across several storage writes, interleaved with an external call to a party that the caller effectively controls (the predispatch calldata routed through `CallDispatcher`), without effects being fully committed atomically or without a reentrancy lock. Because the predispatch calldata is attacker-supplied and executed in step 2 (before the escrow bookkeeping is even written) and the final sweep call in step 4 happens after the bookkeeping write, an attacker's contract embedded in `predispatch.call`, or a malicious/callback-triggering ERC-20 used as `order.inputs`/`predispatch.assets`, can reenter `placeOrder` (no guard) or other public functions (`cancelOrder`, `fillOrder`) while the gateway's real token balance and the `_orders` escrow map are inconsistent with each other.

### Impact Explanation
If escrow accounting (`_orders[commitment][token]`) can be made to reflect amounts not yet (or never) actually held by the gateway, and no reentrancy guard prevents concurrent invocation, a same-chain order could be filled, cancelled, or double-escrowed against inflated/duplicated bookkeeping, allowing a solver or the order-placer's own reentrant call to withdraw more value than was ever transferred into the contract — i.e., theft of escrowed input tokens or a permanently inconsistent escrow ledger. This directly reaches the "concrete theft ... of funds" bar via the intent gateway's escrow, one of the explicitly in-scope paths (intents escrow and bids).

### Likelihood Explanation
Medium. `placeOrder` is callable by any unprivileged user via a single transaction with attacker-controlled `predispatch.call` and `order.inputs`/`predispatch.assets` (which can include an ERC-20 with transfer hooks). The absence of `nonReentrant` (present in the mainline contract but missing here) and the ordering of the escrow-credit write before the actual token sweep execution are concrete, verifiable deviations from the hardened mainline implementation, which strongly suggests this is an unintentional omission specific to the Tron port rather than a deliberately accepted risk.

### Recommendation
Port the same `nonReentrant` protection (or an equivalent mutex) applied to `evm/src/apps/IntentGatewayV2.sol::placeOrder()` to the Tron variant, and reorder the predispatch flow so that `_orders[commitment][token]` is only credited after `ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls))` has executed and the actual balances have been confirmed — mirroring the CEI fix already applied and tested (`IntrinsicIntentsReentrancyTest.sol`) for the fill/withdraw paths in the mainline contracts.

### Proof of Concept
Not independently executable from the available index (the Tron contract's build/test harness was not available to run locally); the analysis is based on static comparison against the mainline, already-hardened `IntentGatewayV2.sol`/`IntentsBase.sol` and their regression tests. A concrete PoC would: (1) deploy the Tron `IntentGatewayV2`, (2) place an order with `predispatch.assets` set to a malicious ERC-20 (or `predispatch.call` targeting an attacker contract) that reenters `placeOrder`/`cancelOrder` during the `CallDispatcher.dispatch` calls, and (3) demonstrate that `_orders[commitment][token]` can be credited without the corresponding token balance landing in the gateway, or that a nested call can cancel/withdraw against inconsistent escrow state. This PoC construction is inferred from the code paths shown above and was not run against a live/forked environment as part of this analysis — verifying it end-to-end would require a Devin session with full repository/tooling access.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-338)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L413-414)
```text
            // Execute the call dispatcher with predispatch call
            ICallDispatcher(dispatcher).dispatch(order.predispatch.call);
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
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
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L448-449)
```text
            // Execute transfer calls from call dispatcher
            ICallDispatcher(dispatcher).dispatch(abi.encode(transferCalls));
```

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```
