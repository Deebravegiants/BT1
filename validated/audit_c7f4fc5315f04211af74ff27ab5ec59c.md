### Title
Tron `IntentGatewayV2.instance()` fallback to `address(this)` lets an attacker forge peer-authenticated governance/escrow messages from any unregistered chain - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` resolves peer-gateway addresses with a fallback that returns `address(this)` when no instance is registered for a given source `stateMachineId`, instead of reverting. `authenticate()` then treats any incoming request whose `from` field equals `address(this)` as coming from a "known instance," even when the claimed source chain has never had a peer gateway registered.

### Finding Description
`instance()` in the Tron contract: [1](#0-0) 

returns `address(this)` for any `stateMachineId` that has no registered `_instances` entry, rather than reverting. `authenticate()` uses this value as the trust anchor for incoming ISMP `PostRequest`s: [2](#0-1) 

Because `IntentGatewayV2` deployments are deterministically created via CREATE2 so that "each peer is bound to `address(this)`" across chains (documented in the mainline EVM contract's `initialize`), the contract's own address is a fixed, publicly-known value. Any chain that Hyperbridge governance has not yet registered as a peer (`_instances[keccak256(chainId)] == address(0)`) is therefore treated as authenticated for a request whose `from` equals that deterministic address — with no `_addDeployment`/governance action required.

This is the exact bug class of the referenced advisory: a fallback that silently substitutes a fixed/predictable value for "not configured/not found," and callers implicitly trust that fallback as if it were the real, verified value (there, a hardcoded Program Files path treated as trusted `git.exe`; here, `address(this)` treated as a verified peer gateway).

Note that the mainline production contract already fixed this exact defect: `IntentsBase._instance()` explicitly reverts with `UnknownInstance()` on an unregistered chain: [3](#0-2) 

and test coverage explicitly encodes this as the expected/secure behavior: [4](#0-3) 

The Tron contract, however, still contains the vulnerable pre-fix pattern.

### Impact Explanation
`authenticate()` gates `onAccept` (the ISMP handler for incoming `PostRequest`s), which dispatches on `RequestKind`: `RedeemEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, `RefundEscrow`. If an attacker can get a legitimately-verified ISMP message delivered from any state machine that Hyperbridge governance has not registered as a peer for the Tron gateway (i.e., any chain outside the currently configured `_instances` set, including a brand-new/unsupported chain the attacker fully controls), and encodes the message `from` field as the Tron gateway's own deterministic CREATE2 address, `authenticate()` will accept it as coming from a "known instance." This allows an attacker to:
- Register a forged `NewDeployment` (poisoning `_instances` with attacker-controlled gateway addresses for other chains),
- Push a malicious `UpdateParams` (changing `dispatcher`, `priceOracle`, fee parameters),
- Trigger `RedeemEscrow`/`RefundEscrow`/`SweepDust` against real escrowed user funds held by the Tron gateway.

Given the Tron gateway custodies escrowed order funds and governance parameters, this is a concrete path to theft/misappropriation of escrowed funds and unauthorized app configuration changes — satisfying "concrete theft... or unauthorized app action."

### Likelihood Explanation
Exploitation requires the attacker to (a) control or stand up a state machine that ISMP consensus can verify (any state machine with a supported consensus client that is simply not yet on Hyperbridge's `_instances` allow-list for this gateway — this is plausible since new chains are onboarded over time and the fallback is silently permissive during that gap), and (b) reproduce the deterministic CREATE2 deployer address as the `from` field of the dispatched message on that chain (feasible since the deployment scheme is public/documented). No admin, governance, or relayer compromise is needed — a single dispatched/relayed message with a proof from an unregistered but real chain is sufficient, matching the "unprivileged relayer/message path" reachability required.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g., with `UnknownInstance()`/`Unauthorized()`) when `_instances[keccak256(stateMachineId)] == address(0)`, mirroring the fix already applied in `evm/src/apps/intentsv2/IntentsBase.sol::_instance()`. Do not fall back to `address(this)` as an implicit trust anchor for unregistered chains.

### Proof of Concept
1. Identify a state machine ID `X` that has no entry in `_instances` on the Tron `IntentGatewayV2` (i.e., `instance(X) == address(this)` per the current fallback).
2. From chain `X` (any chain with an ISMP-verifiable consensus client, including one the attacker controls/deploys on), dispatch a `PostRequest` with `source = X`, `from = abi.encodePacked(address(intentGatewayOnTron))` (the deterministic CREATE2 address), and `body` set to a crafted `RedeemEscrow`/`NewDeployment`/`UpdateParams` payload.
3. Have this request relayed with a valid consensus/state proof for chain `X` (the proof is legitimate — the vulnerability isn't in proof verification but in the peer-authentication fallback).
4. `onAccept` calls `authenticate(request)` → `instance(X)` returns `address(this)` (fallback) → matches `module = address(this)` decoded from `from` → passes authentication despite chain `X` never being registered as a peer.
5. The forged request body executes as governance/escrow logic against the Tron gateway's real state and funds.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L3149-3154)
```text
    function testInstance() public {
        bytes memory stateMachineId = bytes("TEST_CHAIN");

        // An unregistered chain reverts with UnknownInstance.
        vm.expectRevert(IntentsBase.UnknownInstance.selector);
        intentGateway.instance(stateMachineId);
```
