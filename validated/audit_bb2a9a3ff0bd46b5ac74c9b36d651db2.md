### Title
Missing parameter validation in `IntentGatewayV2.setParams()` (Tron) enables permanent gateway bricking and fund freezing - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` initializes its configuration via `setParams()`, which performs no validation whatsoever on the supplied `Params` struct, while the equivalent EVM-mainline initialization path (`initialize()` → `_validateParams()` in `IntentsBase.sol`) enforces strict invariants on the same fields. This is the same inconsistency class flagged in the referenced C4 report: a one-time setup function lacking the checks its sibling "update" function enforces.

### Finding Description
`IntentsBase._validateParams()` enforces that `host`, `dispatcher` are non-zero contracts, `surplusShareBps <= 10_000`, `protocolFeeBps < 10_000`, and `priceOracle` is either zero or a contract: [1](#0-0) 

This validator is invoked from `_updateParams()`, the governance-driven parameter update path used post-deployment: [2](#0-1) 

The test suite confirms the initial setup path on the canonical EVM gateway (`initialize`) also rejects the same bad inputs (EOA dispatcher/host, `surplusShareBps > 10000`, `protocolFeeBps >= 10000`, EOA `priceOracle`): [3](#0-2) 

However, the Tron deployment's one-shot `setParams()` bypasses all of this — it directly assigns `_params = p` and irreversibly zeroes out the admin, with zero checks on `host`, `dispatcher`, `surplusShareBps`, `protocolFeeBps`, or `priceOracle`: [4](#0-3) 

Exactly like the original RANGE.sol/Operator.sol report — where `setSpreads()`/`setCushionFactor()` validated inputs but the `constructor()` did not — here `_updateParams()` (the ongoing "setter") validates, but `setParams()` (the one-time "constructor-equivalent") does not.

### Impact Explanation
Because `_admin` is zeroed inside `setParams()` itself, misconfiguration here is **irreversible via the admin path**; the only remaining recovery route is cross-chain governance via `updateParams` requests routed through `host()`. If `p.host` is set to an address with no code (or the wrong host), the gateway can never authenticate/receive that governance request in the first place, since inbound dispatch/`onAccept` relies on the configured host — permanently bricking the gateway with no recovery path.

Even if `host`/`dispatcher` are set correctly but `surplusShareBps > 10_000` is set, `_splitSurplus()` computes:
```
protocolShare = (dust * _params.surplusShareBps) / 10_000;   // > dust
beneficiaryShare = dust - protocolShare;                      // underflows, reverts
``` [5](#0-4) 

This causes every fill involving any dust/overpayment to revert, permanently freezing escrowed order funds for affected fills. A `protocolFeeBps >= 10_000` misconfiguration analogously corrupts fee accounting on order placement. Because the admin capability that could otherwise fix this is deliberately burned by `setParams()` itself, this is a permanent freeze-of-funds risk, not merely a transient misconfiguration — matching the Medium severity rationale given in the original C4 judgment ("directly leads to malfunctions at the protocol level").

### Likelihood Explanation
This requires only a single call to `setParams()` by whoever holds `_admin` at deployment time with an improperly-formed `Params` struct — no attacker collusion or governance compromise needed, only an operational/deployment mistake, which is exactly the scenario the original finding and Oighty's response ("only an issue if configured improperly") describe. Given `_admin` is zeroed on first (and only) call, there is no opportunity to self-correct.

### Recommendation
Add the same `_validateParams()` check (already defined in `IntentsBase.sol`) at the start of `setParams()` in `evm/tron/contracts/apps/IntentGatewayV2.sol`, mirroring the validation performed by `_updateParams()`/`initialize()`, so that malformed `host`, `dispatcher`, `surplusShareBps`, `protocolFeeBps`, or `priceOracle` values cannot be locked in before the admin capability is revoked.

### Proof of Concept
1. Deploy the Tron `IntentGatewayV2` and call `setParams()` as `_admin` with `surplusShareBps = 10_001` (or `host`/`dispatcher` set to an EOA/zero address).
2. `setParams()` succeeds unconditionally, storing the bad params and zeroing `_admin`: [6](#0-5) 
3. Users place orders and tokens are escrowed normally.
4. Any fill that produces overpayment/dust calls `_splitSurplus`, which underflows and reverts, permanently freezing the escrowed input tokens for that order (and if `host`/`dispatcher` are wrong, governance can never intervene to fix `_params` at all).

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L426-434)
```text
    function _splitSurplus(uint256 dust, bool hasOutputCall)
        internal
        view
        returns (uint256 protocolShare, uint256 beneficiaryShare)
    {
        if (hasOutputCall) return (dust, 0);
        protocolShare = (dust * _params.surplusShareBps) / 10_000;
        beneficiaryShare = dust - protocolShare;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L592-598)
```text
    function _validateParams(Params memory p) internal view {
        if (p.host == address(0) || p.host.code.length == 0) revert InvalidInput();
        if (p.dispatcher == address(0) || p.dispatcher.code.length == 0) revert InvalidInput();
        if (p.surplusShareBps > 10_000) revert InvalidInput();
        if (p.protocolFeeBps >= 10_000) revert InvalidInput();
        if (p.priceOracle != address(0) && p.priceOracle.code.length == 0) revert InvalidInput();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L611-616)
```text
    function _updateParams(ParamsUpdate memory update) internal {
        _validateParams(update.params);

        emit ParamsUpdated({previous: _params, current: update.params});
        _params = update.params;

```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3818-3861)
```text
    /// @notice setParams rejects EOA dispatcher (no code).
    function testRevert_SetParams_EOADispatcher() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(0xdead),
            solverSelection: false,
            surplusShareBps: 5000,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }

    /// @notice setParams rejects surplusShareBps > 10000.
    function testRevert_SetParams_SurplusShareBpsTooHigh() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 10001,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }

    /// @notice setParams rejects protocolFeeBps >= 10000.
    function testRevert_SetParams_ProtocolFeeBpsTooHigh() public {
        IntentGatewayV2 gw = _deployGatewayProxy();
        Params memory p = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 5000,
            protocolFeeBps: 10000,
            priceOracle: address(0)
        });
        vm.expectRevert(IntentsBase.InvalidInput.selector);
        gw.initialize(p, new bytes[](0), address(0));
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L302-311)
```text
    /**
     * @notice Sets the parameters for the IntentGateway.
     * @param p The parameters to be set, encapsulated in a Params struct.
     */
    function setParams(Params memory p) public {
        if (msg.sender != _admin) revert Unauthorized();

        _admin = address(0);
        _params = p;
    }
```
