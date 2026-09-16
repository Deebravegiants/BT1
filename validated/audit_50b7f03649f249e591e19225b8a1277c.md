### Title
Shared `CallDispatcher` retains standing ERC20 approvals across unrelated orders/transfers, allowing an attacker to drain future users' tokens routed through it - ([File: evm/src/utils/CallDispatcher.sol])

### Summary
`CallDispatcher` is a single, shared, immutable-address contract used by every `IntentGatewayV2` order (predispatch/postdispatch calldata) and every `HyperFungibleToken`/`WrappedHyperFungibleToken` cross-chain transfer with attached calldata. Any user can make `CallDispatcher` execute arbitrary `Call[]`, including `IERC20.approve(spender, amount)`, on any token. Because `CallDispatcher` is one persistent contract reused by all orders/transfers, an `approve()` issued by one (malicious) order's calldata is not scoped to that order and is never revoked — it remains a standing allowance on whatever token was targeted. Any later order/transfer from a different, honest user that routes the same token through `CallDispatcher` (as a predispatch input, an output beneficiary, or dust awaiting sweep) exposes its temporarily-held balance to that stale approval, letting the original attacker `transferFrom` it away. This is structurally the same bug class as the Footium `FootiumEscrow.setApprovalForAll` report: a shared/reusable "escrow" contract exposes a caller-controlled approval primitive whose effect outlives the caller's own session and can be used to steal assets belonging to a subsequent, unrelated owner of that same contract.

### Finding Description
`CallDispatcher.dispatch` executes attacker-controlled `Call[]` with no restriction on target or calldata, and it is the same contract address for every caller: [1](#0-0) 

`IntentGatewayV2`/`ExtrinsicIntents`/`IntrinsicIntents` route predispatch assets to this single dispatcher, execute the order's calldata, then only sweep back the balances relevant to *that* order's known input/output tokens: [2](#0-1) 

`WrappedHyperFungibleToken.onAccept` similarly forwards arbitrary attacker-supplied `data` to the same shared dispatcher after minting/unlocking tokens to it: [3](#0-2) 

The project's own documentation acknowledges that calldata routed through `CallDispatcher` can include `approve()` calls and explicitly warns against unlimited allowances "since the dispatcher holds tokens temporarily during execution" — but nothing on-chain prevents or resets such an approval: [4](#0-3) 

Because `_params.dispatcher` is one fixed address shared by every order (see `dispatcher = _params.dispatcher` usage in `IntentGatewayV2`/`IntentsBase`/tron `IntentGatewayV2.sol`), an approval granted by attacker A's order calldata (e.g. `Call({to: TOKEN, data: approve(attacker, type(uint256).max)})`) is not attached to A's order lifecycle — it is a permanent allowance from `CallDispatcher` on `TOKEN`. Any subsequent, unrelated order/transfer that moves `TOKEN` through the dispatcher (predispatch assets transferred in prior to a swap, or output/refund dust awaiting sweep-back) leaves a real, spendable balance on the dispatcher that the attacker can drain via `TOKEN.transferFrom(dispatcher, attacker, amount)` before the legitimate sweep/forward step executes, exactly as the original Footium report describes a previous owner's standing `setApprovalForAll` draining a future owner's assets from a shared escrow.

### Impact Explanation
Any user who has ever placed an order or bridged tokens with calldata can plant a hidden, permanent `approve()` inside their `Call[]` for a token they don't even use themselves. Every future order/transfer by any other user that happens to route that same token through the shared `CallDispatcher` — a legitimate, encouraged usage pattern (swap-then-escrow, transfer-and-swap) — exposes its escrowed/transient balance to theft. This is a direct theft-of-funds vector against arbitrary future users of the intent gateway and HFT bridge, not limited to the attacker's own funds.

### Likelihood Explanation
The attack requires no special privilege: placing an order with `predispatch`/`output.call` or bridging an HFT transfer with `data` is available to any unprivileged caller, and the `Call[]` structure lets them target arbitrary tokens/spenders (`evm/src/utils/CallDispatcher.sol` has no allow-list). The only timing constraint is that a victim's transaction must route the targeted token through the same dispatcher after the approval is set — a realistic and likely event for widely-used tokens (e.g. USDC/DAI) given the dispatcher is shared indefinitely across the protocol's lifetime.

### Recommendation
Do not use a single long-lived, shared `CallDispatcher` for all callers' balances. Either (a) deploy an ephemeral dispatcher/sub-account per order (e.g., via `CREATE2` clone) that is destroyed or has zero residual approvals after use, or (b) have `CallDispatcher.dispatch` explicitly reset (`approve(spender, 0)`) any allowance it granted at the end of the same call, or (c) restrict `dispatch` calldata to disallow `approve`-style state-changing calls on arbitrary ERC20s, only allowing pre-approved integration targets (e.g., a fixed router allow-list). At minimum, sweep-back logic in `IntentsBase._execute`/predispatch handling should also revoke any allowances the just-executed calldata may have granted on tokens known to pass through the dispatcher.

### Proof of Concept
1. Attacker places an `IntentGatewayV2` order with `predispatch.call` (or `output.call`) containing a single `Call`: `{to: USDC, value: 0, data: approve(attackerEOA, type(uint256).max)}`. No predispatch assets need to be sent for USDC — only the approve call is executed by `CallDispatcher.dispatch` (`evm/src/utils/CallDispatcher.sol:44-61`), and the standing allowance `USDC.allowance(dispatcher, attackerEOA) = max` is now permanent.
2. A separate, honest user later places an order whose `predispatch.assets` include USDC (swap-then-escrow pattern) or whose output token is USDC with `output.call` set (fill-then-act pattern) — in both cases USDC is transferred to `_params.dispatcher` before/while `ICallDispatcher(dispatcher).dispatch(...)` runs (`evm/src/apps/intentsv2/IntentsBase.sol` predispatch/`_execute` flow, tron mirror `evm/tron/contracts/apps/IntentGatewayV2.sol:387-449`).
3. Attacker, monitoring the mempool/dispatcher balance, calls `USDC.transferFrom(dispatcher, attackerEOA, balance)` using the standing allowance from step 1, either front-running the sweep-back transfer inside the honest user's transaction or racing it in the same block, draining the victim's temporarily-held USDC before it is returned to the gateway or forwarded to its intended recipient.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L322-328)
```text
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
