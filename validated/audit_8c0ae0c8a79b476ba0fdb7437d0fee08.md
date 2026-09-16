## Analysis: Insecure Fallback in Tron `IntentGatewayV2.instance()` Authorization Check

I found a concrete analog. It concerns an authorization check that was properly implemented in the canonical EVM `IntentGatewayV2` but not preserved when the contract was ported to Tron — the same class of bug as the xxl-job report (a permission check silently missing/bypassable on an alternate code path, letting an attacker-controlled identifier slip through).

### Title
Insecure fallback in `instance()` lets an unregistered source chain authorize escrow withdrawal - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The canonical EVM `IntentGatewayV2` (`evm/src/apps/intentsv2/IntentsBase.sol`) enforces that a cross-chain source module must be an explicitly registered instance, reverting with `UnknownInstance` otherwise: [1](#0-0) 

The Tron port of the same contract implements `instance()` with a silent fallback instead of a revert: [2](#0-1) 

When no instance is registered for `request.source` (`_instances[keccak256(stateMachineId)] == 0`), `instance()` returns `address(this)` rather than reverting. This return value feeds directly into `authenticate()`, which is the sole gate before releasing escrowed funds in `onAccept()` for `RedeemEscrow`/`RefundEscrow`: [3](#0-2) 

### Finding Description
`authenticate()` is supposed to verify that an incoming settlement message really originated from a *known* IntentGateway instance on the claimed source chain: [4](#0-3) 

Because `instance()` degrades to `address(this)` for any state machine that has not yet had a `NewDeployment` registered (a routine, expected pre-governance state for newly supported chains, or any chain that will never get an official deployment there), the check `instance(request.source) != module` collapses to `address(this) != module`. Any ISMP module whose `from` field equals `address(this)` (the destination gateway's own address) on such an unregistered source chain therefore passes authentication, even though it is not a peer IntentGateway instance at all.

This is the same bug class as the xxl-job advisory: a permission/authorization decision that depends on an identifier-driven lookup (there, a sub-task ID; here, a state-machine-keyed instance mapping) was not consistently preserved across ported/duplicated code paths, so the check can be satisfied by an unintended value instead of a properly-registered one.

### Impact Explanation
If exploited, `withdraw()` is invoked with attacker-supplied `WithdrawalRequest.commitment`, `tokens`, and `beneficiary`, releasing another order's escrowed tokens (and fee-token balance) to an attacker-chosen address: [5](#0-4) 

This is concrete theft of escrowed user funds on the Tron IntentGateway deployment — a High severity impact matching the "theft of funds" bar in scope.

### Likelihood Explanation
Exploitability requires the attacker's module to be deployed at the same address as the destination gateway (`address(this)`) on a source chain that Hyperbridge already supports but for which the intent gateway has no registered instance yet — e.g., during the interval between a new chain's consensus-client integration and the governance `NewDeployment` call, or a chain that will only ever host non-intent apps. Given this ecosystem's common practice of deterministic (CREATE2/factory) deployment to keep gateway addresses identical across chains, an attacker able to deploy a contract on such an under-registered chain at that address (or otherwise cause `from` to encode it) can trigger the bypass without needing any admin/governance compromise, keeping this within the permissionless attacker model.

### Recommendation
Make `instance()` (or `authenticate()`) fail closed: revert (e.g., `UnknownInstance`) when no instance is registered for the given `stateMachineId`, matching the behavior of `IntentsBase._instance()` in the canonical EVM contract, instead of returning `address(this)` as a default.

### Proof of Concept
1. Identify a state machine `X` supported by Hyperbridge (has a consensus client) for which `_instances[keccak256(X)] == 0` on the Tron `IntentGatewayV2`.
2. Deploy/obtain a module on chain `X` whose address equals the Tron gateway's own address (`address(this)`), e.g., via a shared deterministic-deployment factory used across the ecosystem's chains.
3. From that module, dispatch an ISMP POST request with `source = X`, `to = <TronGatewayAddress>`, and `body = RequestKind.RedeemEscrow ++ abi.encode(WithdrawalRequest{commitment: <victim order commitment>, tokens: <victim's escrowed tokens>, beneficiary: <attacker>})`.
4. Once the message is relayed and proof-verified by the host (a purely mechanical, permissionless relay of a legitimately-sourced-but-unregistered message), `EvmHost`/handler calls `onAccept()`, which calls `authenticate()`. Since `instance(X) == address(this) == module`, authentication passes.
5. `withdraw()` executes, transferring the victim's escrowed tokens to the attacker-controlled `beneficiary`.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L287-300)
```text
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-723)
```text
    function withdraw(WithdrawalRequest memory body, bool isRefund) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        _filled[body.commitment] = beneficiary;

        // redeem escrowed tokens
        uint256 len = body.tokens.length;
        for (uint256 i; i < len;) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (_orders[body.commitment][token] == 0) revert UnknownOrder();

            if (token == address(0)) {
                (bool sent,) = beneficiary.call{value: amount}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                (bool success,) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, amount));
                if (!success) revert TransferFailed();
            }

            _orders[body.commitment][token] -= amount;
            unchecked {
                ++i;
            }
        }

        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```
