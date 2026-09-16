## Title
Unregistered source state machines fall back to trusting the gateway's own address in Tron `IntentGatewayV2.authenticate()` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`evm/tron/contracts/apps/IntentGatewayV2.instance()` returns `address(this)` whenever a state-machine ID has no registered peer, instead of rejecting it. `authenticate()` uses this fallback to authorize incoming cross-chain messages, so any unregistered/unconfigured source chain is implicitly treated as if it were the gateway itself.

### Finding Description
`instance()` is meant to resolve the trusted peer `IntentGatewayV2` address for a given source state machine: [1](#0-0) 

```solidity
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

When `_instances[keccak256(stateMachineId)]` is unset (the default state for every state machine that governance has not explicitly registered via `_addDeployment` — the "documented but optional allowlist" analog of LimeSurvey's unset `allowedHosts`), `instance()` silently falls back to `address(this)` rather than reverting. `authenticate()` then accepts any incoming `PostRequest` whose `request.from` equals the gateway's own address, regardless of which chain (`request.source`) it claims to originate from.

This is the exact bug class in the LimeSurvey advisory: a security check is gated by an allow/deny list that defaults to "no restriction" when unconfigured, and the code that should refuse an unrecognized value instead falls back to trusting a value that is easy for an attacker to match (the client-controlled Host header there; the gateway's own well-known, deterministically-deployed address here).

The corrected pattern already exists elsewhere in the same codebase — `IntentsBase._instance()` in the current EVM app reverts with `UnknownInstance` instead of returning a fallback address: [2](#0-1) 

This confirms the tron contract's behavior is a regression/divergence from the hardened logic, not an intentional design choice.

### Impact Explanation
`IntentGatewayV2` (and its `ExtrinsicIntents`/`IntentsBase` analogs) is the escrow contract for the Hyperbridge intents protocol: incoming authenticated `PostRequest`s drive `RedeemEscrow` (release escrowed input tokens to a filler), `RefundEscrow`, `NewDeployment` (register a new trusted peer address for a state machine), `UpdateParams`, and `SweepDust`. If an attacker can get Hyperbridge's consensus layer to accept a `PostRequest` whose `source` is any EVM (or substrate) state machine that this gateway has not yet had a peer registered for, and whose `from` field is set to `abi.encodePacked(address(this))` (the gateway's own address, which is public and — because these gateways are deployed deterministically via CREATE2 with a fixed salt/bytecode across chains — is often reproducible by a third party deploying identical bytecode from a permissionless CREATE2 factory on a new chain), the message passes `authenticate()`. This can be used to forge `RedeemEscrow`/`RefundEscrow` deliveries that drain escrowed user funds, or to forge `NewDeployment` and hijack the trusted-peer registry for a chain, permanently misrouting or capturing future cross-chain intents. This satisfies "concrete theft of funds" / "unauthorized app action."

### Likelihood Explanation
Exploitability depends on whether Hyperbridge's consensus clients will produce a valid state/consensus proof for an arbitrary, attacker-supplied EVM (or other) chain ID that has never been registered as an `IntentGatewayV2` peer — e.g., a fresh EVM chain using a generic EVM light client, or any state machine ID an attacker can stand up a real chain for. Given Hyperbridge already supports generic EVM state-machine IDs and permissionless relaying/dispatch, an attacker able to deploy a contract at the correct deterministic address (matching this gateway's own address) on such a chain, and dispatch a request with `from = address(this)`, needs no privileged access — only a chain the protocol is willing to verify proofs from and standard deterministic-deployment tooling. This fits the required threat model (single relayed/dispatched cross-chain message), but confirming end-to-end reachability requires knowing whether governance actually pre-registers every EVM chain ID before it's usable, and whether the deterministic deployment salt/bytecode is public and reproducible for this exact tron contract — I could not verify this from the indexed files alone.

### Recommendation
Change `instance()` (or `authenticate()`) in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g., `UnknownInstance`/`Unauthorized`) when `_instances[keccak256(stateMachineId)] == address(0)`, matching the `_instance()` implementation already used in `evm/src/apps/intentsv2/IntentsBase.sol`. Audit all other call sites of `instance()`/`_instances` in the tron contracts for the same silent-fallback pattern, and add a regression test asserting that messages from unregistered state machines are always rejected, never implicitly authorized.

### Proof of Concept
1. Identify a state machine ID `X` for which `IntentGatewayV2._instances[keccak256(X)]` has never been set (any chain governance has not yet called `_addDeployment` for).
2. Deploy (or otherwise obtain the ability to dispatch from) a contract at the same address as this `IntentGatewayV2` instance on a chain corresponding to `X` that Hyperbridge's consensus layer can produce valid proofs for.
3. From that contract, dispatch an ISMP `PostRequest` with `from = abi.encodePacked(address(this))`, `source = X`, and body encoding a `RedeemEscrow`/`NewDeployment` request kind.
4. Relay the request through Hyperbridge to the real `IntentGatewayV2` deployment; `authenticate()` calls `instance(X)`, which returns `address(this)` (the fallback), matching `module` derived from `request.from`, so the forged request passes authentication and executes. [1](#0-0) [3](#0-2)

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
