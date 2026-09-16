### Title
Unregistered Peer Chains Default to Self-Address, Enabling Forged Cross-Chain Message Authentication in Tron `IntentGatewayV2` - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` resolves an unregistered source chain's peer address to `address(this)` instead of rejecting it, unlike the canonical EVM `IntentGatewayV2`/`IntentsBase`, which reverts with `UnknownInstance` for the same case. This null/default-value fallback lets `authenticate()` pass for any incoming message whose `from` field equals the gateway's own address, on any chain the gateway has not explicitly registered as a peer — the same bug class as the daptin advisory, where a check silently treats an unset/zero reference as a match instead of rejecting it.

### Finding Description
In `evm/tron/contracts/apps/IntentGatewayV2.sol`: [1](#0-0) 
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

`_instances[keccak256(stateMachineId)]` defaults to `address(0)` for any state machine that has never been registered via a `NewDeployment` governance message. `instance()` maps that unset/zero case to `address(this)` rather than reverting. `authenticate()` then only checks `instance(request.source) != module`; for an unregistered source chain this collapses to `module != address(this)`. Any relayed, consensus-proof-verified `PostRequest` whose `source` is a chain the gateway has never registered as a peer, and whose `from` field happens to equal the gateway's own address, passes authentication as if it came from a legitimate registered peer instance.

This directly mirrors the daptin flaw: `CanRead`/`CanCreate`/etc. treat an unset (`0`) `p.UserId` as matching every requester, while `CanExecute` explicitly guards the zero case. Here, `instance()` treats an unset (`address(0)`) peer mapping as matching `address(this)`, while the canonical EVM `IntentsBase._authenticate` (and its test `testInstance`, which asserts `UnknownInstance` for an unregistered chain) explicitly guards against it: [2](#0-1) 
```
function _authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (_instance(request.source) != module) revert Unauthorized();
}
```
(`_instance` in the core `IntentsBase`/`ExtrinsicIntents` path reverts `UnknownInstance` for unregistered chains rather than defaulting to `address(this)`, as pinned by `testInstance` in `evm/tests/foundry/IntentGatewayV2Test.sol`.)

The Tron contract's `onAccept` dispatches on the decoded `RequestKind` — `RedeemEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, `RefundEscrow` — after calling `authenticate()`, so any governance-style or escrow-release action gated only by `authenticate()` inherits this weakness.

### Impact Explanation
Because `_filled`, escrow release (`RedeemEscrow`), refunds (`RefundEscrow`), and peer/parameter updates (`NewDeployment`, `UpdateParams`) are all reached through `authenticate()`, an attacker who can get a valid consensus-verified `PostRequest` accepted from any state machine the gateway has not registered as a peer — with `from` crafted/deployed to equal the gateway's own deterministic address on that chain — can forge messages that the Tron gateway treats as coming from a trusted peer instance. This can release escrowed funds to an attacker-controlled recipient or install a fraudulent peer/deployment mapping, i.e., theft or unauthorized app action reachable from a single relayed, proof-verified message.

### Likelihood Explanation
Exploitability depends on the attacker being able to produce (or already control) a contract/account at the gateway's exact address on an unregistered source chain — feasible on chains using the same CREATE2 deployer/salt/bytecode pattern documented for this gateway family (deterministic address across chains), particularly before governance has explicitly deployed/registered the gateway there. This narrows likelihood relative to a fully unauthenticated bypass, but the underlying authorization check itself is unconditionally wrong (defaults to trusting `address(this)` on any unregistered chain), matching the daptin pattern of "returns true whenever the compared value equals an unset default."

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g., with an `UnknownInstance` error) when `_instances[keccak256(stateMachineId)] == address(0)`, matching the canonical EVM `IntentsBase._instance` / `_authenticate` behavior, instead of silently falling back to `address(this)`. Add a regression test mirroring `testInstance` in `evm/tests/foundry/IntentGatewayV2Test.sol` that asserts an unregistered chain reverts rather than authenticating against the gateway's own address.

### Proof of Concept
1. Governance never calls `NewDeployment` to register state machine `X` as a peer of the Tron `IntentGatewayV2`, so `_instances[keccak256(X)] == address(0)`.
2. An attacker deploys (or otherwise controls) a contract at the exact address of the Tron gateway on chain `X` (feasible if the deployment pattern is deterministic/CREATE2-based and not yet claimed on `X`), then dispatches a `PostRequest` with `source = X`, `from = <that address>`, and a body encoding `RequestKind.RedeemEscrow` (or another privileged kind) targeting funds/parameters on the real gateway.
3. A relayer submits a valid consensus proof for chain `X`'s state (chain `X` itself may be entirely legitimate/attacker-uncontrolled at the consensus level — only the specific contract address is attacker-controlled).
4. `onAccept` → `authenticate(request)` computes `instance(X) == address(this)` (default fallback) and compares to `module == address(this)` (attacker's contract address) → passes.
5. The forged request is processed as if from a genuine registered peer, releasing escrow or mutating gateway state without legitimate authorization.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```
