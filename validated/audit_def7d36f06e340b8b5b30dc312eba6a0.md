### Title
Unrestricted `CallDispatcher.dispatch()` lets anyone drain tokens the dispatcher accumulates outside the enumerated sweep list — (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is a fully public, unauthenticated entry point that executes attacker-supplied `Call[]` (arbitrary `to`/`value`/`data`) from the dispatcher's own context, with no caller restriction and no reentrancy guard. [1](#0-0)  `IntentGatewayV2`/`IntentsBase` and the `HyperFungibleToken`/`WrappedHyperFungibleToken` apps route escrowed/solver funds through this shared dispatcher during `predispatch`/`postdispatch` and `onAccept` calldata execution, then sweep back only the balances of tokens explicitly enumerated in the order (`order.inputs` / `order.output.assets`). [2](#0-1)  Any token balance the dispatcher ends up holding that is *not* on that enumerated list (e.g., an intermediate/reward token from a swap, WETH remainder, dust from a partial/odd-lot conversion, or plain ETH force-sent via `receive()`) [3](#0-2)  is never swept and stays parked on the dispatcher indefinitely — retrievable by literally anyone, since `dispatch()` performs no `msg.sender` check.

### Finding Description
`CallDispatcher` is explicitly designed to be a stateless pass-through: it "dispatch[es] untrusted call(s)" and is meant to only hold funds transiently for the duration of one predispatch/postdispatch execution. [4](#0-3)  Its `dispatch(bytes)` function has no access-control modifier of any kind — it decodes the caller-supplied `Call[]` and blindly `.call{value: call.value}(call.data)`s each target. [1](#0-0) 

The intents flow relies entirely on the *caller* (`IntentsBase`/`IntentGatewayV2`) to compute what needs to be swept back, based only on the token set the order declares up front:
- In `placeOrder`'s predispatch path, the gateway snapshots `IERC20(token).balanceOf(dispatcher)` only for tokens listed in `order.inputs`, and only sweeps those. [5](#0-4) 
- In `_execute` (postdispatch, used by both same-chain and cross-chain fills), after running `order.output.call` the sweep loop only iterates `order.output.assets`, checking `dispatcher.balance` and `IERC20(token).balanceOf(dispatcher)` for each declared output token. [2](#0-1) 

Because `order.predispatch.call` / `order.output.call` are attacker-controllable calldata (the order creator freely composes them, e.g. arbitrary DEX router calls, per the documented "swap-then-escrow"/"fill-then-act" patterns) [6](#0-5) , it is trivial for an order creator to route a swap through a path that leaves a reward/side token, rounding remainder, or unwrapped-native leftover on the dispatcher that is not one of the declared `inputs`/`output.assets` tokens. That balance is then permanently un-swept by the protocol's own logic, yet remains sitting on `CallDispatcher`, a single shared/canonical contract instance used by every app and order across the chain. [7](#0-6) 

Since `dispatch()` has zero caller restriction, any unrelated, unprivileged third party can simply call `CallDispatcher.dispatch()` directly with `Call{to: strandedToken, data: transfer(attacker, balance)}` (or `Call{to: attacker, value: dispatcher.balance}` for stray native ETH) and pull out any value stranded there — value that rightfully belongs to the protocol (as "dust") or to whichever order left it behind. This mirrors the reported bug class: a callback/executor meant to be reachable only through a controlled flow is instead callable by anyone with arbitrary calldata, and the executing contract can end up holding funds outside its own accounting, which the arbitrary call can then exfiltrate.

### Impact Explanation
Any value left on the shared `CallDispatcher` — dust from imperfect sweeps, reward tokens from postdispatch/predispatch DEX routes, or plain force-sent ETH — is a bounty for any unprivileged address, permanently and independent of protocol governance. Because `CallDispatcher` is shared across all `IntentGatewayV2` orders and both `HyperFungibleToken`/`WrappedHyperFungibleToken` apps on a chain, this is not confined to a single user's mistake: it is a standing, permissionless drain vector on protocol/user value that the contract itself is supposed to safeguard until swept ("collected as dust").

### Likelihood Explanation
High for creation of the stranded balance: any order creator (fully unprivileged) can design `predispatch.call`/`output.call` to leave a non-enumerated token or native remainder on the dispatcher — this requires no special access, only crafting one's own order with a swap path producing a side-output. Extraction is then trivial and permissionless: `CallDispatcher.dispatch()` can be called directly by anyone at any later block with a single crafted `Call[]`.

### Recommendation
1. Restrict `CallDispatcher.dispatch()` to an allow-listed set of trusted callers (the specific gateway/token contracts), or scope dispatcher instances per-caller/per-call so no shared, globally-drainable balance can accumulate.
2. Add a reentrancy guard to `dispatch()`.
3. After each dispatch cycle, sweep *all* residual balances (not just the ones enumerated in `order.inputs`/`order.output.assets`) back to the calling contract, e.g. by tracking every token touched during the call batch, or by disallowing any call target from leaving unaccounted balances.
4. Consider making the dispatcher immutable-per-call (e.g., deployed fresh via `CREATE2`/`create` per invocation and self-destructing/becoming inert after use) so stray balances cannot persist across transactions for third parties to claim.

### Proof of Concept
1. Attacker (as order creator) calls `IntentGatewayV2.placeOrder` with `predispatch.assets = [TOKEN_A: X]` and `predispatch.call` encoding a swap of `TOKEN_A` into `TOKEN_B` and `TOKEN_C` on some router, where `order.inputs` only declares `TOKEN_B` (the amount needed for escrow).
2. `placeOrder`'s predispatch flow transfers `TOKEN_A` to `CallDispatcher`, runs the swap via `dispatch(order.predispatch.call)`, then only sweeps `TOKEN_B` back to the gateway per `order.inputs` — `TOKEN_C` remains stranded on `CallDispatcher`. [8](#0-7) 
3. Any third party (no relation to the order) calls `CallDispatcher.dispatch(abi.encode([Call({to: TOKEN_C, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, TOKEN_C.balanceOf(dispatcher))})]))` directly. [1](#0-0) 
4. Because `dispatch()` has no caller check, the call succeeds and `TOKEN_C` is transferred to the attacker — value that should have been recorded as protocol dust or returned to the order, permanently lost from the protocol's accounting.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-39)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}
```

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

**File:** sdk/packages/core/contracts/interfaces/ICallDispatcher.sol (L26-37)
```text
/**
 * @title The ICallDispatcher
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @notice This interface is used to dispatch untrusted call(s)
 */
interface ICallDispatcher {
    /*
     * @dev Dispatch the encoded call(s)
     */
    function dispatch(bytes memory params) external;
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

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L99-112)
```text
### Predispatch

The `predispatch` field in `Order` contains calldata to execute *before* escrowing inputs. The predispatch assets specified in `DispatchInfo.assets` are transferred to the `CallDispatcher`, the encoded calls are executed, and the resulting tokens are transferred back to the gateway for escrow. This enables swap-then-escrow patterns — for example, a user sends ETH which the `CallDispatcher` swaps to DAI on Uniswap, and the resulting DAI is escrowed as the order input.

### Postdispatch

The `call` field in `PaymentInfo` contains calldata to execute *after* the order is filled. This enables fill-then-act patterns — for example, output tokens received from the solver are routed through a DeFi protocol before reaching the beneficiary.

Execution timing differs by mode:

- **Same-chain**: Calldata executes only after the order is **fully filled**. Partial fills do not trigger calldata — only the final fill that completes the order executes it. This ensures all output tokens are available when the calls run.
- **Cross-chain**: Calldata executes **immediately** after the solver delivers output tokens to the beneficiary, before the settlement message is dispatched back to the source chain.

After execution, any tokens remaining in the `CallDispatcher` are swept back to the gateway and collected as dust (emitting `DustCollected` for each token). When postdispatch calldata is present, 100% of any surplus (solver overpayment) goes to the protocol rather than being split with the beneficiary — this prevents manipulation of surplus distribution through calldata side effects.
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
