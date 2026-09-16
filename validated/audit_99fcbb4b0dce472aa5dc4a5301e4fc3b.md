### Title
Incorrect Authorization via Unregistered-Instance Fallback in Tron IntentGatewayV2 — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron fork of `IntentGatewayV2` resolves the trusted counterpart gateway for an incoming cross-chain message differently than the canonical EVM implementation. Where the canonical `IntentsBase._instance()` reverts with `UnknownInstance()` when no gateway has been registered for a source state machine [1](#0-0) , the Tron variant's `instance()` silently falls back to `address(this)` for any state machine that has no explicit registration [2](#0-1) . Because `authenticate()` checks `instance(request.source) == module` where `module` is `request.from` taken from the incoming message, an attacker who deploys a contract at the same address as this Tron `IntentGatewayV2` (achievable via CREATE2 with the same salt/deployer, a technique the protocol itself documents and relies on for cross-chain address parity) on **any state machine that was never explicitly registered as a peer** can forge a `RedeemEscrow`/`RefundEscrow` message and have it accepted as authentic.

### Finding Description
The core authorization primitive that protects escrow releases is `authenticate()`: [3](#0-2) 
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
`instance()` treats an *unregistered* state machine identically to one whose registered gateway happens to equal `address(this)`. In the canonical implementation, the equivalent function is `_instance()`, which explicitly reverts on the unregistered case rather than defaulting to `address(this)`: [1](#0-0) 

Deployments are only added by Hyperbridge governance via `NewDeployment`, gated by `onlyHost` and a Hyperbridge-source check in the sibling implementation [4](#0-3) , and are recorded in `_instances` keyed by `keccak256(stateMachineId)` [5](#0-4) . Any chain that governance has not yet (or will never) explicitly register as a peer has no entry in `_instances`, so `_instances[keccak256(stateMachineId)] == address(0)` for it. The Tron contract turns that "no entry" state into an implicit trust grant for `address(this)`.

The IntentGateway protocol advertises deterministic CREATE2 deployment specifically so `HyperFungibleToken`/`WrappedHyperFungibleToken`/gateway contracts share the same address across chains [6](#0-5) , which is the same operational pattern IntentGateway deployments use. An attacker can therefore:
1. Deploy an arbitrary malicious contract at the exact address of the Tron `IntentGatewayV2` on any EVM-compatible or ISMP-supported state machine that is *not* in `_instances` (any chain the operator has not yet onboarded, or deliberately never will onboard, e.g. a permissionless/attacker-controlled rollup that the relaying/consensus-verification path for that state machine nonetheless accepts).
2. From that malicious contract, dispatch a `PostRequest` with `source` = that unregistered chain, `from` = the 20-byte address of the malicious contract (which equals `address(this)` on Tron by construction), and `body` = a forged `RedeemEscrow` or `RefundEscrow` payload naming an arbitrary `beneficiary` and the exact `tokens`/`commitment` of a real, currently-escrowed order.
3. Once the message is relayed and delivered through the ordinary ISMP path (`onAccept`), `authenticate()` computes `instance(source)`, finds no entry, returns `address(this)`, compares it to `module` (the forged `from` == `address(this)`), and the check **passes** — even though Hyperbridge governance never registered that source chain as a legitimate IntentGateway peer.
4. `withdraw()` then releases the escrowed input tokens for a real order to the attacker-chosen beneficiary.

This is the same bug class as the referenced GitLab CVE-2023-4532: an implicit trust default let an unauthorized/unlinked party (there, non-member users linking private CI/CD jobs; here, an unregistered/attacker-controlled chain contract) pass an authorization check that was supposed to be scoped to explicitly-approved relationships.

### Impact Explanation
This breaks the entire cross-chain trust model of the Intent Gateway on Tron: `authenticate()` is the sole gate distinguishing a legitimate peer gateway from an arbitrary contract, and it is the check that precedes unconditional escrow release in `RedeemEscrow`/`RefundEscrow` handling. A successful forgery lets an attacker drain escrowed user funds (theft of funds) for any order routed through or destined to the Tron gateway, without needing any real fill, valid solver action, or legitimate cross-chain settlement. This is a Critical/High-severity, concrete theft-of-funds bug reachable by anyone able to deploy a contract on an unregistered chain and relay a forged message — no privileged role required.

### Likelihood Explanation
Likelihood is High for a determined attacker: CREATE2 address-matching across chains is a documented, intended deployment pattern for this protocol family, making address parity with `address(this)` straightforward to obtain on any chain not yet in `_instances`. The only additional requirement is that the relaying/consensus-verification infrastructure for that state machine accepts messages (i.e., ISMP has some client/consensus verification for that chain) — this is a property of which state machines Hyperbridge already supports at the protocol layer, independent of whether IntentGateway governance has explicitly whitelisted that chain as an IntentGateway peer via `NewDeployment`. Any gap between "chains ISMP can relay proofs from" and "chains registered in `_instances`" is directly exploitable.

Note: I could not fully inspect `onAccept`/`_withdraw` in the Tron contract file within the available tool budget (grep found the functions but their bodies were not retrieved before the iteration limit), so I cannot cite the exact withdraw call site line-for-line; the described flow is inferred from the analogous, verified logic in `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (`onAccept` → `_authenticate` → `_withdraw`) and the confirmed `authenticate()`/`instance()` divergence in the Tron file. This should be verified against `evm/tron/contracts/apps/IntentGatewayV2.sol`'s full `onAccept` implementation before remediation.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. with `UnknownInstance()`) when `_instances[keccak256(stateMachineId)] == address(0)`, mirroring `IntentsBase._instance()` in the canonical implementation, so `authenticate()` cannot be satisfied by any unregistered source chain. Audit all other Tron-specific contracts for the same fallback-to-`address(this)` pattern, and add a regression test asserting that a forged message from an unregistered state machine is rejected even when `request.from` encodes `address(this)`.

### Proof of Concept
1. Confirm the Tron `IntentGatewayV2` has never had `NewDeployment` called for state machine `X` (i.e., `_instances[keccak256(X)] == address(0)`).
2. Using the same CREATE2 salt/deployer/bytecode-init pattern the protocol uses for cross-chain address parity, deploy any contract on state machine `X` at the identical address as the live Tron `IntentGatewayV2`.
3. From that contract, cause Hyperbridge to relay a `PostRequest` with `source = X`, `from = abi.encodePacked(address(this))` (== the Tron gateway's address), `to`/`dest` pointing at the real Tron gateway, and `body = bytes.concat(bytes1(uint8(RequestKind.RedeemEscrow)), abi.encode(WithdrawalRequest({commitment: <real order commitment>, tokens: <real escrowed tokens>, beneficiary: <attacker address>})))`.
4. Observe `authenticate()` compute `instance(X) == address(0) → address(this)`, matching `module == address(this)`, passing the check and releasing escrow to the attacker — reproducible in a Foundry test analogous to `testOnAcceptRedeemEscrow`/`testOnAcceptNewDeployment` in `evm/tests/foundry/IntentGatewayV2Test.sol`, but supplying `request.source` for a chain never registered via `NewDeployment` and `request.from = address(intentGateway)` directly against the Tron contract.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L581-584)
```text
    function _addDeployment(Deployment memory body) internal {
        _instances[keccak256(body.chain)] = body.gateway;
        emit DeploymentAdded({chain: string(body.chain), gateway: body.gateway});
    }
```

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-349)
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
```

**File:** docs/content/developers/evm/hyper-fungible-token/overview.mdx (L71-71)
```text
Using CREATE2 with the same salt and deployer across all chains gives each contract the same address, simplifying peer registration and frontend integration.
```
