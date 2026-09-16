### Title
Unregistered source chain authenticates as the gateway's own address, allowing forged escrow withdrawal requests - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`IntentGatewayV2.instance()` on the Tron deployment returns `address(this)` as a fallback when a state machine ID has no registered peer deployment, instead of reverting. `authenticate()` compares this value against the `from` field of an incoming `PostRequest` to decide whether a delivered message is trusted. Because the fallback silently substitutes the gateway's own address for "no peer registered," any request whose source chain has not yet been registered via `NewDeployment` can pass authentication as long as its `from` field encodes the gateway's own address, letting an attacker forge `RedeemEscrow`/`RefundEscrow` withdrawal instructions.

### Finding Description
`instance()` is meant to resolve the trusted peer `IntentGateway` deployment for a given state machine ID, exactly analogous in purpose to the `footiumClub.ownerOf(_clubId)` check in the reported bug: it should only "exist" (return non-zero) once explicitly registered, and other logic should reject non-existent bindings rather than silently accepting a substitute value.

In `evm/src/apps/IntentGatewayV2.sol` / `IntentsBase.sol`, this is done correctly — `_instance()` reverts with `UnknownInstance` when nothing is registered: [1](#0-0) 

But the Tron variant instead falls back to `address(this)`: [2](#0-1) 

This fallback value then feeds directly into the authentication check for every incoming post request: [3](#0-2) 

`onAccept` calls `authenticate(incoming.request)` for `RedeemEscrow` and `RefundEscrow` requests before processing a `WithdrawalRequest` that releases escrowed tokens to an arbitrary `beneficiary`: [4](#0-3) 

Because the ISMP host verifies only that a `PostRequest` genuinely originated from *some* consensus-verified state machine (via `HandlerV2.handlePostRequests`), not that the state machine is a peer this specific app has registered, an attacker who controls a contract deployment on *any* state machine that Hyperbridge already trusts — one this `IntentGateway` instance has simply never called `NewDeployment` for — can dispatch a `PostRequest` whose `from` bytes encode `address(this)` (the Tron gateway's own address). `instance(request.source)` then returns `address(this)` (since no explicit registration exists), which equals `module` derived from `from`, so `authenticate()` incorrectly succeeds.

### Impact Explanation
A successful forgery lets the attacker submit a fabricated `WithdrawalRequest` (`RedeemEscrow` or `RefundEscrow`) that is authenticated as if it came from a legitimate peer gateway. `withdraw()` sends escrowed order tokens to whatever `beneficiary` the attacker encodes, and marks `_filled[commitment]`, for any commitment that still has non-zero escrowed balances in `_orders`: [5](#0-4) 

This is a direct theft of escrowed user/solver funds and an unauthorized app action — the exact bug class the rules require (forged message delivery / unauthorized app action against intents escrow), reachable by any relayed proof/dispatched request from a single unregistered source chain.

### Likelihood Explanation
Exploitability depends only on: (1) the attacker being able to dispatch a `PostRequest` from a state machine that Hyperbridge already supports consensus verification for, and (2) the `from` field of that request encoding `address(this)` (the fixed, known, on-chain address of the Tron `IntentGatewayV2`). Both are attacker-controlled since `from` is arbitrary application-layer data set by the dispatching contract, not tied to `msg.sender` identity on the source chain. No privileged role or governance compromise is required — this is reachable directly through the ordinary relayed-message delivery path (`onAccept`, `onlyHost`-gated but host-agnostic to peer registration), matching the required "single relayed proof" reachability.

### Recommendation
Make `instance()` revert (or explicitly signal "unregistered") when no deployment is registered for a state machine, mirroring `evm/src/apps/intentsv2/IntentsBase.sol`'s `UnknownInstance` revert, instead of returning `address(this)`:
```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    if (gateway == address(0)) revert UnknownInstance();
    return gateway;
}
```
Then have `authenticate()` reject any request whose source is unregistered rather than silently treating it as self-authenticating.

### Proof of Concept
1. Confirm the Tron `IntentGatewayV2` has not called `NewDeployment` to register a peer for state machine `X` (i.e., `_instances[keccak256(X)] == address(0)`).
2. From a chain corresponding to state machine `X` that Hyperbridge already has a working consensus client for, dispatch an ISMP `PostRequest` to this Tron gateway with:
   - `source = X`
   - `from = abi.encodePacked(address(tronIntentGateway))` (20 bytes, the Tron gateway's own address)
   - `body = abi.encodePacked(uint8(RequestKind.RedeemEscrow), abi.encode(WithdrawalRequest({commitment: <existing order commitment>, tokens: <that order's escrowed tokens>, beneficiary: bytes32(uint256(uint160(attacker)))})))`
3. Have this request relayed and delivered through the normal ISMP handler pipeline to `IntentGatewayV2.onAccept`.
4. `authenticate()` computes `instance(X)`, which returns `address(this)` (fallback, since `X` is unregistered) — equal to `module` decoded from `from` — so authentication passes.
5. `withdraw()` executes, transferring the escrowed order tokens to `attacker` and marking the order filled/refunded, without any legitimate peer having sent this instruction.

Note: the exact identity of a "state machine Hyperbridge already trusts but this app has not registered as a peer" was not independently confirmed with a live example in this review — it is inferred from `HandlerV2.handlePostRequests` validating only destination/timeout/consensus proof, not per-app peer registration; a Devin session with full repo/test access should confirm this against the actual `HandlerV2`/`IsmpHost` request-acceptance logic before treating this as certain.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-634)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
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
