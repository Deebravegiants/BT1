### Title
`CallDispatcher.dispatch()` is a permissionless arbitrary-call primitive that can drain any residual token approval or balance it holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The Auctus exploit abused `ACOWriter.write()`, a function that let anyone trigger an arbitrary low-level `call` (attacker-chosen target + calldata) from the writer contract's own context, which was then used to invoke `transferFrom` against a victim who had previously approved the writer as spender. Hyperbridge's `CallDispatcher` contract exposes the exact same primitive: `dispatch(bytes memory encoded)` is `external` with **no caller restriction at all** — no `onlyHost`, no `onlyGateway`, no `msg.sender` allow-list — and simply loops over an attacker-supplied `Call[]` array, issuing `to.call{value: call.value}(call.data)` for each entry.

### Finding Description
`CallDispatcher.dispatch` decodes the caller-supplied bytes into `Call[]` and executes each one with the CallDispatcher itself as `msg.sender`, without any check on who is calling `dispatch`: [1](#0-0) 

This contract is intentionally shared/singleton across multiple apps — `HyperFungibleToken`/`WrappedHyperFungibleToken` forward user-controlled cross-chain `data` payloads to it after minting/unlocking tokens: [2](#0-1) 

and `IntentGatewayV2` forwards user-controlled `predispatch.call` / `output.call` payloads to it during order placement and fill, immediately followed by "sweep" calls that transfer the dispatcher's token/ETH balance back to the gateway: [3](#0-2) [4](#0-3) 

Because `dispatch()` has zero access control, any unrelated third party can invoke it directly with their own `Call[]`, targeting the CallDispatcher's own current state:
- The dispatcher's `receive()` is unconditionally payable, so anyone can push ETH into it, and any ETH/ERC20 balance currently sitting on the dispatcher — even balances placed there mid-flow by another app's transaction — can be swept out by a Call such as `{to: token, data: transfer(attacker, balance)}`, since the token contract sees `msg.sender == dispatcher` (the true owner of that balance).
- The documented "approve then swap" composable pattern explicitly has flows push a `Call` that does `IERC20(token).approve(router, amount)` from the dispatcher. The project's own docs flag this as risky: "Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution." Any residual/unconsumed allowance left on the dispatcher toward a router remains valid indefinitely and is not scoped to the originating transaction, because nothing revokes it and no caller check prevents anyone from later interacting with that allowance-bearing router/token pair on behalf of the dispatcher via more `dispatch()` calls. [5](#0-4) 

This is structurally identical to the Auctus bug class: an externally reachable function that executes an arbitrary `(target, value, data)` triple with the calling contract's own identity/privileges, with no restriction on who may invoke it or what it targets.

### Impact Explanation
Because the CallDispatcher is a shared, cross-app singleton (used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` simultaneously, per the "Existing `CallDispatcher` deployments" contract-addresses reference), any value it transiently holds — stray ETH from `receive()`, ERC20 dust from a partially-consumed batch, or a router allowance left over-provisioned by any app's Call sequence — is directly stealable by an unrelated address simply calling `dispatch()` with its own `Call[]`. This is a concrete theft-of-funds vector reachable by a single unprivileged transaction, matching the required "concrete theft ... of funds" bar.

### Likelihood Explanation
Likelihood is tied to whether the dispatcher ever holds exploitable state outside of a single atomic transaction. The happy-path flows (`IntentsBase._execute`, `IntentGatewayV2` predispatch/postdispatch) sweep balances back to the gateway within the same transaction, but (a) the `receive()` function accepts ETH unconditionally at any time from anyone, and (b) the docs explicitly acknowledge that unlimited/over-provisioned ERC20 approvals left by a `Call[]` are a real risk pattern the integrator must avoid manually — i.e., the contract itself provides no on-chain protection against this, relying entirely on off-chain caller discipline. Given the function is called with user-supplied `data` from multiple independent, permissionless entry points (HFT `send()`, intent order placement), the probability that some flow leaves an exploitable balance/allowance is non-trivial and is aggravated by `dispatch()`'s complete lack of access control.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to a fixed set of authorized callers (e.g., an `onlyAuthorizedCaller` allow-list of the HFT/WrappedHFT/IntentGatewayV2 instances that legitimately use it), or deploy per-app/per-call ephemeral dispatchers instead of a shared singleton.
- Enforce exact-amount approvals (no unlimited allowances) at the contract level rather than relying purely on documentation guidance, or auto-revoke approvals granted during a `dispatch()` batch at the end of execution.
- Consider guarding `receive()` or sweeping any dispatcher balance at the start of `dispatch()` to the caller-designated recipient, so no value can persist on the dispatcher between transactions.

### Proof of Concept
1. Any legitimate order/message flow (e.g., an `IntentGatewayV2` predispatch swap) sends a `Call` through `CallDispatcher.dispatch()` that includes `IERC20(token).approve(router, largeAmount)` before swapping, per the documented "approve then swap" pattern.
2. If `largeAmount` exceeds what the swap consumes (or the swap partially fails within its own bounds), a residual allowance `token.allowance(dispatcher, router)` remains.
3. An attacker directly calls `CallDispatcher.dispatch(abi.encode(Call[]{ {to: router_or_token, value: 0, data: <calldata redirecting dispatcher's tokens/allowance to attacker>} }))` — this succeeds because `dispatch()` performs no caller check: [6](#0-5) 
4. Funds/allowance held by the shared CallDispatcher are extracted to the attacker, exactly mirroring how Auctus's `write()` let an attacker trigger `transferFrom` using the ACOWriter's pre-existing approval.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L326-328)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-96)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
