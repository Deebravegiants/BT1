## Analysis

The reported bug class (missing/insufficiently-scoped authorization check that lets an under-privileged caller trigger a privileged action) maps directly onto `BandwidthManager.onAccept` in this codebase.

Across the repo, every other `IApp.onAccept` implementation that handles privileged/governance actions was hardened with a single-relayer allowlist gate, checked *before* the message body is decoded:

- `HostManager.onAccept` — `restrict(incoming.relayer, _params.admin)` [1](#0-0) 
- `BridgeToken.onAccept`/`onPostRequestTimeout` — `_checkRelayer(incoming.relayer)` [2](#0-1) 
- `ExtrinsicIntents.onAccept`/`onGetResponse` — `_checkRelayer(incoming.relayer)` [3](#0-2) 
- `SimplexPaymaster.onAccept` — `_checkRelayer(incoming.relayer)` [4](#0-3) 

The rationale for this pattern is spelled out explicitly in the repo's own docs: it defends governance/withdrawal-style callbacks against a scenario where the trusted `handler` is swapped or compromised (e.g. via `HostManager`'s `SetHostParam`), since a malicious handler can fabricate an `IncomingPostRequest` (including `request.source`) and call `onAccept` directly, bypassing real state-proof verification. That is exactly why `HostManager`, `BridgeToken`, `IntentGatewayV2`/`ExtrinsicIntents`, and `SimplexPaymaster` were all retrofitted with a relayer allowlist gate — see the dedicated changelog entries. [5](#0-4) [6](#0-5) 

`BandwidthManager.onAccept` was left out of this hardening. It only checks `onlyHost` and `request.source == hyperbridge`, with no relayer allowlist at all, and its `Withdraw` action transfers an arbitrary `amount` of an arbitrary `token` (or native currency) to an arbitrary `beneficiary` supplied in the message body: [7](#0-6) 

### Title
Missing relayer authorization gate on `BandwidthManager.onAccept` allows treasury drain / price manipulation if the handler is ever compromised - (File: `evm/src/apps/BandwidthManager.sol`)

### Summary
Every other privileged `onAccept` callback in this codebase (`HostManager`, `BridgeToken`, `ExtrinsicIntents`/`IntentGatewayV2`, `SimplexPaymaster`) was hardened with a single-relayer allowlist check that runs before the message body is decoded, specifically to defend the `Withdraw`/governance path against a compromised or maliciously-swapped `handler` contract. `BandwidthManager.onAccept` was never given this gate, so its `Withdraw` (arbitrary ERC20/native transfer) and `SetTiers` (pricing) actions remain reachable by anyone who can get the host to call `onAccept` with a forged `request`, e.g. through the exact handler-swap primitive the rest of the codebase explicitly defends against.

### Finding Description
`BandwidthManager.onAccept` is restricted with `onlyHost` and checks only `request.source.equals(hyperbridge)`: [7](#0-6) 

Unlike `HostManager.onAccept`, which additionally requires `restrict(incoming.relayer, _params.admin)` [1](#0-0) , `BandwidthManager` never inspects `incoming.relayer`. The `relayer` field is not part of any verified state proof — it is simply the `msg.sender` the `handler` reports to the host on `dispatchIncoming`, i.e., attacker-controlled data if the `handler` itself is ever malicious or swapped, and `request.source` is likewise a value the `handler` supplies rather than something re-verified by the app. This is precisely the class of attack `testForgedHandlerSwapIsRefused` exercises against `HostManager` [8](#0-7) , and the reason the same allowlist gate was rolled out to every other privileged app [9](#0-8) . `BandwidthManager` was missed from this rollout, leaving its `Withdraw` action — which moves the contract's entire fee-token/native balance to an attacker-chosen `beneficiary` — and `SetTiers` — which controls purchase pricing — without the second line of defense every comparable governance callback in the repo now has.

### Impact Explanation
`Withdraw` sweeps `w.amount` of `w.token` (or native currency) to `w.beneficiary` with no relayer/allowlist check: [10](#0-9) . `BandwidthManager` accumulates the fee-token proceeds of every `purchase()` call in its own balance [11](#0-10) , so a successful forged `Withdraw` delivery drains that entire treasury balance. `SetTiers` can similarly be manipulated to zero out or arbitrarily set pricing. This is concrete theft of funds, consistent with High severity.

### Likelihood Explanation
Exploitation requires the same precondition the repo's own hardening effort targets: the ability to get the host to invoke `onAccept` with an attacker-chosen `request`/`relayer`, i.e., a compromised or swapped `handler`. That precondition is not `BandwidthManager`-specific — it is the same trust boundary `HostManager`, `BridgeToken`, `IntentGatewayV2`, and `SimplexPaymaster` were all patched against. Because `BandwidthManager` alone lacks the mitigating gate, it is the single remaining app in the deployment where that trust-boundary failure directly yields fund theft, making it the most likely target if that boundary is ever crossed.

### Recommendation
Add a `_relayer` allowlist to `BandwidthManager`, mirroring `HostManager`/`SimplexPaymaster`: store an authorised relayer/admin address, gate `onAccept` with a `_checkRelayer(incoming.relayer)` (or `restrict`) check before decoding `request.body`, and provide a privileged `setRelayer`/rotation function, consistent with the pattern already applied everywhere else in the codebase.

### Proof of Concept
1. Attacker obtains the ability to have the host invoke `BandwidthManager.onAccept` with a forged `IncomingPostRequest` where `request.source` is set to `hyperbridge()` and `incoming.relayer` is arbitrary (the exact primitive demonstrated for `HostManager` in `testForgedHandlerSwapIsRefused`, e.g. via a compromised/malicious `handler`).
2. Craft `request.body = abi.encodePacked(uint8(OnAcceptActions.Withdraw), abi.encode(Withdrawal({token: feeToken, beneficiary: attacker, amount: type(uint256).max /* or contract balance */})))`.
3. Call `onAccept` — since only `onlyHost` and the source-string check apply, and `incoming.relayer` is never validated, the withdrawal executes and transfers the contract's entire fee-token balance to `attacker`. Compare to `HostManagerTest.testForgedHandlerSwapIsRefused`, which shows the equivalent attack is blocked in `HostManager` precisely because of the relayer gate `BandwidthManager` lacks. [12](#0-11)

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L331-336)
```text
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L313-317)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) {
            revert UnauthorizedCall();
        }
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-governance-deliveries-to-hostmanager-gated-on-the-same-relayer.md (L1-9)
```markdown
# 2026-09-03 — Governance deliveries to `HostManager` gated on the same relayer

Closes the route around the app-level gates: `HostManager.onAccept` accepted `SetHostParam` from
any relayer, and that request can replace the host's handler, the contract every app trusts to
report the relayer address. `HostManager` now holds `_relayer`, set by the host admin through
`setRelayer`, and `onAccept` reverts with `UnauthorizedRelayer` for any other relayer, zero
included. Only governance traffic reaches this contract, so ordinary relaying is unaffected.
No file in this package changed; the entry is here because the delivery flow documented in
`Flow.md` is what it corrects.
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

**File:** evm/src/apps/BandwidthManager.sol (L153-171)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);

```

**File:** evm/src/apps/BandwidthManager.sol (L208-232)
```text
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

**File:** evm/tests/foundry/HostManagerTest.sol (L221-241)
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
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L24-31)
```markdown
The address checked in step 3 is only as trustworthy as the contract in step 1, and that contract
is `_hostParams.handler`, which `HostManager.onAccept` can replace through a `SetHostParam`
request from Hyperbridge (`evm/src/core/HostManager.sol`, then `EvmHost.updateHostParams`). The
HostManager therefore runs the same relayer check before decoding any governance action, against
its admin: the account named in its constructor, which is also the only one allowed to bind the
host with `init` when the host was not known at construction. `testForgedHandlerSwapIsRefused` in
`evm/tests/foundry/HostManagerTest.sol` plays the swap through the real host and shows it refused.
The HostManager sees no user traffic, so this leaves ordinary relaying open.
```
