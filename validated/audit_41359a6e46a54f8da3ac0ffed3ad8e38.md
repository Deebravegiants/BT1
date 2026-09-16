### Title
Unrestricted `CallDispatcher.dispatch()` Lets Anyone Sweep Stray Token/ETH Balances Left on the Shared Dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` has no caller restriction of any kind — it is a bare `external` function callable by anyone. [1](#0-0)  The contract is shared across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` on every chain it's deployed to, and is documented as holding tokens/ETH temporarily while executing user- or solver-supplied `Call[]` arrays during order placement (`predispatch`) and order settlement (`output.call`). [2](#0-1) [3](#0-2)  The sweep logic that returns balances from the dispatcher back to the gateway only accounts for the specific tokens declared in `order.inputs`/`order.output.assets`; any other token or leftover balance that ends up on the dispatcher (multi-hop swap remainders, fee-on-transfer dust, partially-filled DEX routes, failed/partial sweeps) is never returned and is left sitting on the contract indefinitely. [4](#0-3)  Because `dispatch()` is permissionless, any unprivileged actor can subsequently call it directly with a `Call{to: strayToken, data: transfer(attacker, balance)}` and drain whatever balance remains, since the low-level call executes with `msg.sender == CallDispatcher`. [5](#0-4) 

### Finding Description
`CallDispatcher` is intentionally generic — it decodes an ABI-encoded `Call[]` and executes each entry via a low-level `.call` in its own storage/msg.sender context (not `delegatecall`), checking only that the target has code. [5](#0-4)  This design is safe as long as (a) the dispatcher never holds a balance outside of a single atomic transaction, and (b) only the intended app can invoke `dispatch()` while a balance is present. Neither guarantee is enforced in code:

- `dispatch()` carries no `onlyGateway`/`onlyHost`/access-control modifier at all — it is fully public. [6](#0-5) 
- In `IntentGatewayV2.placeOrder`, the predispatch flow sends assets to the dispatcher, executes the user-supplied `predispatch.call`, then sweeps back only the balances of tokens explicitly listed in `order.inputs`, using a before/after balance diff scoped to those tokens. [7](#0-6)  Any other token touched by the predispatch call's swap route (e.g., an intermediate hop token, or a token with rounding/rebasing behavior) is not measured and not swept — it stays on the dispatcher.
- In `IntentsBase._execute`, the postdispatch sweep is likewise scoped only to `order.output.assets`, again leaving any non-listed token balance behind on the dispatcher. [3](#0-2) 
- The documentation itself acknowledges the dispatcher accumulates balances it does not fully account for, and explicitly warns callers to avoid unlimited approvals in their `Call[]` "since the dispatcher contract holds tokens temporarily during execution," confirming the design assumes — but does not enforce — that no value is left behind or reachable by outsiders. [8](#0-7) 

Because the same `CallDispatcher` instance is shared by every order/transfer across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken` on a chain, any stray balance left by one user's order becomes fair game for a subsequent unrelated, unprivileged caller. That caller needs no special role — they simply call `CallDispatcher.dispatch(abi.encode(Call[](...)))` with a `Call` targeting the stray token contract (or the native-ETH `to: attacker` transfer), and the call executes as `msg.sender == CallDispatcher`, moving out whatever the dispatcher holds. [5](#0-4) 

### Impact Explanation
This is a concrete theft-of-funds path reachable by any unprivileged party (an intent solver, a bystander MEV bot, or any address willing to send a transaction) with no permission requirements. The value at risk is real user/solver escrow and swap-route residue routed through the shared, protocol-wide `CallDispatcher`. Because the contract is reused across all `IntentGatewayV2` orders, `HyperFungibleToken` sends, and `WrappedHyperFungibleToken` sends on a chain, the blast radius is not scoped to a single order — any stray balance from any user's order is exposed to any other address. This qualifies as concrete theft of funds under the "unprivileged intent solver / token bridger" reachability requirement.

### Likelihood Explanation
Likelihood is moderate-to-high: multi-hop swap routes, DEX slippage, fee-on-transfer tokens, or partial-fill DEX behavior are routine, non-adversarial occurrences in `predispatch`/`postdispatch` calldata, and any of them can leave an unaccounted token balance on the dispatcher. Once any balance lands there, exploitation requires nothing more than a single permissionless call to `dispatch()` — no proof, no relayer, no privileged role, and no race condition beyond simply observing the dispatcher's balance (e.g., via a public RPC or event) and submitting a transaction.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to a caller allow-list (e.g., the registered `IntentGatewayV2`/`HyperFungibleToken`/`WrappedHyperFungibleToken` instances) rather than leaving it fully public.
- Ensure predispatch/postdispatch sweep logic fully drains the dispatcher of *all* tokens touched during execution (not just the tokens declared in `order.inputs`/`order.output.assets`), or require calldata to explicitly declare every token it may produce so sweeps are exhaustive.
- Consider using a fresh, single-use `CallDispatcher`-like execution context per order (e.g., via `CREATE2`/ephemeral proxy) so no balance can ever persist beyond a single atomic transaction, removing the shared-contract attack surface entirely.

### Proof of Concept
1. A user places an order via `IntentGatewayV2.placeOrder` with `predispatch.call` performing a multi-hop swap (e.g., USDC → WETH → DAI) where an intermediate-hop token (WETH) is not listed in `order.inputs` (only DAI is). [9](#0-8) 
2. Due to slippage/rounding, a small residual WETH balance remains on the `CallDispatcher` after the swap; the subsequent sweep only measures/moves DAI (the declared input token), leaving the WETH balance behind. [4](#0-3) 
3. Any unprivileged third party observes `WETH.balanceOf(CallDispatcher) > 0` and calls `CallDispatcher.dispatch(abi.encode([Call({to: WETH, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, balance)})]))` directly. [5](#0-4) 
4. Since `dispatch()` has no access control and the low-level call is made from `CallDispatcher` itself, `WETH.transfer` succeeds with `msg.sender == CallDispatcher`, and the residual balance is stolen — with no relationship to the original order or its owner.

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

**File:** evm/src/apps/IntentGatewayV2.sol (L235-311)
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
