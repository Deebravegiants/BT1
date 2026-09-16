### Title
`_checkRelayer` fails open when `_relayer` is unset, letting any relayer deliver escrow-withdrawing intent messages - ([File: evm/src/apps/intentsv2/ExtrinsicIntents.sol])

### Summary
`IntentGatewayV2`/`ExtrinsicIntents`'s relayer gate uses `address(0)` as its "not configured" sentinel, and treats that sentinel as "accept everyone" rather than "accept no one." This mirrors the CVE-2018-12615 bug class: a security-relevant value (Passenger's gidset vs. here the authorised-relayer address) has an unsafe/all-permissive default, so any window where the value has not been explicitly initialized silently grants broad, unintended access — here, to whichever account happens to relay the Hyperbridge message first.

### Finding Description
`_checkRelayer` only rejects a delivery when `_relayer` is non-zero and the caller-reported relayer differs from it: [1](#0-0) 

`onAccept` calls `_checkRelayer(incoming.relayer)` immediately after `onlyHost`, before any further authentication, and then dispatches to fund-moving logic (`RedeemEscrow`/`RefundEscrow` via `_withdraw`, plus `NewDeployment`/`UpdateParams`/`SweepDust`/`Execute` governance actions): [2](#0-1) 

`_relayer` is only written by `_setRelayer`, called from `initialize`, `migrate`, and `setRelayer`: [3](#0-2) 

Critically, `initialize` accepts an explicit `relayer` parameter and there is nothing preventing it from being deployed with `address(0)`, which "leaves the gate open" by design/comment: [4](#0-3) 

The same fail-open default exists in the parallel `EvmHost`/`HandlerV2` message path, since `HandlerV2.handlePostRequests`/`handleGetResponses` pass whatever `_msgSender()` called the handler as `relayer`, with no restriction on who calls the handler (it is documented as permissionless): [5](#0-4) 

The project's own documentation explicitly confirms this is an intended-but-dangerous default state ("a fresh proxy is in until governance arms it") rather than a bug that was already fixed: [6](#0-5) [7](#0-6) 

The same pattern (fail-open sentinel, armed later by governance) is repeated verbatim in `SimplexPaymaster` and `HostManager`, indicating it's a systemic design choice across the privileged-relayer gates in this codebase: [8](#0-7) 

### Impact Explanation
While `_authenticate` still checks that the request's `from` module matches the registered peer gateway, and Hyperbridge-only actions still check `request.source`, the `relayer` field is not otherwise authenticated by cryptographic proof — it is simply "whoever called `HandlerV2` last." For any gateway/paymaster/host-manager instance whose relayer has not yet been explicitly armed (freshly deployed, or migrated-but-not-yet-armed, or explicitly reopened via `setRelayer(address(0))`), any address that can call `HandlerV2.handlePostRequests`/`handleGetResponses` (which is permissionless by design) can present itself as the "relayer" and have `onAccept`/`onGetResponse` treat the delivery as coming from a trusted relayer, allowing it to trigger `RedeemEscrow`/`RefundEscrow` withdrawals (and governance actions gated only by the source check) ahead of the intended relayer. This does not by itself forge state or bypass consensus/state-proof verification (the underlying request must still be legitimately dispatched and proven), so it is not full unbacked mint or arbitrary theft — but it does let an unauthorized third party race the intended relayer to claim relayer-associated privileges/fee capture, and, for any deployment/period where the gate is unarmed, defeats the entire purpose of having a relayer allowlist (privilege escalation to "trusted relayer" for anyone).

### Likelihood Explanation
Likelihood is dependent on deployment/operational state rather than a pure code path always reachable in production: mainnet deployments are expected to arm the gate via `initialize`/`migrate` with a non-zero relayer per the changelog notes, so the exposure window is any not-yet-armed proxy, any deployment intentionally left open, or any period after `setRelayer(address(0))`/`migrate` misconfiguration. Given that the codebase's own docs and tests (`testFreshProxyIsOpenUntilGovernanceArmsIt`, `testMigrateRejectsEveryoneButHost`) explicitly acknowledge and test for this open-gate state, it is a known, reachable condition, not a theoretical one, but it requires operational timing (pre-arming) to be exploitable, keeping it below the always-reachable severity of the original Passenger CVE.

### Recommendation
Treat "relayer unset" as "no relayer authorized" (deny-by-default) rather than "any relayer authorized," or require `initialize`/`migrate`/`setRelayer` to reject `address(0)` (as `SimplexPaymaster.migrate` already does), eliminating any window where an unauthenticated caller can pose as the trusted relayer. If an intentional "permissionless bootstrap" period is required, gate the withdrawal-triggering paths separately from the open-relaying period, or restrict `HandlerV2` message submission during that window.

### Proof of Concept
1. Deploy `IntentGatewayV2` proxy and call `initialize(params, peerChains, address(0))` (or leave a migrated proxy unarmed). [9](#0-8) 
2. A legitimate `RedeemEscrow`/`RefundEscrow` `PostRequest` from the correct peer gateway is proven and delivered to `HandlerV2.handlePostRequests` by an arbitrary, non-designated address (handler calls are permissionless). [5](#0-4) 
3. `EvmHost.dispatchIncoming` calls `onAccept(IncomingPostRequest(request, msg.sender))` with `msg.sender` being that arbitrary caller.
4. `_checkRelayer` passes because `_relayer == address(0)`, so the arbitrary caller's delivery is processed identically to the intended relayer's, and `_withdraw` executes. [10](#0-9)

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L86-104)
```text
    function setRelayer(address relayer) external onlyHost {
        _setRelayer(relayer);
    }

    /**
     * @dev Points the proxy at `newImplementation` and delegatecalls `data` on it in the same
     * transaction, e.g. `migrate(relayer)`. Host-only, so reachable only through `Execute`.
     * @param newImplementation The implementation to install; must have code.
     * @param data Migration calldata run against the new implementation, or empty.
     */
    function upgradeToAndCall(address newImplementation, bytes calldata data) external onlyHost {
        ERC1967Utils.upgradeToAndCall(newImplementation, data);
    }

    /// @dev The only writer of `_relayer`, behind `initialize`, `migrate` and `setRelayer`.
    function _setRelayer(address relayer) internal {
        emit RelayerUpdated({previous: _relayer, current: relayer});
        _relayer = relayer;
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-350)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L105-127)
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
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L19-22)
```markdown
So a delivery from anyone but the authorised relayer never decodes the body, never runs
`_authenticate`, and leaves no receipt. The authorised relayer submitting the same message later
takes the normal path. A gateway whose `_relayer` is zero accepts every relayer: that is the state
a fresh proxy is in until governance arms it, below.
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-05-hostmanager-admin-is-the-governance-relayer-gateway-setrelayer.md (L13-18)
```markdown
On the gateway, `setRelayer` moved from `IntentGatewayV2` to `ExtrinsicIntents` and is `onlyHost`,
so `_owner` can no longer rotate the relayer; the host reaches it only as `UpgradeContract`
migration calldata, and nothing else writes the relayer. `initialize` is unchanged, so a fresh
proxy starts with no relayer, and an unset relayer now gates nothing: the governance upgrade that
arms it has to be delivered first. `setRelayer(address(0))` reopens the gate rather than closing
it. `DeployIntentGateway.s.sol` no longer reads `GATEWAY_RELAYER` or calls `setRelayer`.
```

**File:** evm/src/utils/SimplexPaymaster.sol (L258-290)
```text
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
