### Title
Unauthenticated `CallDispatcher.dispatch()` allows anyone to drain token/ETH balances left in the shared dispatcher contract - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The dTRINITY incident lost funds because a *swap adapter contract* held balances/approvals that an unprivileged caller was able to trigger for their own benefit. Hyperbridge's `IntentGatewayV2` uses an analogous shared, unprivileged "swap adapter" helper — `CallDispatcher` — to execute predispatch/postdispatch calldata (approve-then-swap-then-transfer sequences) on behalf of orders [1](#0-0) . `CallDispatcher.dispatch()` itself has no caller restriction whatsoever, and it is a single, reusable contract for *every* order in the protocol.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` is `external` with no `onlyGateway`/`msg.sender` check of any kind — any address can invoke it directly with an arbitrary `Call[]` array, and it will execute those calls using whatever ETH/token balance and pre-existing ERC-20 approvals the `CallDispatcher` contract currently holds: [2](#0-1) 

The docs confirm `CallDispatcher` is a **shared singleton** used across all orders, both for predispatch (swap-then-escrow) and postdispatch (fill-then-act) calldata, and that it routinely holds real ERC-20 balances (predispatch assets, solver output tokens) between the transfer-in step and the execution of the encoded calls: [3](#0-2) 

Order calldata is free to include unlimited-approval patterns such as `IERC20.approve(router, type(uint256).max)` against `CallDispatcher`'s own balance, as demonstrated in the test suite's postdispatch sweep scenario: [4](#0-3) 

Because (a) `CallDispatcher` is one contract shared by every order, (b) order calldata can leave standing `type(uint256).max` approvals to arbitrary spenders, and (c) only tokens explicitly enumerated in `DispatchInfo.assets` / `PaymentInfo.assets` get swept back to the gateway as "dust" after execution, any token balance that lands on `CallDispatcher` outside that enumerated set (e.g., swap-router refunds, multi-hop intermediate tokens, or amounts left over from a previous order's calls that failed to get swept) remains sitting on the contract. Because `dispatch()` has no access control, **anyone** — not just `IntentGatewayV2` — can call `CallDispatcher.dispatch()` directly with calldata that transfers out any such residual balance, or that exercises a leftover `approve(..., max)` grant to pull tokens out via the previously-approved spender, redirecting them to an attacker-chosen recipient.

This mirrors the dTRINITY root cause: a swap-adapter-style contract accumulating balances/approvals that an unprivileged actor could trigger for personal gain, rather than the protocol's intended flow.

### Impact Explanation
Any ERC-20 or ETH balance left on `CallDispatcher` (dust from swaps, leftover approvals from prior orders' predispatch/postdispatch calldata, or improperly swept residues) is permanently and trivially stealable by any unprivileged address, with no need to interact with `IntentGatewayV2` at all. This is a direct theft-of-funds vector reachable from a single, unauthenticated transaction, satisfying the "concrete theft ... of funds" bar. Severity is Medium-to-High depending on how much value typically transits/lingers in the shared dispatcher (analogous to dTRINITY's ~$56k loss from adapter-held funds).

### Likelihood Explanation
Likelihood is High for triggering the primitive (calling `dispatch()` costs nothing and requires no special conditions), though the magnitude of loss depends on how much dust/approval residue realistically accumulates on `CallDispatcher` in production given the documented sweep-back behavior. Any deviation from perfect sweeping (unlisted output tokens, swap refunds, reentrant/partial execution paths, or malicious calldata deliberately routed through unlisted tokens) creates an immediately exploitable window, since exploitation requires only one direct call — no auction participation, no order placement, no relayer/proof interaction.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to be callable only by the authorized gateway contract(s) (e.g., an `onlyGateway`/`onlyAuthorized` modifier configured at construction), or
- Make `CallDispatcher` per-order/ephemeral (e.g., deployed via `CREATE2`/minimal proxy per order and self-destructing or being fully swept-and-revoked at the end of every call sequence) so no state/approvals persist between orders, and
- Explicitly `approve(spender, 0)` immediately after any bounded/one-shot approval within the same calldata sequence, and sweep *all* token balances the dispatcher could plausibly touch (not just the enumerated asset list) before returning control.

### Proof of Concept
1. Order A's postdispatch calldata (as in `testPostdispatchTokenSweep`) has `CallDispatcher` call `token.approve(uniswapRouter, type(uint256).max)` and perform a swap, per [5](#0-4) . Suppose the swap over-refunds or a downstream call leaves `token` dust on `CallDispatcher` that is not among the assets enumerated for sweep-back.
2. An attacker, with no relationship to Order A, calls `CallDispatcher.dispatch(encoded)` directly (per [2](#0-1) ) with `encoded` decoding to `Call({ to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, dustAmount) })`.
3. Since `dispatch()` performs no caller check, the call succeeds and transfers the residual `token` balance to the attacker — funds that belonged to the protocol/other users, exactly analogous to the dTRINITY swap-adapter drain.

### Citations

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L85-97)
```text
## Calldata

Orders support arbitrary calldata execution at two points in the lifecycle — before escrow (predispatch) and after fill (postdispatch). Both are executed through the `CallDispatcher` contract, which takes an ABI-encoded `Call[]` array:

```solidity
struct Call {
    address to;      // Target contract (must have code, reverts with NotContract otherwise)
    uint256 value;   // ETH to send with call
    bytes data;      // Calldata to execute
}
```

The `CallDispatcher` executes each call sequentially and reverts the entire batch if any call fails.
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1358-1382)
```text
        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });

        // Call 2: Exact output swap - swap USDC for exactly 1000 DAI
        postdispatchCalls[1] = Call({
            to: uniswapRouter,
            value: 0,
            data: abi.encodeWithSelector(
                bytes4(keccak256("swapTokensForExactTokens(uint256,uint256,address[],address,uint256)")),
                daiOutputAmount, // exact amount out
                type(uint256).max, // max amount in
                path,
                address(dispatcher), // tokens come back to dispatcher
                block.timestamp
            )
        });

        // Call 3: Transfer DAI to user
        postdispatchCalls[2] = Call({
            to: address(dai), value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, user, daiOutputAmount)
        });
```
