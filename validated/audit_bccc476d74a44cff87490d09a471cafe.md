## Title
Permissionless, shared `CallDispatcher.dispatch()` lets any caller plant a persistent ERC-20 approval that can later drain tokens routed through the same dispatcher by unrelated users/orders - (File: evm/src/utils/CallDispatcher.sol)

## Summary
`CallDispatcher` is deployed once per chain and its address is reused as the shared "untrusted call executor" by every bridge app on that chain — `HyperFungibleToken`/`WrappedHyperFungibleToken` (calldata-execution feature) and `IntentGatewayV2` (predispatch/postdispatch) all point at the same `CallDispatcher` instance, as configured via `Params.dispatcher` / `ConfigOptions.dispatcher` and shown in the deployed contract addresses. [1](#0-0) [2](#0-1)  `dispatch()` is completely public/permissionless and simply executes `to.call{value}(data)` for every attacker-supplied `Call` in the batch — exactly the `target.call(data)` pattern described in the external report — with no restriction on `to` or `data` beyond `to` having code. [3](#0-2)  Anyone (no order, no bridge message, no privilege) can call `dispatch()` directly with a `Call[]` that only contains `token.approve(attacker, type(uint256).max)`. Because `CallDispatcher` never revokes or tracks allowances, that approval is a persistent state change on the ERC-20 token contract that outlives the transaction, exactly like the Aave Credit Delegation left standing in the reported incident.

## Finding Description
`CallDispatcher.dispatch()` is invoked with attacker/user-controlled `Call[]` data from multiple call sites: `IntentGatewayV2`/`IntentsBase._execute` for order fills and predispatch swaps, [4](#0-3)  and `HyperFungibleToken`/`WrappedHyperFungibleToken` on `onAccept` for calldata-execution transfers, which explicitly documents that unlimited approvals set inside a `Call[]` remain on the dispatcher. [5](#0-4) 

Because `dispatch()` itself is a public external function with no `onlyGateway`/`onlyHost` gate, any address can call it directly — bypassing the gateway/HFT entirely — supplying a `Call[]` of `approve(attackerAddress, type(uint256).max)` for any ERC-20 token. This plants a permanent allowance from `CallDispatcher` to the attacker. [3](#0-2) [6](#0-5) 

Because `CallDispatcher` is the *same shared contract address* for every app and every user on the chain, any token balance that subsequently, even transiently or accidentally, ends up on that address (e.g. residual "dust" not covered by an order's declared `output.assets`/`inputs` set and therefore not swept, a misrouted direct transfer to the dispatcher, or leftover balance from a token whose fee-on-transfer/rounding behavior isn't fully accounted by the sweep loop) becomes stealable by the attacker at any later point via a plain `token.transferFrom(dispatcher, attacker, amount)` call on the ERC-20 itself — no interaction with `IntentGatewayV2` or `HyperFungibleToken` required. The sweep logic in `_execute`/`onAccept` only clears balances for tokens explicitly listed in that specific order's `assets`, not arbitrary tokens the dispatcher might hold. [7](#0-6) 

This mirrors the reported bug class precisely: a callable function forwards arbitrary `target`/`data` while the contract retains a delegated permission (here, an ERC-20 allowance instead of Aave credit delegation), and that permission can be exploited independently of the "legitimate" flow that created it.

## Impact Explanation
Any residual or misdirected ERC-20 balance on the shared `CallDispatcher` — belonging to any user of any app that uses this dispatcher on the chain — can be permanently drained by an attacker who front-loads a self-approval via a single, permissionless `dispatch()` call. Because the dispatcher is a shared, long-lived, multi-tenant contract rather than an ephemeral per-order executor, the blast radius covers every app configured to use it (`IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken`) on that chain, not just a single order.

## Likelihood Explanation
Triggering the exploit precondition — a stray approval on the dispatcher — requires zero privilege and a single unauthenticated transaction to `dispatch()`. The harder part is timing exploitation to catch a real balance on the dispatcher; the sweep logic reduces the practical window to non-order-tracked tokens/dust, which lowers exploitation frequency but does not eliminate it, matching the report's own outcome (a real exploit was found and executed, but ultimately recovered by a whitehat before the attacker could withdraw).

## Recommendation
Restrict `CallDispatcher.dispatch()` to authorized callers (the configured `IntentGatewayV2`, `HyperFungibleToken`, `WrappedHyperFungibleToken` instances) instead of leaving it fully public, and/or have `CallDispatcher` revoke (`approve(spender, 0)`) any non-zero allowance it granted for tokens named in the batch immediately after execution, so no approval survives past the call that created it.

## Proof of Concept
1. Attacker calls `CallDispatcher.dispatch(abi.encode(calls))` directly (no gateway interaction needed) where `calls = [Call({ to: TOKEN, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attacker, type(uint256).max) })]`. [8](#0-7) 
2. `CallDispatcher` now has an infinite `TOKEN` allowance to `attacker`, with no expiry and no way for anyone else to revoke it.
3. Whenever `TOKEN` balance later lands on the dispatcher address that is not covered by an order's declared/tracked asset sweep (e.g., dust, a misrouted transfer, or a fee-on-transfer/rounding remainder), attacker calls `TOKEN.transferFrom(dispatcherAddress, attacker, balance)` directly on the token contract, draining it — entirely outside of `IntentGatewayV2`/`HyperFungibleToken` logic.

### Citations

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L64-66)
```text
| `CallDispatcher` | [`0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd`](https://optimistic.etherscan.io/address/0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd) |
| `IntentGatewayV2` | [`0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716`](https://optimistic.etherscan.io/address/0xAe041F7B0CB581876832830baeB6a2Aa2a3C9716) |
| `IntentGatewayV2 (Implementation)` | [`0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7`](https://optimistic.etherscan.io/address/0x9d82B05156d0da273D66C5cCbDccef2b00EE06A7) |
```

**File:** evm/script/DeployIntentGateway.s.sol (L71-85)
```text
        bytes memory initData = abi.encodeCall(
            IntentGatewayV2.initialize,
            (
                Params({
                    host: HOST_ADDRESS,
                    dispatcher: config.get("CALL_DISPATCHER").toAddress(),
                    solverSelection: config.get("7702").toBool(),
                    surplusShareBps: 6_000, // 60%
                    protocolFeeBps: 5, // 0.05%
                    priceOracle: address(0)
                }),
                peerChains,
                relayer
            )
        );
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L504-533)
```text
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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
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
