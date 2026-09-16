### Title
`instance()` fallback to `address(this)` for unregistered chains lets a rogue CREATE2-cloned gateway bypass source-authentication - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron `IntentGatewayV2.instance()` function, unlike its EVM counterparts, returns `address(this)` when a state machine has no registered peer instance, instead of reverting. Since `authenticate()` uses `instance(request.source)` to validate the sender of an incoming cross-chain message, any request whose `source` chain is *not yet registered* is authenticated against the local contract's own address rather than being rejected — an identity-check bypass analogous to the KernelSU apk-path lookup flaw.

### Finding Description
`authenticate()` verifies that an incoming `PostRequest` really originates from a legitimate peer `IntentGatewayV2` deployment on the claimed source chain: [1](#0-0) 

It calls `instance(request.source)`, which — unlike `IntentsBase._instance()` used by the mainline EVM contract (`evm/src/apps/intentsv2/IntentsBase.sol`, which reverts with `UnknownInstance()` when `_instances[keccak256(stateMachineId)] == address(0)`) — silently falls back to `address(this)`: [2](#0-1) 

Compare with the fail-closed reference implementation: [3](#0-2) 

This means: for any state machine `request.source` that Hyperbridge governance has *not* registered a peer for on this gateway, `instance(request.source)` returns `address(this)` (the local gateway's own address), and `authenticate()` will accept the request as long as `request.from` (bytes20) decodes to that same address. Since `IntentGatewayV2` is designed to be deployed at the same CREATE2 address across every chain the protocol supports, an attacker only needs to deploy a bytecode-identical contract via CREATE2 (or otherwise land a contract at that exact address) on any Hyperbridge-supported chain that Hyperbridge governance simply hasn't yet added as a `Deployment` for *this* gateway instance. That attacker-controlled contract, dispatching from that unregistered chain with `from = address(this)`, passes `authenticate()` as if it were a real registered peer.

### Impact Explanation
`authenticate()` gates the `RedeemEscrow` and `RefundEscrow` request kinds (the ones actually reachable by a relayed cross-chain message, as opposed to governance-only kinds gated separately). A forged, "authenticated" `RedeemEscrow`/`RefundEscrow` request lets an attacker release escrowed order funds (`_orders[commitment][token]`) held by the gateway to an attacker-chosen beneficiary, without ever having filled or legitimately interacted with the corresponding order on a real peer chain. This is concrete theft of escrowed user funds — the same class of impact as the referenced CVE (unauthorized privileged action due to an identity check silently accepting an unintended fallback value).

### Likelihood Explanation
Reachability requires: (1) Hyperbridge having a working consensus/state-proof client for some chain that has not yet been registered as an IntentGatewayV2 peer (plausible during rollout/onboarding of new chains, or simply any Hyperbridge-connected chain the operator never intended to register this gateway on), and (2) the attacker deploying a contract at the exact CREATE2 address of the legitimate gateway on that chain. Because the whole gateway family is explicitly designed for deterministic same-address CREATE2 deployment across chains, reproducing that address on an arbitrary chain is a normal, low-cost action for anyone with access to the same factory/salt/bytecode (or any means of getting `request.from` to equal `address(this)`). No admin, governance, or relayer collusion is required — an ordinary relayer/attacker submitting one crafted proof triggers it. This is Medium-to-High likelihood conditioned on the existence of at least one unregistered-but-Hyperbridge-supported source chain, which is a normal, transient operational state.

### Recommendation
Change `instance()` (and `authenticate()`'s reliance on it) in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g. with an `UnknownInstance` error, mirroring `IntentsBase._instance()`) when no peer is registered for `request.source`, instead of returning `address(this)`. Audit all other callers of the public `instance()` view function to ensure none of them depend on the fallback-to-self behavior for legitimate functionality before tightening it.

### Proof of Concept
1. Hyperbridge has a consensus client for chain `X`, but governance has never dispatched a `NewDeployment` registering an `IntentGatewayV2` peer for `X` on the target chain's gateway (`_instances[keccak256(X)] == address(0)`).
2. Attacker deploys a contract with the same CREATE2 salt/bytecode as the legitimate `IntentGatewayV2` on chain `X`, obtaining the same address `A` as the real gateway (`address(this)` on the target chain).
3. Attacker dispatches (or otherwise gets included) an ISMP `PostRequest` from chain `X` with `source = X`, `from = abi.encodePacked(A)`, `body = [RedeemEscrow, WithdrawalRequest{commitment: <victim's real order commitment>, beneficiary: attacker, ...}]`.
4. On delivery, `onAccept` calls `authenticate(request)`: `instance(X)` returns `address(this) == A` (fallback path, since `X` is unregistered) → matches `module = A` decoded from `request.from` → authentication passes.
5. The withdrawal logic executes, releasing the victim's escrowed tokens to the attacker's beneficiary — despite chain `X` never having a real, governance-approved gateway peer.

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
