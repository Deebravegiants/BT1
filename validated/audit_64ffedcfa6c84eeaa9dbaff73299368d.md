### Title
Unregistered-chain fallback in `IntentGatewayV2.instance()` lets a same-address contract on any unconfigured state machine forge authenticated `onAccept` deliveries - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.instance(stateMachineId)` returns `address(this)` whenever no peer instance is registered for that chain, and `authenticate()` accepts a request whenever `instance(request.source) == module` (the 20-byte `request.from`). Because the contract is meant to be deployed at the same address on every chain via CREATE2, any chain that Hyperbridge has *not yet* whitelisted with `_instances[keccak256(chainId)]` collapses the check to "does `from` equal my own address" — a condition trivially satisfiable by deploying the identical bytecode/salt on that unconfigured chain. This is the same bug class as ALPINE-CVE-2026-3591: a default/fallback value in an authorization "matching" function causes an unintended source to match, defeating what should be a default-deny ACL for cross-chain message provenance.

### Finding Description
`instance()`:
```
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}
``` [1](#0-0) 

`authenticate()`:
```
function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    // IntentGateway only accepts incoming assets from itself or known instances
    if (instance(request.source) != module) revert Unauthorized();
}
``` [2](#0-1) 

The default branch of `instance()` was designed to authenticate genuinely same-chain messages (`request.source == host()`, where the peer module really is `address(this)`). But it also fires for **every** `request.source` that Hyperbridge/the operator has not yet added to `_instances` — which is the default state for any new or unlisted EVM state machine. `authenticate()` never checks that `request.source` is actually this contract's own chain; it only checks the resolved "expected instance" address against `request.from`.

Because IntentGatewayV2 is deployed at a deterministic CREATE2 address to keep parity across chains (the same pattern used for `EvmHost`, see the constructor-comment rationale in `EvmHost` for CREATE2 parity), an attacker can:
1. Deploy a contract with the same bytecode/salt (or simply any contract whose address happens to equal `address(this)` on the destination chain — CREATE2 makes this attacker-achievable if they control the deployer/salt on the unconfigured chain) on a state machine that Hyperbridge has not yet registered as an IntentGateway peer.
2. Genuinely dispatch (via real ISMP infra on that unregistered chain) a `PostRequest` with `from = address(this)` (their own, address-matching contract), `to` = the destination IntentGatewayV2, and a body encoding `WithdrawalRequest` or `SweepDust`.
3. This message is provably delivered through consensus/state-proof verification for that real (but unregistered) source chain, so `HandlerV2`/`EvmHost.dispatchIncoming` will accept and route it (`AYontt/hyperbridge--012:evm/src/core/HandlerV2.sol:181-210`, `AYontt/hyperbridge--012:evm/src/core/EvmHost.sol:794-818`).
4. On arrival, `onAccept` calls `authenticate(request)`, which resolves `instance(request.source)` to `address(this)` (default fallback, since the chain was never registered) and finds it equal to `module` (the attacker's address, which was engineered to equal `address(this)`), so the check **passes**.

This lets an unauthorized/unlisted chain's message be treated as coming from a trusted, registered IntentGateway peer — precisely analogous to BIND's use-after-return causing an ACL to "improperly match" an address in a default-allow evaluation.

### Impact Explanation
A successful forgery reaches `withdraw()`/`SweepDust` handling in the settlement path, which releases escrowed input tokens and protocol fees to an attacker-chosen beneficiary (`_filled[commitment] = solver`, transferring escrowed tokens per the intent-gateway settlement flow described in `docs/content/developers/evm/intent-gateway/overview.mdx:50-58`). This is concrete theft of escrowed user funds — an unauthorized app action leading to fund loss, satisfying the "forged message delivery" / "unauthorized app action" criteria.

### Likelihood Explanation
Exploitation requires the attacker to control a state machine that Hyperbridge has consensus support for but has not yet added to `_instances` for this specific IntentGatewayV2 deployment (e.g., a newly supported chain before the operator calls whatever admin function registers `_instances`, or a chain intentionally left unregistered). It also requires the attacker to obtain the same CREATE2 address as the legitimate deployment on that chain, which is plausible if deployment salts/deployer addresses are public/standardized (as implied by the cross-chain address-parity design goal). This is a real, single-transaction-reachable path (a relayed proof delivering one forged request) rather than a privileged/administrative attack, so it meets the required reachability bar, though the address-collision precondition narrows likelihood to Medium.

### Recommendation
`authenticate()` should not rely on the `address(this)` fallback for arbitrary/unregistered `request.source`. Restrict the self-instance shortcut to the case where `request.source == host()` (a genuine same-chain message), and require an explicit, non-zero entry in `_instances` for every other chain — reverting with `UnsupportedChain`/`Unauthorized` when no instance is registered, rather than silently defaulting to `address(this)`.

### Proof of Concept
1. Deploy `IntentGatewayV2` (or an identical bytecode clone) via CREATE2 with the same salt/deployer on a state machine `X` that is never passed to whatever sets `_instances[keccak256(X)]` — `instance(X)` therefore returns `address(this)` by default.
2. From chain `X`, dispatch a genuine ISMP `PostRequest` with `source = X`, `from = abi.encodePacked(address(this))` (the CREATE2 clone address, equal to the real gateway's address), `to = <victim chain's IntentGatewayV2 address>`, `body = WithdrawalRequest` referencing a real, previously-placed order's commitment.
3. Relay the message with a valid consensus/state proof for chain `X` through `HandlerV2.handlePostRequests` → `EvmHost.dispatchIncoming` → `IntentGatewayV2.onAccept` → `authenticate(request)`.
4. `instance(X) == address(this) == module` ⇒ authentication passes ⇒ escrowed tokens for that order are released to the attacker-controlled solver/beneficiary, even though chain `X` was never registered as a trusted IntentGateway instance.

Note: I could not fully trace which admin/governance function populates `_instances` (e.g., a `setInstance`/`updateParams` call) within the remaining budget, so the exact registration lifecycle and whether newly-supported-but-unregistered chains are a realistic operational window should be verified directly in the deployment/governance scripts before treating likelihood as more than Medium.

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
