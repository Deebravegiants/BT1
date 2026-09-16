## Analysis Result

I found a concrete analog: the Tron `IntentGatewayV2.sol`'s `instance()`/`authenticate()` pair defaults an unregistered remote chain's trusted sender to `address(this)` (the local gateway itself), which is the exact "unset key defaults to a value that becomes exploitable" bug class described in the referral report — a mapping that is `address(0)` by default is read through a fallback that resolves to something meaningful/attacker-reachable instead of reverting.

### Title
Unregistered-chain fallback in `instance()` lets a forged `RedeemEscrow`/`RefundEscrow` request from any un-deployed source state machine authenticate as the local `IntentGatewayV2` itself, draining escrow — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
`IntentGatewayV2.instance(stateMachineId)` returns `_instances[keccak256(stateMachineId)]`, but falls back to `address(this)` when no deployment has been registered for that state machine [1](#0-0) . `authenticate()` then requires only that the incoming request's `from` field equal `instance(request.source)` [2](#0-1) . Because the default is the gateway's own address rather than "no valid sender," any ISMP `PostRequest` whose `source` is a state machine that has never had a `NewDeployment` registered on this chain, and whose `from` bytes are set to this gateway's own address, passes authentication for `RedeemEscrow`/`RefundEscrow` in `onAccept` [3](#0-2) .

### Finding Description
`_instances` is populated only via the privileged `NewDeployment`/`_addDeployment` path, driven by Hyperbridge governance [4](#0-3) , and is `address(0)` for every state machine that hasn't yet had a gateway deployed there. Rather than treating that as "unknown/untrusted," `instance()` substitutes `address(this)`:
```
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}
```
`authenticate()` compares this value against `request.from`:
```
function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    if (instance(request.source) != module) revert Unauthorized();
}
```
This mirrors the referral bug exactly: a "default/unset" identity (`address(0)`) is resolved through a getter into a *meaningful, attacker-satisfiable* value (the local contract's own address) instead of being rejected. Any party able to get a `PostRequest` dispatched from a source state machine that the ISMP host/consensus module considers legitimate (any chain whose consensus client hyperbridge already verifies, but for which this Tron gateway has simply not yet had a remote deployment registered — the default state for most supported chains until governance explicitly adds them) can construct `from = abi.encodePacked(address(thisGateway))`. The `onAccept` handler for `RedeemEscrow`/`RefundEscrow` only calls `authenticate(request)` before decoding and executing the withdrawal [3](#0-2) , so the forged request is accepted and `withdraw()` releases escrowed tokens to an attacker-chosen beneficiary.

### Impact Explanation
This is a direct fund-theft / forged-message-delivery vulnerability reachable via a single relayed ISMP request: `withdraw()` transfers escrowed ERC-20/native tokens out of `_orders[commitment][token]` to whatever beneficiary the forged `WithdrawalRequest` specifies [5](#0-4) . Since the check that should assert "this request really came from the genuine remote gateway on `request.source`" degrades to "this request came from *something* whose `from` equals my own address" whenever no deployment is registered for that source, an attacker can redeem or refund any outstanding escrowed order on this Tron gateway from any state machine lacking a registered `_instances` entry — a permanent, unauthorized drain of escrowed user/solver funds.

### Likelihood Explanation
High for chains where deployment registration hasn't (yet) been completed for every state machine hyperbridge's consensus modules recognize — which is the normal operational state during rollout, since `_addDeployment`/`NewDeployment` is applied incrementally by governance per chain. Any attacker who can dispatch (or induce delivery of) a `PostRequest` from such an un-deployed-but-consensus-known source, with `from` crafted to equal the target Tron gateway's address, triggers the bug with no privileged access required — it is reachable by any relayer/dispatcher submitting a proof for that source chain.

### Recommendation
Never let `instance()` return `address(this)` (or any other non-zero sentinel) for an unregistered state machine. `instance()`/`authenticate()` should revert (e.g., `UnknownInstance`) when `_instances[keccak256(stateMachineId)] == address(0)`, exactly as the sibling `evm/src/apps/intentsv2/IntentsBase.sol::_instance` already does [6](#0-5) . Reserve the "fallback to self" convenience, if desired, strictly for outbound `to`/key-derivation on the *same* chain the order was placed on, never for authenticating inbound sender identity.

### Proof of Concept
1. Identify a state machine `S` that hyperbridge's consensus client on the Tron host already tracks (any registered light client), but for which `_instances[keccak256(S)]` has never been set on the target `IntentGatewayV2` contract (default `address(0)`, the normal pre-deployment state).
2. Craft/relay a `PostRequest` with `source = S`, `to = address(targetIntentGatewayV2)`, `from = abi.encodePacked(address(targetIntentGatewayV2))` (the gateway's own address), and `body = abi.encodePacked(uint8(RequestKind.RedeemEscrow), abi.encode(WithdrawalRequest({commitment: <existing order commitment>, tokens: <escrowed tokens>, beneficiary: <attacker>})))`.
3. Have this proven and delivered through the normal ISMP handler pipeline for source `S` (a legitimate, hyperbridge-verified proof of dispatch on `S`, which the attacker can produce since `S`'s consensus is genuinely verified — only the *sender identity on S* is unauthenticated here).
4. `onAccept` computes `kind = RedeemEscrow`, calls `authenticate(request)`; `instance(S)` returns `address(this)` since `_instances[keccak256(S)] == 0`; `module = address(bytes20(from)) == address(this)`; check passes.
5. `withdraw()` executes, transferring the escrowed tokens for `commitment` to the attacker-controlled beneficiary — theft of escrowed funds without ever having a genuine deployment on `S`.

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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
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
