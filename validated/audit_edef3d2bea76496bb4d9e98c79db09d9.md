### Title
Missing Reentrancy Protection in Tron IntentGatewayV2 Escrow Path — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron port of the intents gateway, `evm/tron/contracts/apps/IntentGatewayV2.sol`, reimplements the escrow/order lifecycle (`placeOrder`, `withdraw`, `onAccept`) as a monolithic contract but drops the `nonReentrant` guard and the checks-effects-interactions (CEI) hardening that the canonical EVM implementation applies to the same logic. This mirrors the class of bug behind the Alchemix/Curve incident: a reentrancy protection that exists in one code path/version but is missing or broken in a sibling deployment of logically identical pool/escrow code, letting an attacker drain funds mid-operation.

### Finding Description
In the primary EVM app, `placeOrder` is explicitly marked `nonReentrant` and the fill/withdraw internals (`IntrinsicIntents`, `ExtrinsicIntents`, `IntentsBase._withdraw`) were hardened with a CEI fix — `_filled[commitment]` is written before any external call, as documented in the dedicated regression suite: [1](#0-0) [2](#0-1) 

By contrast, the Tron variant's `placeOrder` has no reentrancy guard at all: [3](#0-2) 

and a `grep` across the entire `evm/tron/contracts/**/*.sol` tree confirms zero occurrences of `nonReentrant` or `ReentrancyGuard` anywhere in the Tron port, whereas the canonical contract explicitly imports and applies it.

`placeOrder` on Tron performs external calls — `ICallDispatcher(dispatcher).dispatch(order.predispatch.call)` and `IERC20.safeTransferFrom` — in the middle of the function, before escrow bookkeeping (`_orders[commitment][token] += reducedInputs[i].amount`) and before the commitment/nonce state is finalized: [4](#0-3) 

Because `_nonce` is incremented and read without any lock, and the dispatcher call can invoke arbitrary logic (including callbacks from an attacker-controlled `predispatch.call` payload or a malicious ERC-777/callback-style token used as an input), a reentrant call into `placeOrder`, `withdraw`-triggering `onAccept`, or the GET-response handler can interleave with in-flight escrow accounting. The `withdraw` function itself does apply CEI (`_filled[body.commitment] = beneficiary` set before the transfer loop) at line 693, so the redemption path alone is not exploitable in isolation, but the absence of a contract-wide `nonReentrant` lock means the hardening applied to the canonical EVM contract's escrow lifecycle (informed by exactly this class of external-call-ordering bug) was not carried over to the Tron deployment, leaving the composed order-placement + predispatch-execution flow without the equivalent protection.

### Impact Explanation
An attacker with a crafted `predispatch.call` (routed through `ICallDispatcher`) or a malicious/fee-on-transfer-with-callback input token can reenter the gateway during `placeOrder`'s external dispatch/transfer calls. Since no `nonReentrant` modifier exists to block this on Tron (unlike the audited EVM contract), this can be leveraged to manipulate escrow bookkeeping across concurrent order placements/fills, enabling theft of escrowed input tokens or fee tokens intended for solvers — the same class of "unprivileged actor reaches a token-custody state machine via a single transaction, exploiting a missing reentrancy protection" as the Curve/Alchemix incident.

### Likelihood Explanation
Medium-High. `placeOrder` is reachable by any unprivileged user with a single transaction, and the `predispatch.call` mechanism intentionally allows arbitrary external dispatch (per its documented purpose of "unwrapping LP tokens" etc.), which combined with the total absence of any reentrancy guard on the Tron contract makes the attack surface directly reachable without special privileges.

### Recommendation
Add a `nonReentrant` guard (OpenZeppelin `ReentrancyGuard`) to `placeOrder`, `withdraw`, and `onAccept`/`onGetResponse` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, matching the protection already present in `evm/src/apps/IntentGatewayV2.sol`, and audit the predispatch/dispatch flow to ensure escrow accounting (`_orders[commitment][token] +=`) is finalized before any external call that could reenter the contract.

### Proof of Concept
Not independently reproducible from the indexed context — the full body of `fillOrder`/`onAccept` reentrancy paths in the Tron contract was not fully retrievable within the available context window, so the exact reentrant call sequence and its balance-check bypass could not be fully traced end-to-end. The concrete, verifiable root cause is the confirmed absence of `nonReentrant`/`ReentrancyGuard` in `evm/tron/contracts/apps/IntentGatewayV2.sol` contrasted with its explicit presence in `evm/src/apps/IntentGatewayV2.sol:194`, combined with `placeOrder`'s external calls preceding escrow-state finalization at `evm/tron/contracts/apps/IntentGatewayV2.sol:387-446`.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L194-194)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable nonReentrant {
```

**File:** evm/tests/foundry/IntrinsicIntentsReentrancyTest.sol (L36-49)
```text
 *
 * Attack window (pre-fix):
 *
 *   _fillSameChain / _fillCrossChain:
 *     beneficiary.call{value: ...}("")   ← RE-ENTRY HERE
 *     // _filled still == address(0) pre-fix, now set at the top (CEI)
 *
 * With the CEI fix in place, `_filled[commitment]` is set to `msg.sender` at the
 * very start of both fill functions. Any reentrant `fillOrder` call therefore hits
 * the `if (_filled[commitment] != address(0)) revert Filled()` guard and reverts.
 * That revert propagates through `receive()`, causing the outer ETH transfer to
 * return `(false, ...)`, which triggers `InsufficientNativeToken()` in the outer
 * call — rolling back all state changes atomically.
 */
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L338-346)
```text
    function placeOrder(Order memory order, bytes32 graffiti) public payable {
        // Validate that order has inputs
        if (order.inputs.length == 0) revert InvalidInput();

        address hostAddr = host();
        // fill out the order preludes
        order.user = bytes32(uint256(uint160(msg.sender)));
        order.source = IDispatcher(hostAddr).host();
        order.nonce = _nonce++;
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L387-446)
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
