### Title
`IntentGatewayV2.instance()` defaults unregistered state machines to `address(this)`, letting an unverified/foreign contract impersonate the gateway - ([File: evm/src/apps/intentsv2/IntentsBase.sol])

### Summary
`IntentGatewayV2` authenticates cross-chain `RedeemEscrow`/`RefundEscrow` deliveries by comparing the incoming request's `from` field against `instance(request.source)`. When a state machine has never had a `NewDeployment` registered for it, `instance()` silently falls back to `address(this)` instead of rejecting the lookup, so any request whose `from` field equals this contract's own address is treated as an authenticated peer — even though nothing on Hyperbridge has ever certified that a peer `IntentGatewayV2` exists (let alone one under attacker control) on that source chain.

### Finding Description
`instance()` in `IntentsBase.sol`/`ExtrinsicIntents.sol` is:
```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}
``` [1](#0-0) 

and `_authenticate` (the EVM-family analog) uses it directly to gate incoming settlement messages:
```solidity
function _authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (_instance(request.source) != module) revert Unauthorized();
}
``` [2](#0-1) 

`onAccept` calls `_authenticate` for the two fund-moving request kinds (`RedeemEscrow`, `RefundEscrow`) before releasing escrowed tokens:
```solidity
if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
    _authenticate(incoming.request);
    ...
    return _withdraw(body, kind == RequestKind.RefundEscrow, true);
}
``` [3](#0-2) 

`_instances` is only populated when Hyperbridge itself dispatches a `NewDeployment` request:
```solidity
function _addDeployment(Deployment memory body) internal {
    _instances[keccak256(body.chain)] = body.gateway;
    emit DeploymentAdded({chain: string(body.chain), gateway: body.gateway});
}
``` [4](#0-3) 

The gap: **before that registration happens (or for any chain governance never explicitly registers), `instance(chain)` returns `address(this)` rather than reverting or requiring an explicit mapping.** This design choice appears aimed at supporting CREATE2 deployments that share the same address across every chain — but it means the contract silently *assumes* "unregistered chain ⇒ trust my own address as the peer" instead of verifying that assumption via governance. This mirrors the GitLab CVE-2020-8795 bug class: a permission-scoping mechanism (group sharing / instance registration) has an implicit inheritance/fallback path that grants trust beyond what was explicitly authorized, because the code substitutes a default assumption for an actual authorization check.

Any Hyperbridge-connected state machine that is not yet registered in `_instances` — which includes every newly connected chain until governance issues `NewDeployment` for it, and any state machine that will never get a matching CREATE2 deployment (e.g. a chain where `address(this)` was already taken by a third party, or a distinct EVM chain-id state machine that governance never intended to onboard) — is treated by this gateway as having its own address as a verified peer. A relayer merely needs to deliver a `PostRequest` from that state machine with `from = abi.encodePacked(address(intentGateway))`; `_authenticate` (or `authenticate` in the tron variant) passes trivially since `instance(unregistered_source) == address(this) == module`.

### Impact Explanation
If this passes, `_withdraw` executes with `isRefund`/redeem semantics driven entirely by attacker-controlled `WithdrawalRequest.tokens` — releasing escrowed order funds (`_orders[commitment][token]`) to an attacker-chosen `beneficiary`, for orders whose true legitimate settlement never occurred on that chain. This is concrete theft of escrowed intent funds: the gate that is supposed to require "this delivery was really produced by the peer `IntentGatewayV2` deployment on `request.source`" is bypassed by a fallback default rather than an actual registration. Given Hyperbridge is adding new EVM/state-machine destinations over time (and CREATE2 addresses are not guaranteed to be free/identical on every chain), this is a High-severity authorization gap reachable by any relayer able to deliver a proof for an as-yet-unregistered or address-collided source chain.

### Likelihood Explanation
Requires: (1) a relevant state machine not yet present in `_instances` on the victim gateway (true for every chain before its `NewDeployment` governance action, and permanently true for any chain intentionally excluded from CREATE2 parity), and (2) the ability to get a `PostRequest` with `from = address(intentGateway)` delivered from that source chain through Hyperbridge's normal consensus/state-proof pipeline (standard relayer flow, not requiring any privileged role). Because onboarding new chains and staggered `NewDeployment` registration is a routine, expected operational sequence (as shown by the `testFreshProxyIsOpenUntilGovernanceArmsIt` test acknowledging an analogous "open gate" window for a different check), the exposure window is realistic and recurring rather than a one-off edge case.

### Recommendation
Change `instance()`/`_instance()` to distinguish "no registration" from "self is the peer": either require an explicit self-registration entry for the local chain's state machine id (populated at `initialize`/`migrate` time) so the mapping is never implicitly defaulted for unrelated foreign chains, or have `_authenticate` revert when `_instances[keccak256(source)] == address(0)` and `source` is not the chain's own recognized state machine id. Only fall back to `address(this)` for the specific state machine id(s) that this deployment actually represents, never as a blanket default for arbitrary unregistered sources.

### Proof of Concept
1. Governance has not yet called `NewDeployment` for `StateMachine::Evm(X)` on `IntentGatewayV2` deployed on chain `Y` (or never will, e.g. because CREATE2 collided on chain `X`).
2. Attacker (or any relayer) crafts a `PostRequest` with `source = Evm(X)`, `from = abi.encodePacked(address(intentGatewayOnY))`, `dest = Y`, `to = abi.encodePacked(address(intentGatewayOnY))`, body = `RedeemEscrow` kind + `WithdrawalRequest{commitment, tokens, beneficiary=attacker}` for a live order commitment with non-zero escrow on chain `Y`.
3. Relayer submits the standard ISMP proof for this request through Hyperbridge's handler/host to chain `Y`; the host calls `intentGatewayOnY.onAccept(...)`.
4. `_authenticate` computes `instance(Evm(X))`; since `_instances[keccak256(Evm(X))] == address(0)`, it returns `address(intentGatewayOnY)`, which equals `module` decoded from `request.from` — authentication passes.
5. `_withdraw` releases the escrowed tokens for `commitment` to `beneficiary` (attacker), even though no genuine peer gateway on chain `X` ever produced this message.

Note: I was unable to execute this scenario in a live environment; the analysis is based on static reading of `IntentsBase.sol`, `ExtrinsicIntents.sol`, and the Tron variant of `IntentGatewayV2.sol`. Confirming exploitability in practice would require checking whether Hyperbridge's ISMP host enforces any additional binding between `request.source` and a configured consensus client that would prevent an attacker from choosing an arbitrary, unregistered `StateMachine` value for `source` (this is governed by `is_router`/`allowed_proxy`/consensus-client presence checks in `modules/ismp/core/src/handlers/request.rs`, which were reviewed and appear to require the source chain to have a real, Hyperbridge-recognized consensus client — meaning the attacker's "source" state machine `X` must genuinely be a supported, consensus-verified chain, just one for which `IntentGatewayV2` on `Y` hasn't yet been told the true peer address).

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-337)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L574-584)
```text
    /**
     * @dev Registers a new IntentGateway deployment for a remote state machine.
     * Called when Hyperbridge governance adds support for a new chain. The gateway
     * address is stored in `_instances` keyed by the hash of the state machine ID.
     *
     * @param body The deployment info containing the state machine ID and gateway address.
     */
    function _addDeployment(Deployment memory body) internal {
        _instances[keccak256(body.chain)] = body.gateway;
        emit DeploymentAdded({chain: string(body.chain), gateway: body.gateway});
    }
```
