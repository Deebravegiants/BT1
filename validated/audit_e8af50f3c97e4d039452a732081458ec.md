### Title
`CallDispatcher.dispatch()` has no access control, letting anyone directly invoke it to drain tokens transiently held by the shared dispatcher - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
The Smarty CVE is a sandbox-escape bug: code meant to run in a restricted context (a template) can reach an internal object that was supposed to be gated, and use it to perform actions outside the sandbox's intended trust boundary. The Hyperbridge analog is `CallDispatcher`, the contract that is supposed to act as an isolated execution sandbox for untrusted, order-supplied calldata on behalf of `IntentGatewayV2` and the `HyperFungibleToken`/`WrappedHyperFungibleToken` apps. `CallDispatcher.dispatch()` is declared `external` with **no caller restriction whatsoever** — any account, not just the intended gateway/HFT contract, can call it directly and make the dispatcher execute arbitrary calls, including using any ERC20 approvals the dispatcher has previously granted.

### Finding Description
`CallDispatcher` is a single, shared, stateless-looking utility contract deployed once per chain and reused by every order placed through `IntentGatewayV2` (and every transfer through `HyperFungibleToken`/`WrappedHyperFungibleToken`): [1](#0-0) 

Its `dispatch` function has no `onlyGateway`/`onlyHost`/allow-list check: [2](#0-1) 

`IntentGatewayV2`/`ExtrinsicIntents` route order-supplied, attacker-controlled `Call[]` arrays through this same dispatcher for both `predispatch` and `postdispatch`/output execution: [3](#0-2) [4](#0-3) 

Documentation explicitly warns that callers should "use exact amounts rather than unlimited allowances" for approvals executed via the `Call[]` array, precisely *because* the dispatcher holds tokens temporarily and is not otherwise protected: [5](#0-4) 

This is only advisory, not enforced on-chain. Because `dispatch()` itself is unauthenticated:
- Any user can place a legitimate-looking order whose `predispatch.call` or `output.call` contains an `approve(attacker, type(uint256).max)` call executed *by the dispatcher* against a common token (e.g. USDC/DAI). Nothing in `CallDispatcher` or `IntentsBase._execute`/`IntentGatewayV2.placeOrder` prevents an arbitrary `to`/`data` pair from being an ERC20 `approve`.
- That approval is permanent state on the shared `CallDispatcher` contract, since nothing ever revokes it.
- From then on, the attacker — using no gateway or host permission at all — can call `CallDispatcher.dispatch()` directly at any later time to pull funds via `transferFrom` for that approval, against whatever balance the dispatcher happens to hold at that moment (e.g. tokens transferred into the dispatcher during another order's predispatch/postdispatch step, before the gateway's sweep call executes, or any token dust/airdrops sent to the dispatcher address).

This breaks the sandboxing guarantee documented for `CallDispatcher` ("executes calls in its own context... so the HFT contract's storage is never at risk") because the "sandbox" object itself is reachable by anyone outside the intended caller (the gateway/HFT app), exactly analogous to the Smarty template being able to reach an internal object that should have been walled off by the sandbox.

### Impact Explanation
Any token balance transiently held by `CallDispatcher` — which by design regularly holds bridged/escrowed ERC20s and native value during `placeOrder`/`fillOrder`/HFT `onAccept` calldata execution — is at risk of theft once any attacker has planted a lingering approval through one legitimate, self-funded order. Given `CallDispatcher` is shared across all `IntentGatewayV2` orders and all `HyperFungibleToken`/`WrappedHyperFungibleToken` transfers on a chain, this is a systemic, permanent-freezing/theft-of-funds vector rather than an isolated one: a single account can seed unlimited approvals for the tokens most likely to pass through the dispatcher, then permissionlessly call `dispatch()` to sweep whatever the dispatcher is holding whenever a favorable balance appears.

### Likelihood Explanation
Reachable by any unprivileged account with no more than the token balance required to place one legitimate order (to reach `_execute`/`predispatch` and get their `approve` calldata executed by the dispatcher). No relayer, governance, or host privilege is needed to call `CallDispatcher.dispatch()` afterward — it is a plain external function.

### Recommendation
Restrict `CallDispatcher.dispatch()` to only be callable by an explicitly configured set of trusted callers (the `IntentGatewayV2` instance(s) and `HyperFungibleToken`/`WrappedHyperFungibleToken` instance(s) that are meant to use it), e.g. via an owner-managed allow-list or a constructor-bound single caller per deployment. Additionally, consider deploying a fresh, single-use dispatcher (or using per-call `CREATE2`/ephemeral proxy) per order execution so that no approval state can persist across unrelated orders, and/or have the gateway explicitly revoke any approvals granted through order calldata before returning control.

### Proof of Concept
1. Attacker (or colluding "solver") places an `IntentGatewayV2` order whose `output.call` (or `predispatch.call`) is `abi.encode([Call({to: USDC, value: 0, data: abi.encodeWithSelector(IERC20.approve.selector, attackerContract, type(uint256).max)})])`.
2. `IntentsBase._execute` (or `placeOrder`'s predispatch branch) calls `ICallDispatcher(dispatcher).dispatch(order.output.call)`, and `CallDispatcher` executes the `approve` call as itself — no check prevents this since `Call.to`/`Call.data` are unrestricted. [3](#0-2) 
3. `USDC.allowance(dispatcher, attackerContract)` is now `type(uint256).max`, permanently (unless separately revoked).
4. At any later point when the shared `dispatcher` transiently holds USDC (e.g., mid-execution of a different, unrelated order's predispatch/output flow, before the sweep call runs), the attacker calls `CallDispatcher.dispatch(abi.encode([Call({to: USDC, value: 0, data: abi.encodeWithSelector(IERC20.transferFrom.selector, dispatcher, attacker, balance)})]))` directly — a plain, unauthenticated external call — draining the dispatcher's USDC balance via the standing approval.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L25-62)
```text
contract CallDispatcher is ICallDispatcher {
    /**
     * @dev error thrown when the target is not a contract.
     */
    error NotContract(address target);

    /**
     * @dev error thrown when a call fails.
     */
    error CallFailed(address target, bytes result);

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L498-503)
```text
    function _execute(Order calldata order, uint256 outputsLen) internal {
        if (order.output.call.length == 0) return;

        address dispatcher = _params.dispatcher;
        ICallDispatcher(dispatcher).dispatch(order.output.call);

```

**File:** evm/src/apps/IntentGatewayV2.sol (L235-258)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-97)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

```
