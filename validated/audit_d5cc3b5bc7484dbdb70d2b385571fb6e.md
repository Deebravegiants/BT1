## Title
Unset relayer gate leaves a newly deployed/expanded IntentGatewayV2 (and SimplexPaymaster) open to forged governance and delivery from any relayer - (File: evm/src/apps/intentsv2/ExtrinsicIntents.sol)

### Summary
The external report describes an operational mistake: when the EOS Poker service was scaled ("expanded"), the operator forgot to (re-)populate a critical security value (the random seed) in the new deployment, leaving newly added infrastructure in an insecure default state that stayed silently unprotected. The reachable analog in this codebase is `ExtrinsicIntents._checkRelayer`, which treats an unset `_relayer` (the default value on any freshly deployed or freshly migrated proxy) as "gate open" — i.e., every relayer is accepted until governance performs a separate, manual step to arm the gate.

### Finding Description
`_checkRelayer` is the only authorization check `IntentGatewayV2`/`ExtrinsicIntents.onAccept` and `onGetResponse` perform before decoding and executing an incoming ISMP message body: [1](#0-0) 

`initialize` deliberately does not arm this gate on a bare proxy unless the deployer explicitly passes a non-zero `relayer` argument, and a proxy carried over from a pre-gate implementation stays open (`_relayer == address(0)`) until the host-only `migrate` is executed: [2](#0-1) 

The design decision doc confirms this is treated as an acceptable operational window rather than a bug to be fixed in code: [3](#0-2) 

The same pattern is duplicated verbatim in `SimplexPaymaster`, another governance-controlled proxy reachable through ISMP: [4](#0-3) 

This is precisely the class of bug in the external report: a required "seeding" step (arming the relayer gate with a trusted address) is an out-of-band, easily forgotten operational action that must happen immediately after a new deployment/expansion (new chain, new proxy, or a legacy-proxy upgrade without correct migration calldata: "an upgrade that forgot the [migrate] calldata leaves nobody able to `initialize` the proxy" but *does* leave the gate open at version 1). Until that step is performed, any relayer that can get a message through `HandlerV2`/`EvmHost.dispatchIncoming` can drive `onAccept` with governance-level request kinds (`NewDeployment`, `Execute`, `UpgradeContract`) and have them applied unconditionally: [5](#0-4) 

`testFreshProxyIsOpenUntilGovernanceArmsIt` explicitly demonstrates that an arbitrary relayer's `NewDeployment` delivery is applied on a freshly initialized gateway before `setRelayer` is called: [6](#0-5) 

### Impact Explanation
During the window between deploying/expanding a gateway (new chain, fresh proxy, or upgraded legacy proxy) and governance's arming transaction, any party capable of relaying a valid ISMP proof through `HandlerV2` — not just the intended relayer — can submit forged governance messages that:
- Register a malicious peer/`instance` mapping via `NewDeployment`, redirecting all subsequent cross-chain intent traffic for that route to an attacker-controlled address (`testOnAcceptGovernanceRejectsUnlistedRelayer` shows this is exactly what the gate is meant to prevent once armed).
- Execute an `Execute`/`UpgradeContract` request that installs a malicious implementation via `upgradeToAndCall`, taking full control of the gateway's escrowed funds (`_orders`, `_filled` order state).
This is a concrete path to theft/permanent freezing of escrowed intent funds and forged message delivery, matching the report's "operational mistake" bug class where a required security-initialization step is easy to skip when standing up new infrastructure.

### Likelihood Explanation
Every new chain deployment or gateway upgrade that installs this implementation creates this window; it is not a hypothetical edge case but a documented, expected operational sequence ("closing it is governance's first act on a new chain"). Any delay, automation gap, or oversight in performing the arming transaction — analogous to the poker operator forgetting to seed the new server — leaves a fully exploitable open gate reachable by an unprivileged relayer.

### Recommendation
Require the relayer/admin to be set atomically as part of `initialize`/`migrate`/constructor rather than allowing a valid zero-relayer state to persist as "open," or fail closed (reject all deliveries) rather than fail open when `_relayer == address(0)`, forcing an explicit governance action before any deliveries — including the arming one — can be accepted.

### Proof of Concept
`testFreshProxyIsOpenUntilGovernanceArmsIt` in `evm/tests/foundry/IntentGatewayV2Test.sol` (lines 4519-4549) demonstrates the exploitable window end-to-end: a freshly initialized gateway with `relayer() == address(0)` accepts a `NewDeployment` delivered by an arbitrary relayer (`filler`) and applies it, before the intended relayer is ever set via `setRelayer`. [7](#0-6)

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L69-78)
```text
    /**
     * @dev Once a relayer is set, rejects deliveries from anyone else before the body is read. The
     * host records the revert as undelivered, so the authorised relayer can resubmit. While unset,
     * every delivery passes: a proxy from before the gate stays open until `migrate` arms it.
     * @param relayer The account that submitted the message to the handler.
     */
    function _checkRelayer(address relayer) internal view {
        address authorised = _relayer;
        if (authorised != address(0) && relayer != authorised) revert Unauthorized();
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L105-138)
```text
    /**
     * @dev One-time init of a bare proxy: registers the peers, each bound to `address(this)`,
     * stores the params, arms the relayer gate, and lands at `VERSION`. Refused on any proxy
     * already at a version, see `onlyFresh`.
     * @param p The initial gateway configuration parameters.
     * @param peerChains State-machine ids of the cross-chain peers to register, each bound to this
     * gateway's own address so no peer address is carried in the proxy's init data.
     * @param relayer The only relayer whose deliveries are accepted. Zero leaves the gate open.
     */
    function initialize(Params memory p, bytes[] memory peerChains, address relayer)
        public
        onlyFresh
        reinitializer(VERSION)
    {
        uint256 peersLength = peerChains.length;
        for (uint256 i = 0; i < peersLength; i++) {
            Deployment memory deployment = Deployment({chain: peerChains[i], gateway: address(this)});
            _addDeployment(deployment);
        }
        _validateParams(p);
        _params = p;
        _setRelayer(relayer);
    }

    /**
     * @dev Migration for a proxy from before this implementation: arms the gate and lands at
     * `VERSION`. Host-only, so nobody can arm it before governance does, and one-shot; delivered as
     * the migration calldata of the upgrade that installs this implementation. Reverts on a proxy
     * `initialize` already took there.
     * @param relayer The account whose deliveries are accepted from now on.
     */
    function migrate(address relayer) external onlyHost reinitializer(VERSION) {
        _setRelayer(relayer);
    }
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-05-gateway-setrelayer-is-host-only-and-the-only-writer-unset-means.md (L9-15)
```markdown
the only caller, reachable solely from `UpgradeContract` migration calldata. Carrying the relayer
in the init data was tried and rejected: the relayer is operational state that governance owns,
not part of what fixes a proxy's address. With no local or init-time arming left, the message that
arms a fresh proxy is a governance delivery, so the unarmed proxy has to accept it; an unset
relayer therefore gates nothing, and `setRelayer(address(0))` reopens the gate. The window is the
one between deployment and the `upgrade_gateway` that arms it, and closing it is governance's
first act on a new chain.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L250-290)
```text
    /// @dev `initialize` is for a bare proxy only. A proxy that an upgrade left below `VERSION` is
    ///      taken there by the host-only `migrate`; without this, anyone could `initialize` it
    ///      with their own host.
    modifier onlyFresh() {
        if (_getInitializedVersion() != 0) revert InvalidInitialization();
        _;
    }

    /// @param host_    Local Hyperbridge host, sole deliverer of governance requests
    /// @param params_  Initial pricing and treasury parameters
    /// @param tokens_  Initially supported ERC-20 tokens
    /// @param oracles_ token/USD feed for each entry in tokens_
    /// @param relayer_ The only relayer whose governance deliveries are accepted; zero leaves
    ///                 the gate open
    function initialize(
        address host_,
        Params memory params_,
        address[] memory tokens_,
        AggregatorV3Interface[] memory oracles_,
        address relayer_
    ) external onlyFresh reinitializer(VERSION) {
        if (host_ == address(0) || host_.code.length == 0) revert InvalidHost();
        if (tokens_.length != oracles_.length) revert LengthMismatch();

        _hostAddr = host_;
        _setParams(params_);

        for (uint256 i = 0; i < tokens_.length; i++) {
            _registerToken(tokens_[i], oracles_[i]);
        }
        _setRelayer(relayer_);
    }

    /// @notice Migration for a proxy from before the relayer gate: arms it and lands at `VERSION`.
    /// @dev Host-only, so reachable only as the init data of an `UpgradeContract` request, which
    ///      delegatecalls it with the host still `msg.sender`; one-shot through the reinitializer.
    /// @param relayer_ The only relayer whose governance deliveries are accepted from now on
    function migrate(address relayer_) external onlyHost reinitializer(VERSION) {
        if (relayer_ == address(0)) revert ZeroAddress();
        _setRelayer(relayer_);
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L14-22)
```markdown
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.

So a delivery from anyone but the authorised relayer never decodes the body, never runs
`_authenticate`, and leaves no receipt. The authorised relayer submitting the same message later
takes the normal path. A gateway whose `_relayer` is zero accepts every relayer: that is the state
a fresh proxy is in until governance arms it, below.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4516-4530)
```text
    /// A fresh proxy has no relayer and accepts every delivery: `initialize` does not touch the
    /// gate, and its only setter is host-only, so the governance upgrade that arms it has to get
    /// through first. Once armed, only that relayer is accepted.
    function testFreshProxyIsOpenUntilGovernanceArmsIt() public {
        IntentGatewayV2 gateway = _freshInitializedGateway();
        assertEq(gateway.relayer(), address(0), "no relayer after initialize");

        PostRequest memory deployment = _newDeploymentRequest(bytes("NEW_CHAIN"), address(0xBEEF));
        deployment.from = abi.encodePacked(address(gateway));
        deployment.to = abi.encodePacked(address(gateway));

        // Open: an arbitrary relayer's delivery is applied.
        vm.prank(address(host));
        gateway.onAccept(IncomingPostRequest({relayer: filler, request: deployment}));
        assertEq(gateway.instance(bytes("NEW_CHAIN")), address(0xBEEF), "open gate applies governance");
```
