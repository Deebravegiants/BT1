## Analog Found

### Title
Authentication Bypass by Assumed-Immutable Peer Mapping in `IntentGatewayV2.instance()` (TRON) - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The GitLab CVE-2024-4024 bug class is "authentication bypass by assumed-immutable data": the victim system assumes an identifier used to authorize/link identities is stable and safe to trust when unset or reused, when in fact it is attacker-influenceable. The TRON fork of `IntentGatewayV2` has the same class of flaw in its cross-chain source authentication: an unregistered peer state machine silently defaults to being treated as "this same trusted gateway" instead of being rejected.

### Finding Description
`IntentGatewayV2.instance()` in the TRON contract resolves a state machine's registered peer gateway, but falls back to `address(this)` when no peer is registered: [1](#0-0) 

This value is used directly by `authenticate()` to gate every incoming `PostRequest`: [2](#0-1) 

Compare this with the canonical/safe implementation used in the primary EVM contracts (`evm/src/apps/intentsv2/IntentsBase.sol`), which explicitly reverts with `UnknownInstance()` when no peer is registered for a state machine, rather than defaulting to any trusted value: [3](#0-2) [4](#0-3) 

The TRON variant's fallback assumes that "no explicit peer configured" is equivalent to "trust `address(this)`" — i.e., it assumes the *absence* of a governance-set mapping entry is immutable proof that the incoming request's claimed `from` (an unauthenticated, module-supplied 20-byte value inside the `PostRequest`) can be safely compared against the local contract's own address as the authorization check. This is the same root-cause pattern as the GitLab bug: relying on an identifier (there, an OAuth-linked email; here, the `_instances[keccak256(stateMachineId)]` mapping being unset) as sufficient grounds for granting trust/authorization, without accounting for the fact that the "default" state is attacker-reachable rather than a safe deny-by-default posture.

### Impact Explanation
Any state machine that Hyperbridge has a valid, registered consensus client for (so a state/event proof from that chain will pass `HandlerV2`/host verification) but that this particular `IntentGatewayV2` deployment has not yet explicitly registered as a peer via `_addDeployment`, is implicitly treated as authorized *as long as the incoming request's `from` field equals this contract's own address*. Because `IntentGatewayV2` instances are deployed via CREATE2 with an identical salt specifically so the same address recurs across chains (see deployment script), an attacker able to get a contract onto any recognized-but-unpaired chain at that same address (or otherwise able to make the origin host record `msg.sender`/`from` as that address) can have arbitrary `onAccept` calls (asset release, `NewDeployment` peer registration, `Execute`/upgrade-style requests routed through this authentication gate) accepted by the TRON gateway as if they came from a legitimate, governance-vetted peer — bypassing the peer allowlist entirely. This can lead to unauthorized asset release/mint, forged peer registration, or unauthorized privileged actions gated by `authenticate()`, i.e. concrete theft or unsound state commitment via forged message delivery.

### Likelihood Explanation
Exploitation requires the attacker to control (or otherwise force) a `msg.sender`/module identity equal to the destination gateway's own address on some Hyperbridge-recognized-but-unpaired source chain. This is a non-trivial precondition (it depends on how "from" is set by the origin host and whether an attacker can achieve a matching CREATE2 deployment or equivalent), so likelihood is not "trivial," but the underlying code defect — defaulting an unset trust mapping to a trusted value instead of denying by default — is a real and directly observable divergence from the safe pattern used everywhere else in the same codebase (`IntentsBase._instance()` reverts instead of defaulting). This divergence is itself the vulnerability worth remediating regardless of the exact deployment topology of the TRON contracts.

### Recommendation
Change `IntentGatewayV2.instance()` (TRON) to match the safe behavior in `IntentsBase._instance()`: revert with `UnknownInstance()` (or equivalent) when `_instances[keccak256(stateMachineId)] == address(0)`, instead of defaulting to `address(this)`. Audit all other divergences between the TRON contract set and the canonical `evm/src/apps/intentsv2/*` implementations for similar "default to self/trusted" fallbacks.

### Proof of Concept
1. Identify a state machine `S` for which Hyperbridge has an active, verifiable consensus client, but for which the target `IntentGatewayV2` (TRON) instance has no entry in `_instances[keccak256(S)]` (i.e., `instance(S)` returns `address(this)` by the buggy fallback).
2. On chain `S`, arrange for a `PostRequest` to be dispatched toward the TRON gateway such that the request's `from` field (the origin module identity, normally bound to `msg.sender` at the origin host) equals the TRON gateway's own 20-byte address — achievable if an attacker-controlled contract can be deployed at that exact address on `S` (e.g., via a CREATE2 factory with attacker-chosen salt/deployer), matching the deterministic address IntentGatewayV2 deployments intentionally share across chains.
3. Relay this request with a valid state proof for `S` through `HandlerV2.handlePostRequests`; `authenticate()`/`instance()` on the TRON gateway will treat `instance(S) == module` as true (both equal `address(this)`) and accept the request as coming from a legitimate registered peer, even though `S` was never actually paired.
4. The forged request is dispatched to `onAccept`, allowing unauthorized asset release, mint, or peer/administrative actions gated behind `authenticate()`.

**Note:** I could not fully verify, within the indexed portion of the repo, the exact mechanism by which the origin-chain host binds `PostRequest.from` to `msg.sender` for TRON-side or all EVM-compatible dispatch paths (only `HyperFungibleToken.sol`'s `_buildDispatchPost` was directly inspectable, which omits an explicit `from` field, implying host-side enforcement). If the origin host does *not* rigidly enforce `from == msg.sender`, the exploit becomes more directly reachable (no CREATE2 address-matching needed) and the severity increases further. A Devin session with full repository access would be needed to trace the exact TRON host dispatch implementation to confirm this precondition.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L284-300)
```text
    /**
     * @dev Fetch the IntentGateway contract instance for a chain.
     */
    function instance(bytes calldata stateMachineId) public view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        return gateway == address(0) ? address(this) : gateway;
    }

    /**
     * @dev Checks that the request originates from a known instance of the IntentGateway.
     */
    function authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        // IntentGateway only accepts incoming assets from itself or known instances
        if (instance(request.source) != module) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L395-405)
```text
    /**
     * @dev Resolves the IntentGateway instance address for a given state machine.
     * Reverts with `UnknownInstance` if no remote deployment has been registered for that chain.
     * @param stateMachineId The raw state machine identifier bytes.
     * @return The gateway address for the given state machine.
     */
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L56-67)
```text
    /**
     * @dev Authenticates an incoming cross-chain post request by verifying that the
     * sender module matches the registered gateway instance for the source chain.
     * Reverts with InvalidInput if the sender address is malformed, or Unauthorized
     * if the sender is not the expected gateway.
     * @param request The incoming post request to authenticate.
     */
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```
