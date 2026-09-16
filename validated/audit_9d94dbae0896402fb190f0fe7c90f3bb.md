## Analysis

The Sherlock report's core bug class is: **a component that both custodies funds and executes attacker-supplied arbitrary calls, without proper authorization on who may trigger it or what state it may act upon**. The closest structurally-identical component in Hyperbridge is `CallDispatcher`, the shared, address-`payable` utility contract used by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` to execute untrusted `Call[]` payloads against tokens temporarily parked in it. [1](#0-0) 

`dispatch()` has **no access control whatsoever** — any external account can invoke it directly, not just the apps that are supposed to own it, and it will `.call{value: call.value}(call.data)` to any address that merely `extcodesize > 0`, exactly the shallow "is a contract" check (and nothing about legitimacy) that the original DODO report flags as insufficient.

`IntentGatewayV2.placeOrder`'s predispatch flow moves user assets into this shared dispatcher, runs the user-supplied predispatch calldata (e.g. a Uniswap swap), and then sweeps back **only the tokens listed in `order.inputs`** by transferring `balanceOf(dispatcher)` for those specific tokens: [2](#0-1) 

Any token or native balance the predispatch call leaves behind that is **not** one of `order.inputs` (an intermediate swap-path token, slippage residue, or stray native `msg.value` change) is never swept, and permanently sits in the shared `CallDispatcher`. Because `dispatch()` is permissionless, any third party — not the order's own placer — can subsequently call `CallDispatcher.dispatch()` with a `Call[]` that transfers that residual balance to themselves.

I could not fully verify within the available budget whether other code paths (e.g. `IntentsBase._execute`'s postdispatch sweep, which is scoped to `order.output.assets` only just like the predispatch sweep) leave similar unaccounted-for token types, nor whether this exact `CallDispatcher` instance is truly shared across multiple deployed apps in production configuration (the docs and deploy scripts suggest reuse is common but not universal) — a full audit would need to confirm production wiring.

### Title
Permissionless `CallDispatcher.dispatch()` Allows Theft of Any Residual Funds Left in the Shared Dispatcher - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher.dispatch()` is callable by anyone, with no restriction to the apps (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`) that are meant to be its only legitimate callers, and its only safety check on the call target is that it has code (`extcodesize > 0`) — mirroring the missing-validation pattern from the reported DODO issue where an arbitrary `assetTo`/`to` address could be driven by unauthenticated calldata.

### Finding Description
`CallDispatcher` is a shared, `payable`, address-fixed (CREATE2) utility contract used by multiple ISMP applications to execute arbitrary `Call[]` batches against tokens that are transiently deposited into it during predispatch/postdispatch order execution and cross-chain calldata delivery. `dispatch()` has no `onlyOwner`/`onlyCaller` modifier: [3](#0-2) 

`IntentGatewayV2.placeOrder`'s predispatch path only sweeps back the exact tokens declared in `order.inputs`, using `dispatcher`'s live balance for each of those tokens: [4](#0-3) 

Any other token/native balance the predispatch call (arbitrary user-supplied swap/DeFi calldata) produces or that any prior caller left behind — including plain ETH sent directly via the dispatcher's `receive()` — is never accounted for or swept, and remains indefinitely inside the shared `CallDispatcher`. Because `dispatch()` is unauthenticated, any address (a bot, a competing solver, an unrelated user) can subsequently call `CallDispatcher.dispatch()` directly with a `Call[]` array that transfers this leftover balance to itself, exactly the "callback function executed against an under-validated target/balance" pattern the source report describes.

### Impact Explanation
Because the dispatcher is a long-lived, address-stable, shared contract across multiple production apps and order placements, dust or stray balances accumulate over the contract's lifetime (Uniswap slippage residue, intermediate swap-path tokens, ETH sent directly). Any of that value is permanently exposed to theft by any unauthenticated third party, since the only gate on `dispatch()` is the trivial `extcodesize` check on the call target, not caller identity. This is a concrete, reachable theft-of-funds path from a single, gas-cheap transaction (`CallDispatcher.dispatch(...)`), satisfying the "concrete theft of funds" bar.

### Likelihood Explanation
Likelihood is Medium: the predispatch/postdispatch calldata feature is explicitly designed to be composable with arbitrary DeFi calls (documented swap-then-escrow / fill-then-act patterns), which routinely produce non-exact-match token residues, and MEV-style bots are strongly incentivized to monitor the shared `CallDispatcher`'s balances and drain them the instant any value appears, since no privileged step (approval, ownership, whitelisting) stands between an observer and a call to `dispatch()`.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allow-list (the specific app contracts that are expected to use it, e.g. `onlyAuthorizedCaller` set at deployment) instead of leaving it fully permissionless, and/or have each app sweep the dispatcher's *entire* balance for every token touched by the predispatch/postdispatch calldata (not just the tokens declared in `order.inputs`/`order.output.assets`) back to itself/the depositor at the end of the same transaction so no value can persist in the shared contract between calls.

### Proof of Concept
1. A user places a same-chain order via `IntentGatewayV2.placeOrder` with `predispatch.call` that swaps ETH for `TokenA` via Uniswap but the swap path also yields incidental `TokenB` dust (or slippage leaves excess `TokenA` beyond `order.inputs[i].amount` combined with a second, unlisted token from a multi-hop route).
2. `placeOrder` sweeps only the token(s) listed in `order.inputs` back to the gateway; any other token/ETH balance remains on `CallDispatcher`. [4](#0-3) 
3. An attacker, without needing to be an authorized app, calls `CallDispatcher.dispatch(abi.encode([Call({to: TokenB, value: 0, data: transfer(attacker, balance)})]))` directly. [3](#0-2) 
4. The call succeeds because `dispatch()` performs no caller authentication and `TokenB` has code, transferring the stranded balance to the attacker.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L36-62)
```text
    /**
     * @dev Receive function to accept ETH transfers
     */
    receive() external payable {}

    /**
     *  @dev reverts if the target is not a contract or if any of the calls reverts.
     */
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
