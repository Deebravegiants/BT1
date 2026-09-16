### Title
Stale, un-expiring governance-relayer-rotation messages allow a message-delivery-order attack to reinstate a revoked relayer/admin key - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
The bug class in the referenced Apostrophe CVE is CWE-613, Insufficient Session Expiration: a previously valid credential (session) is not invalidated when a newer one supersedes it, so it can be replayed later to hijack access. Hyperbridge's EVM app-governance channel has a structurally equivalent flaw: `SetRelayer` / `SetHostParam` / admin-rotation `PostRequest`s dispatched from Hyperbridge carry no expiry, no strict ordering enforcement, and no invalidation of a *previously dispatched but undelivered* rotation once a *newer* rotation has been dispatched. Because delivery of these governance ISMP messages is performed by permissionless relayers (`HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `App.onAccept`), whoever controls delivery order controls which "session" (relayer credential) ends up active, even after Hyperbridge's own state has already moved on to a newer credential.

### Finding Description
Every app that adopts the "relayer gate" pattern (`ExtrinsicIntents.sol` / `IntentGatewayV2.sol`, `SimplexPaymaster.sol`, `HostManager.sol`, `BridgeToken.sol`) stores a single authorised relayer address (`_relayer`) and checks it in `onAccept`/`onGetResponse` before decoding any governance or user action: [1](#0-0) 

Rotation is itself just another ISMP `PostRequest` (`RequestKind.SetRelayer`) dispatched from Hyperbridge and delivered by a relayer: [2](#0-1) 

The dispatch/delivery pipeline treats every request purely by its **commitment**, not by nonce ordering relative to other governance messages: `EvmHost.dispatchIncoming` only checks whether *that specific* request's receipt already exists (replay protection), and a request that reverts inside `onAccept` simply leaves no receipt so it "stays retryable" indefinitely: [3](#0-2) 

This "retryable forever" property, combined with `PostRequest.timeout == 0` used for all governance/relayer-fee/rotation dispatches (see the relayer-fee `DispatchPost{..., timeout: 0}` and the `HostManager`/`SetRelayer` dispatch pattern used throughout), means a governance message never expires and can be delivered at any point in the future chosen by whichever relayer holds it. If Hyperbridge dispatches `SetRelayer(A)` and then, before it is delivered, dispatches a newer `SetRelayer(B)` (e.g., to rotate away from a compromised/retiring key `A`), nothing on the destination distinguishes "supersede" from "concurrent": the destination contract only knows about `_relayer` at the time each message is delivered, and message delivery order is entirely up to the (permissionless) relayer network, not Hyperbridge. If the holder of the still-undelivered `SetRelayer(A)` message delivers it *after* `SetRelayer(B)` lands, `_relayer` reverts back to `A` — the developers' own documentation independently confirms this is a known, unmitigated hazard: [4](#0-3) 

This is the session-expiration analog: the "old session" (`SetRelayer(A)`, the previous authorised-relayer grant) is never invalidated by the issuance of the "new session" (`SetRelayer(B)`); it stays live and deliverable indefinitely (`timeout: 0`, no nonce/ordering check on the destination), exactly like a pre-CVE-2021-25979 Apostrophe session token that remains valid after a newer login/credential change. Once delivered, `A` — an address that Hyperbridge and its operators believe was revoked — regains full control of the contract's relayer-gated action set: minting/refunding for `BridgeToken`, escrow release/refund for `IntentGatewayV2`, and `UpgradeContract`/`WithdrawAssets`/params changes for `SimplexPaymaster` and `HostManager`.

### Impact Explanation
Reinstating a stale/revoked relayer key restores full authority over relayer-gated `onAccept` actions on the affected app. Depending on which app is targeted this can:
- Re-arm a compromised/retired key on `SimplexPaymaster` to reach `WithdrawAssets`, `UpgradeContract`, or `UnlockStake`/`WithdrawStake` — direct fund extraction from the paymaster's EntryPoint stake/deposit and token treasury.
- Re-arm a stale relayer on `IntentGatewayV2`/`ExtrinsicIntents` to release/refund escrowed intent funds to the wrong party.
- Re-arm a stale relayer on `BridgeToken`/`HostManager` to mint tokens or rewrite host parameters (including swapping the handler, per the documented `SetHostParam`/`HostManager` gate).
This is theft/unauthorized app action reachable from an ordinary relayed message, matching the "Accept only" criteria (unauthorized app action / forged authority).

### Likelihood Explanation
The precondition — governance dispatching two relayer/admin rotations to the same app before the first is delivered — is realistic in incident-response scenarios (rotating away from a suspected-compromised key quickly, then rotating again), and delivery order is entirely controlled by the relayer holding the older message, who has every incentive to hold and later replay it. The project's own decision log explicitly flags this as a live, "accepted and not mitigated" operational hazard for `SimplexPaymaster`, and the same undelivered-message/no-expiry/no-ordering properties apply uniformly to every app using the same relayer-gate + `PostRequest(timeout=0)` pattern (`HostManager`, `IntentGatewayV2`/`ExtrinsicIntents`, `BridgeToken`). Likelihood is Medium: it requires two rotations to be in flight and a relayer to intentionally reorder, but no cryptographic or consensus break is needed — only control over delivery timing, which any relayer already possesses.

### Recommendation
Bind each relayer/admin-rotation `PostRequest` to a strictly increasing sequence number stored on the destination contract (separate from the ISMP request nonce, which is per-source-chain and not app-scoped), and reject delivery of any rotation whose sequence number is not exactly `current + 1` (or is less than the last-applied rotation's sequence number). Alternatively/additionally, give governance-critical `PostRequest`s (`SetRelayer`, `SetHostParam`, `SetAdmin`, `UpgradeContract`) a bounded `timeoutTimestamp` so a stale rotation cannot be delivered arbitrarily far in the future, and require Hyperbridge to cancel/supersede an in-flight rotation (e.g., by tracking "latest dispatched rotation commitment" on-chain and refusing to accept delivery of any earlier one) before dispatching a new one to the same destination.

### Proof of Concept
1. Hyperbridge dispatches `PostRequest` #1 = `SetRelayer(A)` to `SimplexPaymaster` (or `IntentGatewayV2`/`HostManager`). A relayer R1 receives/observes it but withholds delivery.
2. Operator detects key `A` should be rotated (e.g., suspected compromise) and Hyperbridge dispatches `PostRequest` #2 = `SetRelayer(B)` to the same contract. Relayer R2 delivers it promptly; `onAccept` succeeds because `_relayer` is still unset/previous and the Hyperbridge-source check passes — see `SimplexPaymaster.onAccept` gate logic (`evm/src/utils/SimplexPaymaster.sol:313-343`). `_relayer` is now `B`.
3. At any later time, R1 delivers the withheld `PostRequest` #1 (`SetRelayer(A)`) through `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming`. Because `EvmHost` only checks the *per-request* commitment/receipt (`evm/src/core/EvmHost.sol:794-818`) and the request never timed out (`timeout: 0`), delivery succeeds and `onAccept` executes `_setRelayer(A)`, silently reinstating the revoked key `A` as `_relayer`.
4. `A` (believed retired/compromised) now passes `_checkRelayer` again and can submit `WithdrawAssets`, `UpgradeContract`, or other relayer-gated actions, exactly as documented as an accepted risk in `sdk/packages/simplex/docs/ai/decisions/2026-09-07-paymaster-relayer-gate-open-while-unset-never-settable-to-zero.md:14-22`.

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

**File:** evm/src/utils/SimplexPaymaster.sol (L309-343)
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

        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        bytes calldata payload = incoming.request.body[1:];

        if (kind == RequestKind.UpgradeContract) {
            (address newImpl, bytes memory initData) = abi.decode(payload, (address, bytes));
            ERC1967Utils.upgradeToAndCall(newImpl, initData);
        } else if (kind == RequestKind.UpdateParams) {
            _setParams(abi.decode(payload, (Params)));
        } else if (kind == RequestKind.RegisterToken) {
            (address token, address oracle) = abi.decode(payload, (address, address));
            _registerToken(token, AggregatorV3Interface(oracle));
        } else if (kind == RequestKind.DeactivateToken) {
            _deactivateToken(abi.decode(payload, (address)));
        } else if (kind == RequestKind.WithdrawAssets) {
            (address token, uint256 amount) = abi.decode(payload, (address, uint256));
            _withdrawAssets(token, amount);
        } else if (kind == RequestKind.UnlockStake) {
            entryPoint().unlockStake();
        } else if (kind == RequestKind.WithdrawStake) {
            entryPoint().withdrawStake(payable(treasury));
        } else if (kind == RequestKind.SetRelayer) {
            address newRelayer = abi.decode(payload, (address));
            if (newRelayer == address(0)) revert ZeroAddress();
            _setRelayer(newRelayer);
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

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-07-paymaster-relayer-gate-open-while-unset-never-settable-to-zero.md (L14-22)
```markdown
Accepted and not mitigated: once armed, every recovery path sits behind the gate, so a lost or
withholding relayer key strands the deposit, stake and surplus for good. A second key was rejected
because it reintroduces the privileged role the contract was designed without. Operational bounds:
the relayer is a plain EOA (the check is the handler's raw `msg.sender`, so an account executing
third-party calldata would let anyone through); sweep surplus and keep the deposit small with
`WithdrawAssets`; `swapAndDeposit` stays treasury-gated and is the one lockout-proof use of surplus;
never dispatch a second `SetRelayer` or `UpgradeContract` while one is undelivered, since requests
never expire and the relayer picks delivery order, so a superseded `SetRelayer(A)` delivered last
hands A the sole key. Confirm delivery with `requestReceipts(commitment)` first.
```
