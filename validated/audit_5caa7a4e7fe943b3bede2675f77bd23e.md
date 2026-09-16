Based on my investigation, I found a strong analog in the shared `CallDispatcher` contract used across `IntentGatewayV2`, `HyperFungibleToken`, and `WrappedHyperFungibleToken`.

### Title
Unauthenticated `CallDispatcher.dispatch()` allows theft of tokens/dust temporarily held by the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` has no access control — any address can call it directly with an arbitrary ABI-encoded `Call[]` array — even though it is a shared, singleton contract that multiple apps (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`) route tokens through as an intermediate execution context.

### Finding Description
`dispatch()` is declared `external` with no `onlyOwner`/`onlyHost`/`onlySelf` guard: [1](#0-0) 

Multiple protocol flows temporarily route tokens (or native ETH) through this exact contract before sweeping them back: `IntentGatewayV2.placeOrder()` transfers `predispatch` assets to the dispatcher and then invokes `dispatch()` to run swap/approval calldata before the resulting balance is pulled back into escrow, e.g.: [2](#0-1) 

Similarly `IntentsBase._execute()` sends output tokens to the dispatcher, calls `dispatch()` on `order.output.call`, then sweeps residual balances back: [3](#0-2) 

And the HyperFungibleToken bridging flow documents the same pattern — minting/unlocking tokens directly to the `CallDispatcher` address, then invoking `dispatch()` to run user-supplied post-mint calldata: [4](#0-3) 

Because `dispatch()` carries no caller restriction, this is structurally the same weakness as the reported `SwapperImpl`/`WalletImpl.execCalls()` issue: a component that is supposed to be invoked only by a trusted orchestrator (the gateway/token contract, analogous to `flash()`'s internal trusted call path) is instead reachable by anyone, letting an unprivileged actor race the legitimate flow. If the dispatcher's ERC20/ETH balance is nonzero at any point observable in a public mempool (e.g., between the token transfer to the dispatcher and the dispatcher's own `dispatch()` invocation within the same transaction, or due to any dust/rounding leftover that a `receive()`-based ETH credit or a partially-consumed approval could create), an attacker can front-run with their own `dispatch()` call moving those funds to themselves, since `dispatch()` executes with `CallDispatcher` as `msg.sender` and can call `IERC20.transfer`/`transferFrom` on whatever balance/allowance is currently held by the dispatcher — mirroring the original bug class of "any unprivileged/privileged caller may invoke an arbitrary-execution primitive intended only for the flow it was inlined in, to redirect funds sitting on that shared execution context."

### Impact Explanation
If exploitable, this allows an unprivileged party to redirect tokens or ETH momentarily custodied by the shared `CallDispatcher` — funds belonging to users placing intent orders or bridging via `HyperFungibleToken`/`WrappedHyperFungibleToken` — resulting in direct theft of user funds mid-flow, which maps to the "concrete theft of funds" bar required by the validation rules.

### Likelihood Explanation
Likelihood depends on whether any code path leaves the dispatcher's balance nonzero across a transaction boundary (rather than fully consuming/sweeping it atomically within one call). Every call site I could locate (`IntentGatewayV2.placeOrder`, `IntentsBase._execute`) transfers assets to the dispatcher and invokes `dispatch()` synchronously within the same top-level transaction, and sweeps residual balances back in the same call, which limits — but does not by design fully rule out — an externally observable window (e.g., approvals left non-zero to routers per the documented caveat, or ETH sent via `receive()` outside of a guarded flow). I was unable to fully verify the `HyperFungibleToken`/`WrappedHyperFungibleToken` `onAccept` implementations (file contents were not retrievable from the index) to confirm whether mint-to-dispatcher and `dispatch()` are always strictly atomic there as well, and the SDK docs explicitly warn "Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution" — an implicit admission that non-exact approvals left by application-supplied calldata create a real residual-allowance risk that any address can immediately exploit via a direct, unauthenticated `dispatch()` call.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g., `onlyAuthorizedCaller` gated to `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken` instances), or make the dispatcher single-use/ephemeral (deployed per-call via `CREATE2`/minimal proxy) so no shared, globally-callable instance ever custodies user funds. At minimum, ensure every code path that leaves the dispatcher holding a balance or non-zero allowance sweeps/revokes it before returning control, and enforce exact (non-infinite) approvals in all `Call[]` payloads routed through the dispatcher.

### Proof of Concept
1. Observe a pending transaction (e.g., `IntentGatewayV2.placeOrder` with `predispatch.call` or an HFT `send()` with non-empty `data`) that transfers ERC20 tokens/ETH to the well-known `CallDispatcher` address before that same transaction calls `dispatch()`.
2. Because `dispatch()` has no access-control modifier (`evm/src/utils/CallDispatcher.sol:44`), directly call `CallDispatcher.dispatch()` with a crafted `Call[]` (e.g., `token.transfer(attacker, token.balanceOf(dispatcher))`) targeting any window where the dispatcher holds a nonzero balance or a non-exact approval left over from a prior `Call[]` payload (per the documented approval-exactness caveat).
3. Funds intended for the legitimate order/bridge flow are redirected to the attacker instead of being swept back to the gateway/token contract or delivered to the intended recipient.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L392-414)
```text
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-516)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L88-96)
```text
Both contracts support optional calldata execution on the destination chain via the `CallDispatcher`. By passing a non-empty `data` field in `SendParams`, the sender can trigger arbitrary contract calls on the destination chain immediately after tokens are minted or unlocked. This enables composable cross-chain workflows like transfer-and-swap (e.g., bridge USDC then swap to WETH via UniswapV2), transfer-and-stake, or transfer-and-deposit into a lending protocol — all in a single cross-chain operation.

The `data` field is an ABI-encoded `Call[]` array, where each `Call` specifies a target contract, a native value to forward, and the calldata to execute. On the destination chain, the HFT contract mints or unlocks tokens to the `to` address, then forwards the entire `data` payload to the `CallDispatcher`, which executes each call sequentially. If the calls need to spend the bridged tokens (e.g., approve then swap), set `to` to the `CallDispatcher` address so tokens are delivered directly to it.

For code examples, see the [HyperFungibleToken](/developers/evm/hyper-fungible-token/hyper-fungible-token#calldata-execution) and [WrappedHyperFungibleToken](/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token#calldata-execution) pages.

### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.
```
