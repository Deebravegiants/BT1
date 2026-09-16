## Analog Found

### Title
Unauthenticated `CallDispatcher.dispatch()` lets anyone exploit any privilege ever granted to the shared dispatcher address - (File: `evm/src/utils/CallDispatcher.sol`)

### Summary
`CallDispatcher` is a single, chain-wide shared contract that executes arbitrary `Call[]` batches "as itself" and has **no caller restriction whatsoever** on its `dispatch()` entrypoint. Multiple apps (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`/`ExtrinsicIntents`) route ISMP-delivered, attacker-influenced calldata through this same contract instance. This mirrors the Blast `CrossDomainMessenger`/governor issue: a widely-reachable relay contract that ends up holding an implicit privilege on a third-party contract can have that privilege hijacked by anyone who can reach the relay — and here, reaching it requires no cross-chain proof at all, just a direct call.

### Finding Description
`CallDispatcher.dispatch(bytes memory encoded)` decodes an arbitrary `Call[]` and executes each entry with `to.call{value: call.value}(call.data)`, with the only check being that `to` has code: [1](#0-0) 

There is no `onlyHost`, `onlyApp`, or any sender check on `dispatch()` — it is a bare `external function` callable by literally any EOA or contract, not gated behind ISMP delivery at all.

The intended design is that `dispatch()` is reached only indirectly, from an app's `onAccept` after a verified cross-chain delivery, e.g.: [2](#0-1) 
and [3](#0-2) 

But because `dispatch()` itself is unauthenticated, this "indirection" provides no real protection: any privilege ever granted *to the `CallDispatcher` address* — a role, an allowance, ownership — is reachable by anyone who calls `CallDispatcher.dispatch()` directly, without needing a relayer, a valid ISMP proof, or any cross-chain message at all.

The codebase itself demonstrates the exact pattern that creates this exposure — granting `MINTER_ROLE` on a fungible token to the shared `CallDispatcher` instance so that calldata delivered through `onAccept` can mint tokens as part of a composable cross-chain flow: [4](#0-3) [5](#0-4) 

`HyperFungibleTokenImpl.grantMinterRole` is a real, deployable capability, not test-only scaffolding: [6](#0-5) 

If an integrator grants `CallDispatcher` `MINTER_ROLE` (or any other standing privilege) on a production token to support "bridge-and-mint" or "transfer-and-swap" composable flows advertised in the docs, that privilege becomes globally exploitable: any address can call `CallDispatcher.dispatch()` directly with `Call({to: feeToken, value: 0, data: abi.encodeWithSelector(mint.selector, attacker, hugeAmount)})` and mint arbitrary tokens, with zero relation to any ISMP request, proof, or relayer.

### Impact Explanation
This is an unbacked-mint / unauthorized-app-action class of vulnerability. Because `CallDispatcher` is deployed once per chain and shared across every app that uses `ICallDispatcher(_dispatcher).dispatch(...)` (`HyperFungibleToken`, `WrappedHyperFungibleToken`, `IntentGatewayV2`), a single misconfiguration — granting the dispatcher any standing role/allowance on any contract — becomes a chain-wide, permanently and permissionlessly exploitable backdoor, independent of ISMP's proof/consensus security entirely. This is more severe than the original Blast report in one respect: the Blast attacker needed to forge a `relayMessage` call through the messenger; here, the attacker doesn't even need to go through the cross-chain path — `dispatch()` is directly callable.

### Likelihood Explanation
The docs explicitly promote composable, calldata-driven flows ("bridge USDC then swap to WETH", "transfer-and-stake", "transfer-and-deposit into a lending protocol") that in practice require the shared `CallDispatcher` to hold ongoing approvals or roles on downstream protocols to be useful for anything beyond one-shot atomic in-array sequences. The current production deploy script (`DeployIsmp.s.sol`) does not grant `CallDispatcher` any role, but the test suite establishes `grantMinterRole(address(callDispatcher))` as the sanctioned integration pattern for calldata-mint flows, making this a likely path for a future or third-party deployment following the documented pattern.

### Recommendation
- Restrict `CallDispatcher.dispatch()` to only be callable by registered/allow-listed app contracts (e.g., an `onlyRegisteredCaller` modifier), or
- Deploy a dedicated, non-shared `CallDispatcher` instance per app/token that needs to hold any standing privilege, so a compromise or misconfiguration on one integration cannot be leveraged against another, and
- Explicitly document that `CallDispatcher` must never be granted any standing role, allowance, or ownership on any contract — only transient, same-transaction custody is safe, and add this to the "Security" note in `docs/content/developers/evm/hyper-fungible-token/overview.mdx`.

### Proof of Concept
1. Any integrator deploys `HyperFungibleTokenImpl` (or a similar mintable token) and calls `grantMinterRole(address(callDispatcher))`, following the exact pattern shown in `evm/tests/foundry/HyperFungibleTokenTest.sol:73-74`, to support composable calldata flows advertised in the docs.
2. An attacker calls `CallDispatcher.dispatch(...)` directly (no ISMP message, no relayer, no proof needed) with:
```solidity
Call[] memory calls = new Call[](1);
calls[0] = Call({
    to: address(feeToken),
    value: 0,
    data: abi.encodeWithSelector(IHyperFungibleTokenImpl.mint.selector, attacker, type(uint256).max)
});
callDispatcher.dispatch(abi.encode(calls));
```
3. Since `msg.sender` inside the `mint` call is `address(callDispatcher)`, which holds `MINTER_ROLE`, the mint succeeds and the attacker receives unbacked tokens, entirely bypassing ISMP consensus verification.

### Citations

**File:** evm/src/utils/CallDispatcher.sol (L44-60)
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
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L303-305)
```text
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

**File:** evm/tests/foundry/HyperFungibleTokenTest.sol (L72-80)
```text
        callDispatcher = new CallDispatcher();
        // Grant minter role to CallDispatcher so calldata tests can mint via it
        feeToken.grantMinterRole(address(callDispatcher));

        hft = new TestHFT();
        hft.configure(HyperFungibleToken.ConfigOptions({
            host: address(host),
            dispatcher: address(callDispatcher)
        }));
```

**File:** evm/tests/foundry/HyperFungibleTokenTest.sol (L406-407)
```text
        wrappedCallDispatcher = new CallDispatcher();
        feeToken.grantMinterRole(address(wrappedCallDispatcher));
```

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L78-85)
```text
    /**
     * @notice Grants minter role to an address
     * @param account The address to grant the minter role to
     */
    function grantMinterRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(MINTER_ROLE, account);
    }

```
