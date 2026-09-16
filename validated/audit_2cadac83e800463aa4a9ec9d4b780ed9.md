Confirmed: `CallDispatcher.dispatch(bytes memory encoded)` at [1](#0-0)  has no access-control modifier whatsoever — it is a bare `external` function callable by anyone, unlike every other cross-chain callback in this codebase (`onAccept`, `onPostRequestTimeout`, etc.) which is gated by `onlyHost` as documented at [2](#0-1) . The docs themselves warn that `Call[]` entries "should use exact amounts rather than unlimited allowances" but this is only a recommendation, not enforced on-chain: [3](#0-2) . Both `HyperFungibleTokenUpgradeable.onAccept` and `IntentsBase._execute` route arbitrary attacker/solver-supplied calldata through this same shared, unprotected dispatcher: [4](#0-3) [5](#0-4) , and the docs' own worked examples set `type(uint256).max` approvals inside these calls (e.g. Uniswap router approve): [6](#0-5) .

### Title
Unauthenticated, shared `CallDispatcher.dispatch` lets anyone weaponize residual approvals left by legitimate calldata-execution flows - (File: evm/src/utils/CallDispatcher.sol)

### Summary
`CallDispatcher` is a single shared, stateless-by-convention contract used by `HyperFungibleToken`/`HyperFungibleTokenUpgradeable` (`onAccept`) and `IntentGatewayV2`/`IntentsBase` (`_execute`, predispatch) to run attacker/solver-supplied `Call[]` batches on behalf of bridged/filled funds. Its `dispatch(bytes)` function performs an arbitrary low-level `to.call{value: call.value}(call.data)` for each entry, and — unlike every other cross-chain entrypoint in the codebase — has **no caller restriction at all**: not `onlyHost`, not `onlySelf`, not even a reentrancy/one-shot guard. This mirrors the BasketDAO root cause: "an arbitrary low-level call in the approval process" reachable without authorization.

### Finding Description
Every ISMP/host callback in this codebase (`onAccept`, `onPostRequestTimeout`, `onGetResponse`, etc.) is explicitly gated with `onlyHost`, as documented and enforced in `HyperApp` ( [2](#0-1) ) and reiterated as a security requirement in the docs ( [7](#0-6) ). `CallDispatcher`, however, is the one contract in the trust chain that executes arbitrary low-level calls with **zero access control**:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
```
( [1](#0-0) )

This same `CallDispatcher` instance is shared across all callers of `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` on a chain (per the deployment addresses listed in `docs/content/developers/evm/contract-addresses/*`). Legitimate flows deliberately route calldata that performs `approve()` with `type(uint256).max` through the dispatcher — the docs' own canonical example does exactly this against Uniswap's router ( [8](#0-7) ), and `IntentGatewayV2Test.sol` mirrors the same unlimited-approval pattern for postdispatch swaps ( [9](#0-8) ). The docs concede the risk only as an informal recommendation ("should use exact amounts rather than unlimited allowances") rather than an enforced invariant ( [3](#0-2) ).

Because `dispatch()` is callable directly by anyone — not only by `HyperFungibleTokenUpgradeable.onAccept` ( [10](#0-9) ) or `IntentsBase._execute` ( [5](#0-4) ) — any standing token allowance the dispatcher accumulates from a prior legitimate batch (e.g., an unrevoked max-approval to a router, or an approval whose swap did not fully consume it) is directly reachable by an unprivileged attacker. The attacker simply calls `CallDispatcher.dispatch()` themselves with a `Call[]` invoking `transferFrom`/`swapExactTokensForTokens`-style functions against the approved spender, redirecting the residual allowance (and any dust ERC20/native balance sitting in the dispatcher between the approve/swap sub-call and the sweep-back step) to an address they control.

### Impact Explanation
Any bridged HFT calldata-execution transfer or any intent-gateway order with postdispatch/predispatch calldata that leaves a non-zero standing allowance on the `CallDispatcher` (unlimited approvals, or exact approvals that a partially-executed/aborted downstream call did not fully consume) creates a window where an unrelated third party can call the public `dispatch()` directly and drain that allowance or any transient token/native balance to themselves. Given the dispatcher is shared infrastructure across `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` deployments, a single instance of over-permissive calldata (as shown in the project's own documentation and tests) becomes a standing attack surface for every subsequent transaction that touches the same dispatcher, resulting in theft of bridged/escrowed funds. This is Medium severity: exploitability is conditional on a preceding calldata batch leaving residual approvals/dust, but the codebase's own reference examples and tests actively encourage that exact pattern.

### Likelihood Explanation
Likelihood is elevated because: (1) the vulnerable function requires no privileged role or proof — a plain EOA transaction suffices; (2) the documented and tested usage pattern for calldata execution (approve `type(uint256).max` then swap) is precisely the pattern that leaves an exploitable allowance; (3) `CallDispatcher` is a single shared contract reused by many independent bridging/intent-fill transactions, so exposure accumulates over time and across unrelated users' transfers.

### Recommendation
Restrict `CallDispatcher.dispatch` to a caller allow-list (e.g., `onlyAuthorizedCaller` mapping maintained by governance, or make it a per-app immutable singleton not shared across apps), and/or make the dispatcher strictly single-use/ephemeral (deploy a fresh minimal-proxy dispatcher per call so no state or allowance can persist across transactions). At minimum, enforce that any approval granted during `dispatch()` is revoked (set back to zero) before the call returns, and document/require exact-amount approvals as a hard on-chain invariant rather than a recommendation.

### Proof of Concept
1. A user bridges tokens via `HyperFungibleTokenUpgradeable.send()` with calldata that, on `onAccept`, has the `CallDispatcher` execute `IERC20(TOKEN).approve(ROUTER, type(uint256).max)` followed by a swap — exactly the pattern shown in the project's own docs ( [8](#0-7) ).
2. The swap consumes less than the full allowance (e.g., due to slippage bounds or partial routing), leaving `CallDispatcher` with a nonzero, unlimited allowance to `ROUTER`.
3. An attacker, with no relationship to the original transfer, directly calls `CallDispatcher.dispatch(abi.encode(Call[]))` where the `Call` targets `ROUTER`/`TOKEN` and moves funds using the dispatcher's residual allowance to an attacker-controlled address — no `onlyHost`/`onlySelf` check in `CallDispatcher.dispatch` ( [1](#0-0) ) prevents this call from succeeding.

### Citations

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

**File:** sdk/packages/core/contracts/apps/HyperApp.sol (L56-62)
```text
    /**
     * @dev restricts caller to the local `Host`
     */
    modifier onlyHost() {
        if (msg.sender != host()) revert UnauthorizedCall();
        _;
    }
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L327-333)
```text
        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L126-147)
```text
Call[] memory calls = new Call[](2);

// Approve UniswapV2 router
calls[0] = Call({
    to: DEST_TOKEN,
    value: 0,
    data: abi.encodeWithSelector(IERC20.approve.selector, UNISWAP_V2_ROUTER, amount)
});

// Swap via UniswapV2
calls[1] = Call({
    to: UNISWAP_V2_ROUTER,
    value: 0,
    data: abi.encodeWithSelector(
        IUniswapV2Router02.swapExactTokensForTokens.selector,
        amount,
        minAmountOut,
        path,
        recipientAddress,
        block.timestamp
    )
});
```

**File:** docs/content/developers/evm/messaging/receiving.mdx (L79-91)
```text
## Security Considerations

**Critical:** Always restrict callbacks to the `IHost` contract using the `onlyHost` modifier. This prevents unauthorized execution of cross-chain messages. `HyperApp` provides this modifier automatically.

```solidity lineNumbers
function onAccept(IncomingPostRequest calldata incoming) 
    external 
    override 
    onlyHost  // Required for security
{
    // Your logic here
}
```
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L1358-1363)
```text
        // Call 1: Approve Uniswap router
        postdispatchCalls[0] = Call({
            to: address(usdc),
            value: 0,
            data: abi.encodeWithSelector(IERC20.approve.selector, uniswapRouter, type(uint256).max)
        });
```
