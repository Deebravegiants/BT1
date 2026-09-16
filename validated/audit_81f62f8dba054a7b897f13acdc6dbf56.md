## Title
Unrestricted `dispatch()` on the shared `CallDispatcher` allows anyone to drain any funds it transiently or residually holds - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch()` is a fully public, unauthenticated function that executes an arbitrary array of attacker-supplied `Call{to, value, data}` entries against the contract's own balance and identity. Every app that relies on it — `IntentGatewayV2`/`IntentsBase` (predispatch/postdispatch calldata execution), `HyperFungibleToken`, and `WrappedHyperFungibleToken` — assumes the security checks live in the calling app (fund accounting, sweep-back logic), exactly as `VestingEscrow.sol` gated voting through `onlyRecipient` while the underlying `OZVotingAdaptor` implementation performed no independent authorization. Here, `CallDispatcher` is the "unsecured adaptor": it exposes the same privileged capability (spend whatever native ETH/ERC20 balance the shared contract currently holds, calling any target) with no restriction to the apps that are supposed to be its only legitimate callers.

### Finding Description
`CallDispatcher` is deployed once and shared across multiple apps [1](#0-0) . Its `dispatch()` function decodes an arbitrary `Call[]` and executes each call with the contract's own balance, with no `msg.sender` check whatsoever: [2](#0-1) 

It also has a `receive()` function that accepts arbitrary native ETH transfers from anyone [3](#0-2) .

The apps that route calldata through it (`IntentsBase._execute`, `IntentGatewayV2` predispatch handling) transfer tokens/ETH to the dispatcher, call `dispatch()`, and then sweep back only the balances of tokens they explicitly track (`order.output.assets` / `order.inputs`): [4](#0-3) 

This mirrors the report's root cause precisely: the higher-level contract (`VestingEscrow`/`IntentGatewayV2`/`HyperFungibleToken`) enforces access control on *its own* entry points, but the underlying executor it delegates security-sensitive action to (`OZVotingAdaptor`/`CallDispatcher`) performs the privileged action for **any caller**, not just the trusted wrapper. Because `CallDispatcher` is a standalone, permissionless, shared singleton (per the docs, one deployment is reused across gateway/HFT contracts on a chain) [5](#0-4) , anyone can call `dispatch()` directly at any moment they observe it holding a balance — whether that balance is protocol dust left over from output tokens not included in `order.output.assets`, ETH sent to `receive()` by mistake, or any residual amount from a partially-swept flow — and route it to an address of their choosing.

### Impact Explanation
Any native ETH or ERC20 balance sitting in the shared `CallDispatcher` at any point in time is immediately stealable by an arbitrary, unprivileged account, since `dispatch()` has no caller restriction and can direct the contract's full balance to any target via `to.call{value: call.value}(call.data)`. Because this contract is shared infrastructure used by the intent gateway and the fungible-token bridge contracts for calldata execution, this is a live theft-of-funds vector reachable from a single unprivileged transaction, matching the report's core theme of a security-critical action being reachable without the access control the system's authors intended.

### Likelihood Explanation
High reachability: `dispatch()` is `external` with no modifier, callable in a single transaction by anyone who observes (or can induce, e.g. via `receive()`) a non-zero balance on the contract. No privileged role, governance, or off-chain condition is required to trigger the drain — only that the shared dispatcher hold some balance at the time of the call.

### Recommendation
Restrict `CallDispatcher.dispatch()` to a caller allowlist (e.g., `onlyAuthorizedCaller`/`onlyGateway` modifier configured at deploy/init time for each app instance permitted to use it), or make the dispatcher stateless-only per-call (e.g., deploy an ephemeral dispatcher per invocation, or require the calling app to be `msg.sender` and to have just funded the dispatcher within the same call frame). At minimum, ensure no balance can ever persist in the shared contract across transactions, and add an authorization check mirroring the `onlyHost`/`onlyRecipient` pattern used elsewhere in the codebase.

### Proof of Concept
1. Observe `CallDispatcher` momentarily/residually holding native ETH or an ERC20 balance (e.g., dust from an `IntentsBase._execute` postdispatch call whose output token isn't included in `order.output.assets`, or ETH sent directly via `receive()`).
2. Call `CallDispatcher.dispatch(abi.encode(calls))` directly, with `calls = [Call({to: attacker, value: dispatcher.balance, data: ""})]` (or an ERC20 `transfer` call to the attacker for any ERC20 balance).
3. Since `dispatch()` performs no caller check [2](#0-1) , the call succeeds and the contract's balance is transferred to the attacker, with no interaction with `IntentGatewayV2`, `HyperFungibleToken`, or any of the apps that are supposed to be its only legitimate callers.

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

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L94-98)
```text
### Security

The `CallDispatcher` executes calls in its own context (not via `delegatecall`), so the HFT contract's storage is never at risk. If any call in the array reverts, the entire `onAccept` handler reverts — including the token mint/unlock. The request can then be retried by any relayer until the timeout expires. If no successful execution occurs before the timeout, the request times out and the sender is eligible for a refund on the source chain. Token approvals in the `Call[]` should use exact amounts rather than unlimited allowances, since the dispatcher contract holds tokens temporarily during execution.

Existing `CallDispatcher` deployments are listed on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
```
