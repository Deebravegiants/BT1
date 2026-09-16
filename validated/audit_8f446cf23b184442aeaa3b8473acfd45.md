### Title
Permissionless, unauthenticated `CallDispatcher.dispatch()` lets any attacker drain ETH/ERC20 value or exploit lingering approvals left in the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The OpenSea incident is a "malicious code injection" bug class: an attacker-controlled payload gets executed in a context that lets it seize assets it should not have access to. Hyperbridge's `CallDispatcher` is the exact on-chain analog: a single, shared, unowned contract with a public `dispatch(bytes)` function and no access control, reused across `HyperFungibleToken`, `WrappedHyperFungibleToken`, `BridgeToken`, and `IntentGatewayV2` on every chain (one deployed address per chain, referenced by all of these apps via the `CALL_DISPATCHER` config).

### Finding Description
`CallDispatcher.dispatch()` decodes a caller-supplied `Call[]` array and executes each call with the dispatcher's own identity (`msg.sender == dispatcher`), forwarding arbitrary `value` and `data` to arbitrary `to` addresses, with **no caller restriction whatsoever**: [1](#0-0) 

This contract also unconditionally accepts native ETH via a public `receive()`: [2](#0-1) 

Every app that uses it feeds it fully attacker/user-controlled calldata: `HyperFungibleToken`/`WrappedHyperFungibleToken` forward the `data` field of a cross-chain `Message` straight to it after minting/unlocking tokens, and `IntentGatewayV2`/`IntentsBase` forward `order.predispatch.call` and `order.output.call` — both attacker-supplied at order placement — to it before escrow and after fill: [3](#0-2) [4](#0-3) 

Crucially, the deployment scripts and mainnet address registry confirm this is **one singleton instance per chain**, shared across all these apps and all orders/transfers forever — not a per-order or per-app ephemeral contract: [5](#0-4) [6](#0-5) 

The project's own documentation acknowledges the resulting hazard — that the dispatcher holds tokens/approvals transiently and that unlimited approvals granted from within a `Call[]` payload are dangerous precisely because the dispatcher's state (approvals, and any stray balance) persists beyond a single call sequence and is shared across unrelated orders/transfers: [7](#0-6) 

Because `dispatch()` has no `onlyGateway`/`onlyHost`/`onlyOwner` gate, **any unprivileged address** can call it directly at any time with an arbitrary `Call[]`. Any value the dispatcher ends up holding outside of a single atomic call sequence — native ETH sent to it directly (its `receive()` accepts from anyone), ERC20 dust from tokens acquired via an executed call but not listed in `order.output.assets`/`outputsLen` (and thus never swept), or an ERC20 allowance a malicious `Call[]` grants to an attacker-chosen spender (which persists in storage indefinitely since ERC20 approvals are never implicitly revoked) — is trivially and permissionlessly claimable by whoever calls `dispatch()` first with a `Call({to: attacker, value: balance, data: ""})` or `token.transferFrom(dispatcher, attacker, amount)`.

### Impact Explanation
This breaks the "no unauthorized app action" and "theft of funds" invariants: a component that legitimately custodies value transiently (native ETH, ERC20 balances, ERC20 approvals) across multiple independent applications and users has zero access control on the function that spends that value. Any stray balance or lingering approval — whether from a bug in one app's sweep logic, a user mistake, or a maliciously crafted `Call[]` from an unrelated order — becomes a race for any attacker monitoring the chain, at the expense of the party who was supposed to receive that value back.

### Likelihood Explanation
Medium. Exploitation does not require any privileged role, consensus manipulation, or governance compromise — only a standard EOA calling `dispatch()` on a well-known, publicly listed contract address. The precondition (dispatcher holding stray value/approvals) is foreseeable and explicitly flagged as a risk by the project's own documentation, and is reachable through several independent code paths (`HyperFungibleToken`/`WrappedHyperFungibleToken` calldata execution, `IntentGatewayV2` predispatch/postdispatch calldata), all of which accept attacker-supplied `Call[]` content that could set unlimited approvals or otherwise leave value behind.

### Recommendation
Add access control to `CallDispatcher.dispatch()` so it can only be invoked by the app contract that is orchestrating the current call sequence (e.g., an `onlyCaller`/allow-listed-caller pattern, or deploy a dedicated, ephemeral dispatcher per call sequence instead of a shared singleton). Additionally, remove the unconditional payable `receive()` or restrict it, and enforce that any approvals granted within a dispatched `Call[]` are reset to zero at the end of the sequence, so no allowance or balance can outlive a single atomic execution.

### Proof of Concept
1. Any user submits a `HyperFungibleToken.send()` or an `IntentGatewayV2` order whose `data`/`call` field is `abi.encode([Call({to: TOKEN, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, ATTACKER, type(uint256).max)})])`. This executes via `ICallDispatcher(dispatcher).dispatch(...)` and grants `ATTACKER` an unlimited allowance over `TOKEN` from the shared `CallDispatcher` (`evm/src/utils/CallDispatcher.sol:44-61`).
2. At any later point, if `TOKEN` balance briefly exists in the dispatcher (e.g., dust not covered by `outputsLen`/`order.output.assets` sweep logic in `IntentsBase._execute`, `evm/src/apps/intentsv2/IntentsBase.sol:498-545`, or ETH sent directly to the dispatcher's `receive()`), `ATTACKER` calls `TOKEN.transferFrom(dispatcher, attacker, amount)` or `CallDispatcher.dispatch(abi.encode([Call({to: attacker, value: dispatcher.balance, data: ""})]))` directly — both succeed because `dispatch()` has no access control.

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L355-357)
```text
        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-502)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);
```

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L64-64)
```text
| `CallDispatcher` | [`0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd`](https://optimistic.etherscan.io/address/0xE2C7e576E26E0bE7aC97c6fE925bcDAbD87c4bEd) |
```

**File:** evm/script/DeployIntentGateway.s.sol (L71-76)
```text
        bytes memory initData = abi.encodeCall(
            IntentGatewayV2.initialize,
            (
                Params({
                    host: HOST_ADDRESS,
                    dispatcher: config.get("CALL_DISPATCHER").toAddress(),
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
