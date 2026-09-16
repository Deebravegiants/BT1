### Title
Unauthenticated `CallDispatcher.dispatch` lets any caller drain the shared dispatcher's ETH balance and impersonate `HyperFungibleToken` cross-chain messages as arbitrary outbound calls - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher.dispatch` has no access control and no binding to the caller or to any specific cross-chain message. It ABI-decodes an attacker-supplied `Call[]` and forwards `to.call{value: call.value}(call.data)` for each entry, using the *contract's own* ETH balance for `call.value`. It is invoked from `HyperFungibleTokenUpgradeable.onAccept` with `message.data` taken directly from a bridged token-transfer body, but the function itself is `external` with no `onlyHost`/`onlySelf`/caller check [1](#0-0) .

### Finding Description
This is structurally analogous to the Struts "forced double evaluation" class: a value that one layer treats as inert data (`message.data` in the ISMP-authenticated POST body) is, in a second, un-scoped step, re-interpreted and executed as fully privileged instructions (arbitrary `to`, `value`, `calldata`), with the second stage never re-checking who authorized it or bounding it to the first stage's context.

`HyperFungibleTokenUpgradeable.onAccept` authenticates only the *source chain contract* (`request.from`/`request.source`), then unconditionally forwards the attacker-controlled `message.data` field to the shared `CallDispatcher`: [2](#0-1) 

`CallDispatcher.dispatch` performs no validation of the caller, of `to`, or of `value` beyond `extcodesize(to) != 0`; it spends the dispatcher contract's own held ETH balance on behalf of whoever last called it: [3](#0-2) 

Because `dispatch(bytes)` is `external` with no modifier, and `CallDispatcher` is a single shared singleton referenced by `HyperFungibleToken`, `WrappedHyperFungibleToken`, and `IntentGatewayV2` deployments (per `grep` matches across those contracts), any ETH balance it accumulates (from its `receive()` function, from leftover `call.value` after a partial spend, or from any other integrator sending it native tokens) is not scoped to the message/user that funded it. Two independent problems compound:
1. Anyone can call `CallDispatcher.dispatch` directly (bypassing the ISMP host entirely) with a `Call[]` that sends the dispatcher's full ETH balance to an attacker address.
2. Even via the "intended" path, an unprivileged cross-chain sender bridging tokens through `HyperFungibleTokenUpgradeable.onAccept` can embed a `Call[]` in `message.data` whose `call.value` exceeds anything related to the bridged `message.amount` — the dispatcher does not check that `call.value` is funded by or proportional to the incoming transfer.

### Impact Explanation
Any native-token balance held by the shared `CallDispatcher` contract can be stolen by an unprivileged actor, either by calling `dispatch` directly or by bridging an arbitrary token amount through `HyperFungibleTokenUpgradeable` and embedding a crafted `message.data`. This is a concrete theft-of-funds primitive (CWE-284/CWE-20 class: untrusted data treated as trusted instructions with no re-authorization) satisfying the "concrete theft of funds" bar, contingent on the dispatcher holding a nonzero balance at time of exploitation.

### Likelihood Explanation
High reachability: `dispatch` requires no proof, no consensus verification, and no special role — a single unsigned/permissionless call, or a single cheap cross-chain POST request through the bridge, triggers it. The only precondition is that `CallDispatcher` holds ETH at the time of the call, which can happen from normal cross-message value leftovers or accidental transfers via its unrestricted `receive()`.

### Recommendation
- Restrict `CallDispatcher.dispatch` to be callable only by the specific app contract that owns the value being forwarded (e.g., `onlyHost`/`onlyCaller` allow-list), or better, make `CallDispatcher` non-custodial: require the caller to supply `call.value` via `msg.value` in the same transaction rather than spending the contract's resident balance.
- In `HyperFungibleTokenUpgradeable.onAccept` (and any other caller of `ICallDispatcher.dispatch`), bound the embedded `call.value` to the actual bridged `message.amount`/`msg.value` forwarded in the same call, and forward funds explicitly rather than letting the dispatcher draw from an ambient balance.
- Add reentrancy and balance-accounting guards so a shared dispatcher never holds funds belonging to unrelated messages/users.

### Proof of Concept
1. Ensure `CallDispatcher` holds ETH (e.g., a prior `call.value` remainder, or send it ETH via its public `receive()`).
2. As any unprivileged EOA, call `CallDispatcher.dispatch(abi.encode([Call({to: attackerContract, value: address(callDispatcher).balance, data: ""})]))` directly — no ISMP proof or host interaction required — draining the balance.
3. Alternatively, bridge a minimal amount through `HyperFungibleTokenUpgradeable.send` from any chain, setting `params.data` to an ABI-encoded `Call[]` with `value` set to the dispatcher's expected balance; on delivery, `onAccept` calls `ICallDispatcher(_dispatcher).dispatch(message.data)` [4](#0-3) , executing the attacker's arbitrary call with the dispatcher's ETH.

**Uncertainty note:** I could not confirm within the available context whether `CallDispatcher` is deployed as a genuinely shared singleton across multiple `HyperFungibleToken`/`IntentGatewayV2` instances in production, or whether operational practice keeps its balance at zero between calls (which would reduce practical exploitability to the "resource-only" case explicitly excluded by the rules). I was also unable to locate any caller that funds `CallDispatcher` with `msg.value` immediately before invoking `dispatch` in the same transaction, which would mitigate this. A Devin session with full repository/deployment-script access could verify actual fund custody patterns and initialization of `_dispatcher` addresses to confirm real-world exploitability.

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
