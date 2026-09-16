Found it. The vulnerability class from CVE-2025-0443 — insufficient validation of a crafted input enabling privilege escalation — maps directly onto an authentication-default flaw in the Tron variant of the intent gateway.

### Title
Unregistered-chain fallback in `IntentGatewayV2.instance()`/`authenticate()` lets a forged peer message drain escrow — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.instance()` in the Tron contracts defaults to `address(this)` for any state machine that has no registered peer gateway, instead of reverting. `authenticate()`, which gates `RedeemEscrow`/`RefundEscrow` withdrawals in `onAccept`, relies on this function to decide whether an inbound `PostRequest` came from a trusted peer.

### Finding Description
`instance()` is defined as: [1](#0-0) 

and `authenticate()` uses it as the sole check for whether an inbound message is from a "known instance": [2](#0-1) 

`onAccept` routes `RedeemEscrow` and `RefundEscrow` through `authenticate()` with no additional relayer/source gate: [3](#0-2) 

Because `instance(request.source)` returns `address(this)` whenever `_instances[keccak256(source)]` has never been set (i.e., the chain is not yet registered as a peer via a governance `NewDeployment`), `authenticate()` passes as long as `request.from` (the 20-byte address of the dispatching contract on the source chain, set by that source chain's own ISMP host) equals this gateway's own address. Any state machine that Hyperbridge has a live, working consensus client for — but for which this particular Tron gateway has not yet registered a peer deployment — can produce a genuine, consensus-verified `PostRequest` whose `from` field is the address of an attacker-controlled contract. If that contract's address collides with the gateway's own address (trivially achievable via CREATE2/CREATE with a chosen deployer nonce on an EVM-compatible chain, which is common for consistent-multi-chain-address deployments this protocol already relies on), `authenticate()` treats it as coming from "itself," i.e. a trusted peer.

This is the direct analog of the CVE's bug class: a default/fallback value collides with an unauthenticated-input value ("insufficient data validation"), letting a crafted message escalate privilege — here, escalating a from an unconfigured/untrusted source into a trusted peer.

Contrast with the current, fixed logic in the mainline EVM/SDK contracts, which reverts instead of defaulting to self: [4](#0-3) 

The Tron variant was not updated to match, leaving the collision-prone fallback live.

### Impact Explanation
`RedeemEscrow`/`RefundEscrow` release escrowed order funds (`_orders[commitment][token]`) to a beneficiary specified in the attacker-forged `WithdrawalRequest` body. Successfully forging one of these requests lets an attacker drain any/all escrowed input tokens held by the gateway to an address of their choosing — direct theft of user funds, satisfying "concrete theft ... of funds" in the validation criteria. It is reachable by a single relayed proof/message from an unprivileged actor (anyone able to dispatch a genuine ISMP message from a state machine Hyperbridge already tracks), matching the "intents escrow" scope explicitly called out.

### Likelihood Explanation
Exploitability depends on the attacker being able to deploy a contract whose address matches the gateway's own address on some chain Hyperbridge has consensus support for but that this Tron gateway hasn't registered as a peer yet. This is a realistic scenario for a multi-chain rollout: gateways are deployed incrementally chain-by-chain via CREATE2 for address consistency, and Hyperbridge's consensus-client coverage for chains typically precedes the intents team's explicit `NewDeployment` registration for each of them, creating a real window during which any not-yet-registered-but-consensus-supported chain is a viable attack vector — self-inflicted by the fallback default, not by any protocol operator error.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. `UnknownInstance`) when `_instances[keccak256(stateMachineId)] == address(0)`, matching `evm/src/apps/intentsv2/IntentsBase.sol::_instance`, and update `authenticate()`/callers accordingly so no unregistered chain can pass the peer check by any address collision.

### Proof of Concept
1. Hyperbridge has a working consensus client for chain `X` (any EVM-compatible chain not yet in `_instances` on the Tron `IntentGatewayV2`).
2. Attacker deploys a contract on chain `X` at the exact address of the deployed `IntentGatewayV2` (achievable via CREATE2 with a chosen salt/bytecode, mirroring the protocol's own consistent-address deployment pattern).
3. From that contract, dispatch a genuine ISMP `PostRequest` with `source = X`, `to = <TronGateway>`, `body = [RedeemEscrow, WithdrawalRequest{commitment: <victim order>, tokens: <victim tokens>, beneficiary: <attacker>}]`.
4. Relay the request with a valid consensus/state proof through the normal handler path to the Tron `IntentGatewayV2.onAccept`.
5. `authenticate()` computes `instance(X) == address(this)` (unregistered default) and `module == address(this)` (attacker's contract address collision) → passes.
6. `withdraw()` releases the victim's escrowed tokens to the attacker-specified beneficiary.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L287-290)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-638)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```
