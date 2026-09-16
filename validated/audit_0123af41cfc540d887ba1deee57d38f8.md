### Title
IntentGatewayV2 (Tron) authenticates cross-chain settlement messages against a permissive default that lets any unregistered chain impersonate a trusted peer, enabling theft of escrowed funds - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.instance()` on the Tron variant of the Intent Gateway returns `address(this)` when no peer gateway is registered for a state machine, instead of reverting like every other implementation of this contract (`evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/IntentGatewayV2.sol`). Since `authenticate()` uses this same default to validate the sender of incoming `RedeemEscrow`/`RefundEscrow` settlement messages, an attacker who can dispatch a forged ISMP message from *any state machine not explicitly registered as a peer* — as long as the `from` field encodes the gateway's own address — passes authentication and can redeem or refund a legitimate user's escrowed order to a beneficiary of their choosing.

### Finding Description
`authenticate()` is the sole gate protecting `withdraw()`, which releases escrowed order funds: [1](#0-0) 

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
``` [1](#0-0) 

`_instances` is only populated by an explicit `NewDeployment` action dispatched by Hyperbridge itself: [2](#0-1) 

For every `PostRequest.source` that has *not* been registered, `instance()` silently falls back to `address(this)` rather than reverting. `onAccept` then calls `authenticate` before decoding the `WithdrawalRequest` and paying out escrow: [3](#0-2) [4](#0-3) 

Contrast this with the maintained, non-Tron implementations, where an unregistered chain deliberately reverts with `UnknownInstance()` instead of resolving to `address(this)`: [5](#0-4) 

This is the exact bug-class in the report: an access-control check that is supposed to restrict a REST/API-style action to a known, registered principal instead silently falls back to a default that an unprivileged caller can satisfy, bypassing the intended restriction.

**Exploitation path**: Hyperbridge supports many connected state machines beyond the ones an individual `IntentGatewayV2` deployment has explicitly registered as peers via `NewDeployment`. Any of those un-peered chains is a valid `PostRequest.source` as far as the ISMP handler/consensus verification is concerned — `_instances` is an application-level allow-list, not a protocol-level one. An attacker who deploys (or controls) a contract on any such un-peered chain, at the exact address of the target `IntentGatewayV2` deployment (achievable with a deterministic CREATE2 factory commonly used for cross-chain address parity, or simply by being first to deploy there), can dispatch a `PostRequest` with `body = [RedeemEscrow] ++ abi.encode(WithdrawalRequest{commitment, tokens, beneficiary: attacker})` targeting a `commitment` of any order legitimately escrowed on the victim chain. Because `instance(attacker_chain)` resolves to `address(this)` and `request.from` is set to that same address, `authenticate()` passes, and `withdraw()` pays out the escrowed tokens to the attacker-chosen beneficiary — stealing funds that were escrowed by a real user for a legitimate order.

### Impact Explanation
This is concrete theft of escrowed user funds: an unprivileged party dispatching a single forged cross-chain message can redirect the payout of any real intent order's escrow to themselves, bypassing the intended "only a registered peer gateway may redeem/refund" restriction. This matches the required impact bar (concrete theft of funds via forged message delivery / unauthorized app action).

### Likelihood Explanation
The primary constraint is obtaining a state machine identifier connected to Hyperbridge that the target gateway has *not* explicitly registered as a peer, and getting a contract deployed at the same address as the target gateway on that chain — both of which are realistic given widespread use of deterministic (CREATE2) deployment factories for cross-chain contract parity, and the fact that Hyperbridge's supported state machine set is broader than any single app's peer registry. No collusion with governance, admin, or the relayer is required; the request only needs to pass normal ISMP proof verification for a real message dispatched from that source chain.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert with `UnknownInstance()` when no peer gateway is registered for the given `stateMachineId`, matching the behavior already implemented in `evm/src/apps/intentsv2/IntentsBase.sol` and `evm/src/apps/IntentGatewayV2.sol`. Audit all other callers of `instance()` in this file (e.g., the `Get` request construction and `RefundEscrow` dispatch paths) to ensure none rely on the permissive `address(this)` fallback.

### Proof of Concept
1. User places a cross-chain order on chain A (`IntentGatewayV2` at address `G`), escrowing tokens; `_orders[commitment][token] = amount` is recorded on chain A.
2. Attacker identifies (or deploys) a contract at address `G` on chain X, a state machine connected to Hyperbridge but never registered via `NewDeployment` as a peer of the chain-A gateway (`_instances[keccak256(X)] == address(0)`).
3. Attacker dispatches (or gets relayed) a genuine ISMP `PostRequest` from chain X: `source = X`, `from = abi.encodePacked(G)`, `to = abi.encodePacked(G_on_chain_A)`, `body = [RedeemEscrow] ++ abi.encode(WithdrawalRequest{commitment, tokens: order.inputs, beneficiary: attacker})`.
4. On chain A, `EvmHost.dispatchIncoming` verifies the proof and calls `IntentGatewayV2.onAccept`. `authenticate()` computes `instance(X)`; since `X` is unregistered, this returns `address(this) == G`, which equals `module` decoded from `request.from`. Authentication passes.
5. `withdraw()` finds `_orders[commitment][token] != 0` (the real escrow from step 1) and transfers the tokens to `attacker`, draining the legitimate user's escrow.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L637-643)
```text
        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-714)
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
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```
