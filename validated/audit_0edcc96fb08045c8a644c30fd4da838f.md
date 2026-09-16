## Front-Running / Unprotected Fund Drain via Permissionless `CallDispatcher.dispatch()` in IntentGatewayV2 Predispatch Flow - ([File: evm/src/utils/CallDispatcher.sol], [File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Sherlock report describes a front-running bug where `buyShares()` mints LP shares based on the *current token balance minus reserve* rather than a value bound to the depositor, letting an attacker race a pending deposit and claim credit for tokens someone else sent to the contract. The Hyperbridge analog is structurally identical but more severe: `IntentGateway`'s shared `CallDispatcher` holds user funds in transit during `placeOrder`'s `predispatch` flow, and `CallDispatcher.dispatch()` has **no access control at all** — any address can invoke it to move whatever balance the dispatcher currently holds. Combined with the fact that the escrow-sweep logic in the (unfixed) tron variant of `IntentGatewayV2` reads the dispatcher's **absolute balance** rather than a delta bound to the caller's own deposit, an attacker can race/hijack funds sitting in the shared dispatcher exactly as in the reported bug class.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` is declared `external` with no `onlyOwner`, `onlyGateway`, or caller check whatsoever: [1](#0-0) 

`IntentGatewayV2.placeOrder` (predispatch branch) transfers the user's predispatch assets to this same shared, singleton `dispatcher` address *before* invoking the predispatch call and sweeping the result back: [2](#0-1) 

and then determines how much to escrow/treat as dust from the dispatcher's **absolute token balance**, not a before/after delta: [3](#0-2) 

Because `dispatcher` is a single shared contract used by every `placeOrder`/`fillOrder` call across the protocol (predispatch and postdispatch, `IntentsBase._execute` uses the identical absolute-balance sweep pattern), and its `dispatch()` entrypoint is callable by anyone, any moment where the dispatcher legitimately or transiently holds a user's assets is a window an unprivileged third party can race into with their own `dispatch()` call — e.g., during the predispatch call itself (which is arbitrary external calldata, documented as swapping via a DEX/router), a reentrant callback (ERC-777 hook, Uniswap-style callback) let an attacker's contract call `CallDispatcher.dispatch()` directly to sweep out the tokens the victim just deposited, before the victim's own sweep-back executes.

The main (non-tron) EVM contract shows the team already recognized and partially hardened the balance-measurement half of this pattern by moving to a before/after delta: [4](#0-3) 
but even that fix does not address the root cause — `CallDispatcher.dispatch()` remains globally callable by anyone, so the delta-based accounting only prevents the *accounting* from double-counting; it does not stop a third party from draining the dispatcher's balance out from under an in-flight order via a direct or reentrant call.

### Impact Explanation
This is a concrete theft-of-funds vector reachable by any unprivileged actor from a single relayed transaction: a user's predispatch assets (native ETH or ERC20) sitting in the shared `CallDispatcher` can be drained by anyone who calls `dispatch()` with a `Call` that transfers the dispatcher's current balance to themselves, at any point the dispatcher holds a nonzero balance and has not yet swept it back into `IntentGatewayV2`. This directly matches the report's "front-running a pending, uncommitted balance to steal value intended for another depositor" bug class, but is worse because there is no gas-race needed at all when a reentrant callback is available in the predispatch call target — the attack is deterministic rather than probabilistic. Loss is a direct transfer of the victim's escrowed input tokens to the attacker (concrete theft of funds), satisfying the High severity bar.

### Likelihood Explanation
Reachable from a single, ordinary `placeOrder` call carrying `predispatch.call` — a documented, intended feature for "swap-then-escrow" patterns that routes through external DEX/router contracts. Any predispatch target that makes an external call able to re-enter (fee-on-transfer/ERC-777 style tokens, router callbacks, or a malicious/compromised third-party contract named in `predispatch.call`) gives an attacker a deterministic hook to call the unprotected `dispatch()`. Even without reentrancy, the dispatcher is a fixed, publicly known address whose balance is observable in the mempool/on-chain, so a griefing/opportunistic drain via a plain front-run is also possible whenever a legitimate transfer to the dispatcher briefly precedes its sweep in a multi-call transaction context.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by the `IntentGatewayV2` (or other registered app) that owns/created the specific dispatch batch — e.g., an `onlyAuthorizedCaller` modifier keyed to the calling app, or better, deploy a fresh, single-use dispatcher (or use per-order transient escrow) rather than one shared, permanently-funded contract. Additionally, apply the reentrancy-safe delta-accounting pattern (already used in `evm/src/apps/IntentGatewayV2.sol`) uniformly across the tron variant and `IntentsBase._execute`, and add `nonReentrant` guards around any external predispatch/postdispatch call that touches the shared dispatcher.

### Proof of Concept
1. Victim calls `IntentGatewayV2.placeOrder(order, graffiti)` with `order.predispatch.assets = [WETH: 10]` and `order.predispatch.call` encoding a swap through an attacker-influenced or callback-capable router (e.g., a token with a transfer hook, or a router that calls back into `msg.sender`/a registered callback address during the swap).
2. `placeOrder` transfers 10 WETH to `dispatcher` [5](#0-4)  then calls `dispatcher.dispatch(order.predispatch.call)` [6](#0-5) .
3. Inside that call, the external target invokes attacker-controlled code (hook/callback), which calls `CallDispatcher.dispatch(encoded)` directly — a fully public function with no caller restriction — encoding `Call({to: WETH, data: transfer(attacker, dispatcher.balanceOf())})`.
4. The dispatcher's WETH balance (the victim's just-deposited funds) is transferred to the attacker before `IntentGatewayV2` sweeps it back in the subsequent lines [7](#0-6) .
5. The subsequent sweep call in `placeOrder` reads a balance now short of `requiredAmount`, either reverting the order (DoS) or, if partially drained and the remaining balance still exceeds `requiredAmount` in a multi-asset order, silently understating dust while the attacker has already exfiltrated the difference — funds are gone regardless of the transaction's final outcome for the victim.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-414)
```text
        // escrow tokens
        uint256 msgValue = msg.value;
        if (order.predispatch.call.length > 0 && order.predispatch.assets.length > 0) {
            address dispatcher = _params.dispatcher;

            // Transfer all predispatch assets to the call dispatcher
            uint256 assetsLen = order.predispatch.assets.length;
            for (uint256 i; i < assetsLen;) {
                address token = address(uint160(uint256(order.predispatch.assets[i].token)));
                uint256 amount = order.predispatch.assets[i].amount;

                if (token == address(0)) {
                    if (amount > msgValue) revert InsufficientNativeToken();
                    msgValue -= amount;

                    (bool sent,) = dispatcher.call{value: amount}("");
                    if (!sent) revert InsufficientNativeToken();
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, dispatcher, amount);
                }

                unchecked {
                    ++i;
                }
            }

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

**File:** evm/src/apps/IntentGatewayV2.sol (L260-311)
```text
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

            // Measure actual received, emit dust for excess, update order.inputs.
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }

                unchecked {
                    ++i;
                }
            }
```
