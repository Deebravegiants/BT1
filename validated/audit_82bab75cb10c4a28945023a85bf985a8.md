## Title
Permissionless `CallDispatcher.dispatch()` allows anyone to drain residual token balances and exploit dangling approvals left by other users' cross-chain calldata - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is a completely unrestricted, `external` entry point with no caller check at all — any address can invoke it with an arbitrary ABI-encoded `Call[]` and force the shared `CallDispatcher` contract to execute calls to any target with any calldata and value. This is the same bug class as the Polynomial Protocol `swapAndDeposit()` incident: a helper contract that executes attacker-supplied calls with no restriction on the caller or on which funds/approvals it may act upon. [1](#0-0) 

### Finding Description
`CallDispatcher` is deployed once per chain and shared across multiple apps: `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` all reference the same `_dispatcher`/`_params.dispatcher` address and call `ICallDispatcher(dispatcher).dispatch(...)` to execute arbitrary `Call[]` batches on behalf of end users (e.g., swap-then-escrow, transfer-and-swap flows). [2](#0-1) 

The dispatcher's `dispatch()` function itself has no `onlyGateway`/`onlyHost`/ownership check whatsoever:

```solidity
function dispatch(bytes memory encoded) external {
    Call[] memory calls = abi.decode(encoded, (Call[]));
    ...
    (bool success, bytes memory result) = to.call{value: call.value}(call.data);
    if (!success) revert CallFailed(to, result);
}
``` [1](#0-0) 

Every caller — not just `IntentGatewayV2` or the `HyperFungibleToken` contracts — can call this function directly and force the dispatcher to execute a self-crafted `Call[]`. This is safe only as long as the dispatcher never holds a standing token balance or a lingering ERC20 approval outside of a single atomic call chain initiated by a legitimate app. The documentation itself flags that this invariant is fragile:

> "Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution." [3](#0-2) 

Unlike `IntentGatewayV2`, which explicitly sweeps the *entire* dispatcher balance back to itself after each `dispatch()` call (`_execute` in `IntentsBase.sol`, and the analogous sweep in `IntentGatewayV2.sol`), `HyperFungibleToken.onAccept()` and `WrappedHyperFungibleToken.onAccept()` mint/unlock tokens directly to the `beneficiary` (which the docs instruct users to set to the `CallDispatcher` address when the calldata needs to spend the bridged tokens) and then call `dispatch(message.data)` — with no sweep step afterward: [4](#0-3) [5](#0-4) 

If a user's `Call[]` batch (i) leaves any dust/leftover token balance on the dispatcher (rounding, partial swap fills, a call that approves an unlimited allowance to a router but doesn't consume it all, or simply a batch whose final call doesn't forward 100% of the minted amount out), or (ii) sets a non-exact/unlimited approval to a router as the docs explicitly warn against, that balance/approval sits on the shared `CallDispatcher` contract indefinitely. Because `dispatch()` is callable by anyone with any `Call[]`, any unrelated third party can subsequently call `CallDispatcher.dispatch()` directly (bypassing `IntentGatewayV2`/`HyperFungibleToken` entirely) with a `Call` such as `{to: token, data: transfer(attacker, balance)}` or `{to: router, data: transferFrom-based-swap-using-the-lingering-allowance}` to steal those funds — exactly mirroring Polynomial's `swapAndDeposit()` loophole, where "anyone can pass in an address and maliciously construct swapData to steal contract-approved tokens."

### Impact Explanation
Because `CallDispatcher` is a single shared contract instance used by every `HyperFungibleToken`/`WrappedHyperFungibleToken` deployment and `IntentGatewayV2` on a chain, any residual balance or approval left by *any* user's cross-chain calldata execution becomes a public target. An attacker monitoring the dispatcher's balance/approvals can permissionlessly drain those funds via a directly-submitted `dispatch()` call, resulting in theft of user funds that were meant to be swept back to the gateway or delivered to the intended recipient. This satisfies "concrete theft ... of funds" via an "unauthorized app action" reachable from a single submitted transaction.

### Likelihood Explanation
The likelihood is Medium: exploitation requires the dispatcher to actually be left holding a non-zero balance or a standing approval after a legitimate `dispatch()` call completes. `IntentGatewayV2`'s own flows are protected by an explicit full-balance sweep, but `HyperFungibleToken`/`WrappedHyperFungibleToken`'s calldata-execution path performs no such sweep, and the documentation's own warning about "unlimited allowances" acknowledges this is a realistic misuse pattern for integrators building swap-then-forward calldata. Any transaction that leaves dust or an unconsumed allowance opens an immediately and permissionlessly exploitable window, since `dispatch()` itself enforces no caller or state restriction.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to a whitelist of authorized callers (the registered `IntentGatewayV2`/`HyperFungibleToken`/`WrappedHyperFungibleToken` instances), or make the dispatcher single-use/ephemeral per call (e.g., deploy a fresh minimal-proxy dispatcher per invocation) so no other party can ever invoke it against residual state.
- Alternatively, enforce a strict "flash" invariant: require the dispatcher to end every `dispatch()` call with a zero balance for all involved tokens and zero non-zero allowances, reverting otherwise.
- Add an explicit sweep step to `HyperFungibleToken.onAccept()`/`WrappedHyperFungibleToken.onAccept()` calldata-execution paths mirroring `IntentGatewayV2`'s post-dispatch sweep.

### Proof of Concept
1. A user bridges tokens via `HyperFungibleToken.send()` with `to = CALL_DISPATCHER` and `data` encoding a `Call[]` that approves a Uniswap router for the full minted amount and swaps, but due to slippage/partial-fill the swap consumes less than the full approved/minted amount, leaving leftover tokens and/or a non-zero allowance on the `CallDispatcher`.
2. Relayer delivers the message; `onAccept()` mints to the dispatcher and calls `dispatch(message.data)`, executing the approve+swap; no sweep occurs afterward, so leftover tokens/allowance remain on the dispatcher.
3. An attacker directly calls `CallDispatcher.dispatch(abi.encode([Call({to: token, value: 0, data: abi.encodeWithSelector(IERC20.transfer.selector, attacker, leftoverBalance)})]))` — this succeeds because `dispatch()` has no caller restriction — transferring the leftover tokens to themselves. If a lingering approval exists instead, the attacker calls `dispatch()` with a `Call` to the approved router/token using `transferFrom(dispatcher, attacker, allowance)` semantics to pull the approved amount.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L320-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
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

        emit Received({from: message.from, to: beneficiary, source: string(request.source), amount: message.amount});
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-329)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

```
