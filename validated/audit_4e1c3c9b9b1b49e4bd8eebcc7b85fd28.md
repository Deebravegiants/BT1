Confirmed: the current mainline EVM contracts (`evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/IntentGatewayV2.sol`) fixed this pattern with `_instance()` reverting `UnknownInstance()` for unregistered chains, but the Tron-targeted contract `evm/tron/contracts/apps/IntentGatewayV2.sol` still uses the old, vulnerable pattern:

```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;   // fallback to "self" instead of rejecting
}

function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (instance(request.source) != module) revert Unauthorized();
}
```

This is functionally identical to CVE-2024-35190: instead of rejecting an unmatched/unauthenticated identity, the "matcher" falls back to a default value (`address(this)`) that ends up matching legitimate-looking input for every unregistered source. Because IntentGatewayV2 (and this Tron port) is deployed via CREATE2 at the **same address on every chain** — confirmed by the deployment scripts and docs (`evm/script/DeployIntentGateway.s.sol`, `sdk/packages/sdk/docs/.../2026-08-27-...md`, `evm/tests/foundry/IntentGatewayV2Test.sol:4631`) — every `dispatch`/`send`/`onAccept` call from this contract always sets `from = abi.encodePacked(address(this))`. That means for **any state machine not explicitly registered as a peer**, the wildcard fallback in `instance()` returns exactly `address(this)`, which trivially equals `module` on every such delivery, so `authenticate()` never rejects it.

### Title
IntentGatewayV2 (Tron) `instance()` fallback wrongly authenticates all messages from unregistered chains as legitimate peers - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`instance()` in the Tron `IntentGatewayV2` returns `address(this)` whenever a state machine id has no explicit deployment registered, instead of reverting. `authenticate()` then compares this fallback to `request.from`, which for a genuine `IntentGatewayV2` message dispatched from *any* chain is always `address(this)` on that chain (CREATE2 gives it the same address everywhere). The intended one-registered-peer check therefore silently matches every unregistered chain too.

### Finding Description
`authenticate()` is the sole gate protecting `RedeemEscrow`/`RefundEscrow` handling in `onAccept`: [1](#0-0) 
It relies on `instance()`: [2](#0-1) 
Compare with the corrected mainline implementation, which reverts with `UnknownInstance` instead of returning a matching default: [3](#0-2) 
Because the gateway is deployed with CREATE2 to the same address on every EVM/Tron chain — as documented in the deploy script and confirmed in tests — `address(this)` is a value any genuine dispatch from an `IntentGatewayV2` on *any* chain naturally has as its `from` field. Governance only explicitly registers a handful of chains via `NewDeployment` (see the `_instances` mapping populated in `onAccept`), but any chain that is never registered — including one Hyperbridge merely proxies requests for, or a state machine an attacker can get requests routed from — passes `authenticate()` because the fallback silently "matches" it.

### Impact Explanation
`RedeemEscrow`/`RefundEscrow` govern release of escrowed order funds (`withdraw()` transfers `_orders[commitment][token]` to an attacker-chosen beneficiary). An attacker able to get a `PostRequest` routed through Hyperbridge with `source` set to an unregistered state machine id and `from = abi.encodePacked(<any IntentGatewayV2 address>)` (trivially satisfied since the same address is used everywhere) can forge `WithdrawalRequest` bodies that pass authentication and drain escrowed tokens — direct theft of user funds.

### Likelihood Explanation
Reachable from a single relayed ISMP `PostRequest`/`RequestMessage` dispatched by any account holding, or forging via a permitted proxy path, a source chain identifier that Hyperbridge governance has not explicitly registered as a peer for this gateway. No privileged role is required to trigger the vulnerable code path; only a state machine/relayer capable of getting a message delivered to this app, consistent with the in-scope reachable-message-dispatch class.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. `UnknownInstance`) when `_instances[keccak256(stateMachineId)] == address(0)`, matching the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol`. Never fall back to `address(this)` as an implicit "match everything" default.

### Proof of Concept
1. Deploy `IntentGatewayV2` (Tron) with peers registered only for chains A and B (as in `initialize`/`NewDeployment`).
2. Attacker crafts a `PostRequest` with `source` = an unregistered state machine id `X`, `from = abi.encodePacked(address(intentGateway))` (the known, CREATE2-deterministic address), `to = abi.encodePacked(address(intentGateway))`, and `body` = `RequestKind.RedeemEscrow` + a `WithdrawalRequest` naming an existing `commitment` with nonzero `_orders[commitment][token]` and an attacker-controlled `beneficiary`.
3. Get this request delivered via the host (`onlyHost` — reachable through the standard relayed-message path, no special privilege on the gateway itself).
4. `onAccept` calls `authenticate(request)`, which calls `instance(X)`. Since `X` is unregistered, `instance()` returns `address(this)`, which equals `module` (`address(bytes20(request.from))`), so authentication passes.
5. `withdraw()` executes, transferring the escrowed tokens to the attacker's `beneficiary`.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L284-290)
```text
    /**
     * @dev Fetch the IntentGateway contract instance for a chain.
     */
    function instance(bytes calldata stateMachineId) public view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        return gateway == address(0) ? address(this) : gateway;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L292-300)
```text
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
