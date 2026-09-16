### Title
Unregistered source-chain fallback in `instance()` lets a forged instance match `address(this)`, bypassing `authenticate()` and unlocking escrowed funds - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.instance()` in the Tron variant returns `address(this)` for any state machine that has never been registered via `NewDeployment`, instead of reverting like the mainline implementation. Because `authenticate()` trusts whatever `instance()` returns as the legitimate peer address, an attacker who can deploy a contract at the same address as this gateway on any other real, consensus-verified chain (even one never explicitly registered as a peer) can dispatch a genuinely-proven cross-chain message that passes authentication and reaches privileged handlers such as `RedeemEscrow`/`RefundEscrow`.

### Finding Description
The Tron gateway's helper: [1](#0-0) 
defaults an unregistered state machine to `address(this)`:
```
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}

function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (instance(request.source) != module) revert Unauthorized();
}
```
This contrasts with the mainline `IntentsBase._instance()` used by `evm/src/apps/intentsv2/IntentsBase.sol` and `evm/src/apps/intentsv2/ExtrinsicIntents.sol`, which explicitly reverts with `UnknownInstance` for any chain that was never registered: [2](#0-1) 

The parallel `_authenticate` in `ExtrinsicIntents.sol` relies on this revert-on-unknown behavior to reject any message from a chain that was not deliberately whitelisted: [3](#0-2) 

The Tron contract instead has no equivalent input validation guarding the case where `_instances[keccak256(stateMachineId)]` is unset — it silently substitutes `address(this)` as a "trusted" default. Any message whose `request.source` hashes to an unregistered slot, and whose `request.from` is set to `bytes20(address(this))`, will satisfy `instance(request.source) == module`, exactly analogous to the reported bug class ("no input validation for the forwarder/account parameters used in an approval check").

### Impact Explanation
`authenticate()` gates `onAccept`'s decoding of `RequestKind`, including `RedeemEscrow` and `RefundEscrow`, which release escrowed order funds to a beneficiary address supplied in the request body. A forged instance match lets an attacker who controls (or can deploy identical bytecode/address at) some chain that the gateway has never explicitly whitelisted submit a genuinely-proven cross-chain message that the gateway treats as coming from a legitimate peer instance of itself. This directly threatens theft of escrowed order funds — concrete loss of user/solver funds held by the Tron `IntentGatewayV2` contract.

### Likelihood Explanation
Exploitation requires the attacker to get a real state-machine proof accepted by the local host for a source chain the deployer never called `NewDeployment` for, and to control an address matching the Tron gateway's address (or otherwise supply `from = bytes20(address(this))`) on that source chain. This is a design/logic flaw rather than a race condition — every unregistered chain is silently trusted by default — so any chain onboarded by Hyperbridge governance for consensus verification but not yet explicitly added as a peer to this specific app is an open door, making likelihood high relative to the deliberate whitelist model used everywhere else in the codebase.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. with `UnknownInstance`) when no deployment is registered for the given state machine id, matching the behavior of `IntentsBase._instance()` in the canonical implementation, rather than defaulting to `address(this)`.

### Proof of Concept
1. Governance has registered peers for chains A and B via `NewDeployment`, but never for chain C, even though chain C has a working, consensus-verified Hyperbridge light client.
2. Attacker deploys a contract at the same address as the Tron `IntentGatewayV2` instance on chain C (or otherwise arranges to control that address on chain C).
3. Attacker's contract on chain C dispatches a `PostRequest` to the Tron gateway with `body` = `RedeemEscrow` kind targeting a real, unfilled order commitment, and `from` = `bytes20(address(thisGateway))`.
4. The message is relayed with a valid consensus proof for chain C and delivered through `HandlerV2`/host `dispatchIncoming` to `onAccept`.
5. `authenticate()` calls `instance(chain_C_id)`, which returns `address(this)` because chain C was never registered, matching `module` from `request.from`; authentication passes.
6. `onAccept` proceeds to execute `RedeemEscrow`, releasing escrowed tokens to an attacker-controlled beneficiary.

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
