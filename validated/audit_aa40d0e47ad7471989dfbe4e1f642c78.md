I found the tron IntentGatewayV2's `authenticate` function has a distinct behavior from the main EVM version — it falls back to `address(this)` when no instance is registered, unlike `IntentsBase._instance()`/`ExtrinsicIntents._authenticate()` which revert with `UnknownInstance`. Let me verify this discrepancy and check how it's used.## Title
IntentGatewayV2 (Tron) `authenticate()` falls back to self-address for unregistered chains, allowing cross-chain impersonation of the gateway — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The CVE describes libcurl wrongly reusing a connection that was authenticated for one credential set as if it were authenticated for a different, unrelated request — the pooling/lookup logic silently substitutes one identity for another. The Tron `IntentGatewayV2.instance()` function exhibits the same bug class: when no peer gateway is registered for a source chain, it silently substitutes the contract's *own* address as the "trusted" credential instead of rejecting the lookup, and `authenticate()` then treats any message whose forged `from` field equals that fallback value as coming from a legitimate, registered instance.

### Finding Description
`instance()` in the Tron variant of `IntentGatewayV2` returns `address(this)` whenever `_instances[keccak256(stateMachineId)]` is unset, rather than reverting: [1](#0-0) 

```
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}

function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    // IntentGateway only accepts incoming assets from itself or known instances
    if (instance(request.source) != module) revert Unauthorized();
}
```

This directly contrasts with the canonical EVM implementation used elsewhere in the codebase (`IntentsBase._instance()` / `ExtrinsicIntents._authenticate()`), which reverts with `UnknownInstance` when no deployment is registered: [2](#0-1) [3](#0-2) 

`authenticate()` is the sole gate protecting `RedeemEscrow`/`RefundEscrow` withdrawal handling in `onAccept()` (mirrored by the reference implementation's dispatch logic): [4](#0-3) 

Because `instance(request.source)` collapses to `address(this)` for *any* `request.source` that has no registered `_instances` entry, an attacker who can get an ISMP POST request relayed from such an unregistered (but otherwise Hyperbridge-connected/trusted-consensus) state machine can freely set `request.from` to `abi.encodePacked(address(this))` (the Tron gateway's own address) and pass `authenticate()` — with no actual peer IntentGateway deployment involved at all. The check effectively "reuses" the contract's own identity as a stand-in credential for an unauthenticated/absent peer, exactly the pattern in the CVE where one credential context is wrongly substituted for another.

### Impact Explanation
A successful forged `PostRequest` with `RequestKind.RedeemEscrow` or `RefundEscrow` and an attacker-chosen `WithdrawalRequest` body (arbitrary beneficiary/amount) reaches `_withdraw(...)`, releasing escrowed order funds held by the gateway to an attacker-controlled address. This is a direct theft of escrowed intent funds — the core custody guarantee of the IntentGateway — reachable purely by dispatching a message from any not-yet-registered source chain, which requires no privileged role, only the ability to relay/deliver a message from that chain (the same capability an ordinary relayer or token bridger already has).

### Likelihood Explanation
Exploitability depends on the existence of at least one Hyperbridge-connected state machine for which `_instances[keccak256(stateMachineId)]` has not yet been set on the Tron gateway (e.g., a newly onboarded chain before governance calls `NewDeployment`, or any chain intentionally left unregistered for this app). Given Hyperbridge's multi-chain, continuously-expanding chain set and governance-driven, asynchronous registration process, such a window is realistic and does not require compromising any existing gateway or consensus client — only using a chain whose gateway entry is still `address(0)`.

### Recommendation
Change `instance()` (and any callers of it, including `authenticate()`) in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g., `UnknownInstance`) when no deployment is registered for the given `stateMachineId`, matching the behavior of `IntentsBase._instance()` used by the canonical EVM implementation, instead of defaulting to `address(this)`.

### Proof of Concept
1. Identify (or wait for) a state machine `S` connected to Hyperbridge for which the Tron `IntentGatewayV2._instances[keccak256(S)]` is still `address(0)` (not yet registered via `NewDeployment`).
2. From chain `S`, dispatch an ISMP POST request destined for the Tron `IntentGatewayV2` with:
   - `source = S`
   - `from = abi.encodePacked(address(tronIntentGatewayV2))` (the victim gateway's own address)
   - `body = abi.encodePacked(uint8(RequestKind.RedeemEscrow), abi.encode(WithdrawalRequest{ beneficiary: attacker, token/amount: escrowed order data }))`
3. Once relayed and delivered, `onAccept()` calls `authenticate(request)`, which calls `instance(S)`; since `S` is unregistered, `instance()` returns `address(this)`, which equals the forged `from`, so `authenticate()` passes.
4. `_withdraw(...)` executes, transferring escrowed funds to the attacker-controlled beneficiary — without any legitimate peer IntentGateway ever having sent the message.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```
