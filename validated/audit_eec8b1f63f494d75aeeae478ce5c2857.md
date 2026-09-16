## Title
Unregistered source-chain fallback collapses distinct chain origins into a single trusted "self" origin, enabling forged escrow redemption/refund - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.instance()` on the Tron/legacy EVM variant returns `address(this)` for any state machine that has no registered deployment, instead of reverting. `authenticate()` uses this same function to validate `request.from` against `instance(request.source)`. As a result, a POST request whose declared `source` is any chain Hyperbridge relays for but that this gateway has never registered via `NewDeployment` is treated as coming from a "known instance" as long as `request.from == address(this)` — the gateway's own address — collapsing every un-configured chain's security origin into the gateway's own trusted identity.

### Finding Description
The authentication routine is: [1](#0-0) 

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

Contrast this with the current mainline implementation in `IntentsBase.sol`, which explicitly rejects unknown chains: [2](#0-1) 

```
function _instance(bytes calldata stateMachineId) internal view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    if (gateway == address(0)) revert UnknownInstance();
    return gateway;
}
```

`authenticate()` is invoked directly from `onAccept` for `RedeemEscrow`/`RefundEscrow` requests, before any escrow funds move: [3](#0-2) 

Because the fallback silently substitutes `address(this)` for any unregistered `stateMachineId`, the gate does not actually bind "who counts as this state machine's authorized module" per source chain — instead it degrades to "does `request.from` equal my own address," for every chain that governance has not yet explicitly configured via `_addDeployment`/`NewDeployment`. This is the same class of bug as CVE-2020-3864: a security check that is supposed to enforce a unique origin per context (per source `StateMachine`) instead lets multiple distinct, unconfigured contexts share one trusted identity.

Since the Hyperbridge/IntentGateway ecosystem is documented to deploy the *same* contract bytecode/address deterministically via CREATE2 across chains, this can happen legitimately without any attacker action: the very first delivery ever received from a newly supported chain — before governance calls `add_deployment`/`NewDeployment` for it — is auto-trusted rather than rejected, because `instance()` never distinguishes "not yet configured" from "configured as self."

### Impact Explanation
If ISMP relays a forged or premature `PostRequest` with `source` set to any chain not yet present in `_instances`, and `from` equal to `address(this)` (the gateway's own address, which is the same on every EVM-compatible chain per the project's CREATE2 deployment convention), `authenticate()` passes. The attacker- or relayer-controlled `WithdrawalRequest` body is then decoded and executed by `withdraw()`, releasing escrowed tokens (`RedeemEscrow`) or refunding orders (`RefundEscrow`) without a legitimate order ever having existed on that "source" chain — a direct theft/drain of escrowed funds from the gateway (Critical/High: unbacked mint-equivalent for withdrawal accounting; concrete theft of escrowed funds).

### Likelihood Explanation
Exploitability depends on getting a `PostRequest` accepted by `onAccept` with an attacker-chosen `source`/`body` from a state machine Hyperbridge already relays for but the gateway has not registered — this requires either a genuine gap in the deployment rollout (new chain supported by Hyperbridge before `NewDeployment` runs for this gateway) or the ability to dispatch through some already-connected but unconfigured state machine with `from == address(this)`. This is not a trivial single-transaction forgery by an arbitrary unprivileged user (it still requires a valid ISMP-proven delivery), but it is reachable purely through the protocol's ordinary permissionless relaying path with no admin/governance compromise, making it a real, if narrower, "unbacked withdrawal" window rather than a hypothetical.

### Recommendation
Change `instance()` (and any other lookup relying on this default) to revert (e.g. `UnknownInstance`) when no explicit deployment is registered, matching the corrected behavior already present in `evm/src/apps/intentsv2/IntentsBase.sol::_instance`. Audit all other call sites of `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` (e.g. the dispatch-side usage for `RefundEscrow`) to ensure they don't rely on the same silent self-fallback.

### Proof of Concept
1. Deploy/observe `IntentGatewayV2` (Tron variant) at address `G` on the destination chain; no `NewDeployment` has been submitted for state machine `X`.
2. Craft/obtain a `PostRequest` proven by Hyperbridge with `source = X`, `from = abi.encodePacked(G)`, `to = abi.encodePacked(G)`, `body = [RedeemEscrow] ++ abi.encode(WithdrawalRequest{commitment, tokens, beneficiary=attacker})`.
3. Relay it through `HandlerV2`/`EvmHost` to `IntentGatewayV2.onAccept`.
4. `authenticate()` calls `instance(X)`, which returns `address(this) == G` since `X` is unregistered, matching `module = G` parsed from `from` — authentication passes.
5. `withdraw()` executes, transferring escrowed tokens to `beneficiary` even though no legitimate order origin ever existed on chain `X`. [3](#0-2) [1](#0-0)

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-635)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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
