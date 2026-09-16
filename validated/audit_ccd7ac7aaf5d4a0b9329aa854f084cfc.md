Analysis found a concrete gap: `BandwidthManager.onAccept` (`evm/src/apps/BandwidthManager.sol`) is the only privileged governance-delivery entry point in the codebase that lacks the relayer-allowlist check that every other equivalent contract enforces.

### Title
Missing relayer permission check on `BandwidthManager.onAccept` allows any relayer to drain treasury funds and manipulate pricing - (File: evm/src/apps/BandwidthManager.sol)

### Summary
`BandwidthManager.onAccept` authorizes a privileged governance action (`Withdraw`, which transfers arbitrary ERC20/native tokens to an arbitrary beneficiary, and `SetTiers`, which sets purchase pricing) using only two checks: `onlyHost` and `request.source == hyperbridge`. It never validates `incoming.relayer`, unlike every structurally identical contract in this repository.

### Finding Description
Every other app-level `onAccept` handler in the codebase enforces a second, independent gate on top of the host/source check: the submitting relayer (`incoming.relayer`, populated by the handler from `msg.sender`) must match a stored, governance-rotatable `_relayer` address before the request body is even decoded.
- `HostManager.onAccept` uses `restrict(incoming.relayer, _params.admin)` [1](#0-0) 
- `ExtrinsicIntents.onAccept`/`onGetResponse` call `_checkRelayer(incoming.relayer)` before reading the body [2](#0-1) 
- `BridgeToken.onAccept`/`onPostRequestTimeout` are "Gated on the relayer before the base token mints" [3](#0-2) 
- `SimplexPaymaster.onAccept` checks the relayer "right after `onlyHost` and before the Hyperbridge source check" [4](#0-3) 

This pattern was deliberately introduced across the codebase specifically to close this exact bug class — documented in dedicated changelogs: "Relayer allowlist on the intent gateway" [5](#0-4)  and "Governance deliveries to `HostManager` gated on the same relayer," which explicitly states the fix closed a route where "`HostManager.onAccept` accepted `SetHostParam` from any relayer" [6](#0-5) .

`BandwidthManager` has no `_relayer` storage, no `setRelayer` function, and no relayer check anywhere: `onAccept` only verifies `onlyHost` and `request.source.equals(hyperbridge())` before dispatching to `SetTiers` or `Withdraw`: [7](#0-6) . This is architecturally identical to the vulnerability class the other four contracts were hardened against — a privileged method (here, a fund withdrawal / price-setting action) is missing a caller-permission check that its sibling implementations all enforce, mirroring CVE-2017-11422's core defect ("does not correctly check a session's permissions when the methods … are called").

### Impact Explanation
The `Withdraw` action moves arbitrary ERC20 or native token balances held by `BandwidthManager` to an arbitrary `beneficiary` [8](#0-7) . Per the codebase's own documented threat model, the relayer gate exists precisely so that "a forged consensus proof alone cannot reach this contract" — i.e., it is defense-in-depth against a compromised/buggy consensus client or handler swap producing a `source`-matching but illegitimate delivery. Because `BandwidthManager` omits this gate entirely, any relayer able to get a `PostRequest` (nominally from `pallet-bandwidth`) delivered through the handler — including via a forged or exploited consensus path — can drain the contract's fee-token and native balances and rewrite `tierPrice`, with no secondary permission check to stop it, unlike the equivalent HostManager/gateway/token/paymaster paths.

### Likelihood Explanation
Likelihood is tied to the same consensus/handler trust assumptions the other four contracts were patched against; the difference is that here there is zero secondary defense. Any relayer capable of delivering a `SetHostParam`-style forged message to the other apps (which the repo's own tests, e.g. `testForgedHandlerSwapIsRefused`, show is exactly the attack the relayer gate stops [9](#0-8) ) would succeed unconditionally against `BandwidthManager`.

### Recommendation
Add the same relayer-allowlist pattern used elsewhere in the codebase to `BandwidthManager`: introduce a `_relayer` storage slot, a governance-only `setRelayer`/rotation path (e.g., through a new `OnAcceptActions.SetRelayer`), and call `_checkRelayer(incoming.relayer)` in `onAccept` before decoding `SetTiers` or `Withdraw`, mirroring `SimplexPaymaster._checkRelayer` and `ExtrinsicIntents._checkRelayer`.

### Proof of Concept
1. An attacker (or a relayer exploiting a consensus-client bug/handler misconfiguration elsewhere in the stack) crafts a `PostRequest` with `source == hyperbridge()` and body `[OnAcceptActions.Withdraw] ++ abi.encode(Withdrawal{token: feeToken, beneficiary: attacker, amount: contractBalance})`.
2. This request is delivered through `EvmHost.dispatchIncoming` to `BandwidthManager.onAccept` with `incoming.relayer` set to the attacker's own address (the handler forwards `msg.sender` verbatim, per the documented delivery flow [10](#0-9) ).
3. `onAccept` checks only `onlyHost` and `request.source == hyperbridge()`, both satisfiable, then executes `Withdraw` unconditionally [11](#0-10) , transferring the full token/native balance to `attacker` — with no check that `incoming.relayer` is an authorized party, unlike every analogous contract in the repo.

### Citations

**File:** evm/src/core/HostManager.sol (L134-139)
```text
    function onAccept(IncomingPostRequest calldata incoming)
        external
        override
        restrict(msg.sender, _params.host)
        restrict(incoming.relayer, _params.admin)
    {
```

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

**File:** evm/src/apps/BridgeToken.sol (L88-98)
```text
    /// @dev Gated on the relayer before the base token mints. See `_checkRelayer`.
    function onAccept(IncomingPostRequest calldata incoming) public override onlyHost {
        _checkRelayer(incoming.relayer);
        super.onAccept(incoming);
    }

    /// @dev Gated on the relayer before the base token refunds. See `_checkRelayer`.
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public override onlyHost {
        _checkRelayer(incoming.relayer);
        super.onPostRequestTimeout(incoming);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L309-317)
```text
    /// @dev Handles governance requests delivered by the local host. The first
    ///      byte of the request body encodes the `RequestKind`; only requests
    ///      originating from Hyperbridge itself, submitted by the authorised
    ///      relayer, are accepted.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-10)
```markdown
# 2026-09-03 — Relayer allowlist on the intent gateway

The gateway now accepts `onAccept` and `onGetResponse` deliveries only from a single authorised
relayer stored at `_relayer` (slot 13, packed behind `_paused`). The check runs before the message
body is decoded, so escrow redemptions, refunds and every governance action, upgrades included, are
covered. A refused delivery reverts, which the host records as undelivered, so the authorised
relayer can submit the same message later. `setRelayer(address)` is callable by the immutable
`_owner` and by the host; the host branch exists so a governance `UpgradeContract` can carry the
call as its migration calldata and arm the relayer in the upgrade transaction (`upgradeToAndCall`
delegatecalls that calldata with the host still as `msg.sender`).
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-governance-deliveries-to-hostmanager-gated-on-the-same-relayer.md (L1-7)
```markdown
# 2026-09-03 — Governance deliveries to `HostManager` gated on the same relayer

Closes the route around the app-level gates: `HostManager.onAccept` accepted `SetHostParam` from
any relayer, and that request can replace the host's handler, the contract every app trusts to
report the relayer address. `HostManager` now holds `_relayer`, set by the host admin through
`setRelayer`, and `onAccept` reverts with `UnauthorizedRelayer` for any other relayer, zero
included. Only governance traffic reaches this contract, so ordinary relaying is unaffected.
```

**File:** evm/src/apps/BandwidthManager.sol (L203-232)
```text
    /// @notice Inbound governance from `pallet-bandwidth`. The first
    /// body byte selects `OnAcceptActions`; the remainder is the
    /// action's ABI-encoded payload.
    /// @dev Only the configured host may invoke (`onlyHost`); the
    /// request's `source` must additionally equal hyperbridge.
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        PostRequest calldata request = incoming.request;

        if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();

        OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
        if (action == OnAcceptActions.SetTiers) {
            Tier[] memory updates = abi.decode(request.body[1:], (Tier[]));
            for (uint256 i = 0; i < updates.length; i++) {
                tierPrice[updates[i].tier] = updates[i].price;
                emit TierSet(updates[i].tier, updates[i].price);
            }
        } else if (action == OnAcceptActions.Withdraw) {
            Withdrawal memory w = abi.decode(request.body[1:], (Withdrawal));
            if (w.token != address(0)) {
                IERC20(w.token).safeTransfer(w.beneficiary, w.amount);
            } else {
                (bool sent,) = w.beneficiary.call{value: w.amount}("");
                if (!sent) revert InsufficientNativeToken();
            }
            emit Withdrawn(w.token, w.beneficiary, w.amount);
        } else {
            revert UnauthorizedAction();
        }
    }
```

**File:** evm/tests/foundry/HostManagerTest.sol (L221-240)
```text
    /// The attack the gate exists for: a forged SetHostParam that swaps the host's handler for a
    /// contract that will report any relayer address. With the gate, an arbitrary relayer cannot
    /// deliver the swap, so the handler stays honest and the attacker's contract never becomes
    /// able to call the host.
    function testForgedHandlerSwapIsRefused() public {
        MaliciousHandler malicious = new MaliciousHandler();
        HostParams memory params = host.hostParams();
        address honestHandler = params.handler;
        params.handler = address(malicious);
        PostRequest memory swap = _setHostParamRequest(params);

        // Delivered by the attacker (through the honest handler, proof assumed forged).
        vm.prank(address(handler));
        host.dispatchIncoming(swap, OUTSIDER);
        assertEq(host.hostParams().handler, honestHandler, "handler unchanged");

        // The attacker's contract is not the handler, so it cannot inject a relayer address.
        PostRequest memory forged = _setHostParamRequest(host.hostParams());
        vm.expectRevert(EvmHost.UnauthorizedAction.selector);
        malicious.deliver(EvmHost(payable(address(host))), forged, address(this));
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-13)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
```
