### Title
Broken authorization in the Tron IntentGatewayV2's `instance()` fallback lets an attacker forge cross-chain escrow-release messages - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Tron variant of `IntentGatewayV2` resolves the peer gateway address for an incoming `PostRequest.source` with a fallback that defaults to `address(this)` when no explicit deployment has been registered for that state machine, instead of reverting. Because `authenticate()` uses this same `instance()` lookup to validate the sender of `RedeemEscrow`/`RefundEscrow` messages, any unregistered (or attacker-controlled) source chain whose message carries `from == address(this)` (the gateway's own, deterministically-identical address) passes authentication, allowing forged escrow-release/refund messages.

### Finding Description
`instance()` in the Tron contract is:
```solidity
function instance(bytes calldata stateMachineId) public view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    return gateway == address(0) ? address(this) : gateway;
}
``` [1](#0-0) 

This is used directly by `authenticate()`, which is the sole gate for `RedeemEscrow`/`RefundEscrow` delivery:
```solidity
function authenticate(PostRequest calldata request) internal view {
    if (request.from.length != 20) revert InvalidInput();
    address module = address(bytes20(request.from));
    // IntentGateway only accepts incoming assets from itself or known instances
    if (instance(request.source) != module) revert Unauthorized();
}
``` [2](#0-1) 

`onAccept` calls `authenticate(incoming.request)` before decoding and honoring `WithdrawalRequest` bodies for `RedeemEscrow`/`RefundEscrow`: [3](#0-2) 

Compare this to the canonical EVM implementation (`evm/src/apps/intentsv2/IntentsBase.sol`), where the equivalent helper **reverts** for unregistered chains instead of defaulting to `address(this)`:
```solidity
function _instance(bytes calldata stateMachineId) internal view returns (address) {
    address gateway = _instances[keccak256(stateMachineId)];
    if (gateway == address(0)) revert UnknownInstance();
    return gateway;
}
``` [4](#0-3) 

Because the gateway is deployed at a deterministic CREATE2 address that is identical across every chain by design (documented explicitly elsewhere in the codebase to preserve cross-chain address parity, e.g. `evm/src/apps/IntentGatewayV2.sol` comments about "atomic CREATE2 deployment already binds the init data to the canonical address"), an attacker does not need to guess an address: `address(this)` on the victim chain is a fixed, publicly known constant. The root cause is that the authorization check (`instance(source) == from`) is keyed only on a state-machine identifier the caller effectively controls the trust boundary of (any not-yet-registered/whitelisted `source`), with a fail-open default, rather than being tied to an explicit, governance-registered peer for every accepted `source`.

This mirrors the reported bug class exactly: the authorization decision is derived from an unauthenticated/attacker-influenceable identifier (here, an unregistered `source` state machine plus a `from` address the attacker can match to the known constant) rather than being validated against an actual registered relationship, letting an unauthorized party impersonate a trusted peer and act on behalf of the real protocol.

### Impact Explanation
An attacker who can get a `PostRequest` delivered to the Tron `IntentGatewayV2.onAccept` (i.e., dispatched from any ISMP-connected state machine that has **not** been explicitly registered as a peer gateway, with `request.from` set to 20 bytes equal to the gateway's own deterministic address) can forge `RedeemEscrow` or `RefundEscrow` messages. `_withdraw()` reachable from `authenticate()` releases escrowed input tokens (and any accumulated protocol/solver fees) to an attacker-chosen `beneficiary` for any known/guessable order `commitment`, resulting in direct theft of escrowed user funds — a Critical, unbacked/forged message delivery vulnerability at the message-authorization boundary of the intents system.

### Likelihood Explanation
Exploitability depends on whether the relayer/ISMP pipeline will actually deliver a `PostRequest` whose `source` is an unregistered-but-real connected state machine (this still requires a valid consensus/state proof for that source chain, which is why this is scoped to the message-authorization logic rather than a bypass of proof verification). Given that: (1) the deterministic-address design is intentional and documented, (2) any of Hyperbridge's numerous connected/supportable EVM chains could serve as an "unregistered" source relative to a given Tron deployment, and (3) the fallback silently defaults to trusting `address(this)` rather than failing closed, the likelihood of exploitation is high once any chain exists that is ISMP-connected but not yet in this gateway's `_instances` map — a state that is normal during incremental peer rollout.

### Recommendation
Change `instance()` (or `authenticate()`) in `evm/tron/contracts/apps/IntentGatewayV2.sol` to fail closed for unregistered state machines, matching `evm/src/apps/intentsv2/IntentsBase.sol::_instance`: revert with an `UnknownInstance`-style error when `_instances[keccak256(stateMachineId)] == address(0)`, rather than falling back to `address(this)`. Audit any other callers of the Tron `instance()` function that may rely on the current fallback behavior, and add a regression test asserting that `onAccept` rejects `RedeemEscrow`/`RefundEscrow` requests from any `source` not explicitly present in `_instances`, even when `from` equals the gateway's own address.

### Proof of Concept
1. Deploy (or identify) the Tron `IntentGatewayV2` at its canonical deterministic address `G` on the target Tron chain; do not register a peer deployment for state machine `X` (i.e., `_instances[keccak256(X)] == address(0)`).
2. From any real, ISMP-connected chain `X` that is not registered as a peer, obtain (or construct, if the attacker controls a contract at address `G` there — trivial since it's the same deterministic CREATE2 address) a valid ISMP `PostRequest` with:
   - `source = X`
   - `from = abi.encodePacked(G)` (20 bytes matching the gateway's own address)
   - `to = abi.encodePacked(G)`
   - `body = bytes1(RequestKind.RedeemEscrow) ++ abi.encode(WithdrawalRequest({commitment: <victim order commitment>, tokens: <victim's escrowed tokens>, beneficiary: <attacker>}))`
3. Have this message relayed and delivered through the real Hyperbridge host/handler with a valid consensus/state proof for chain `X` (the proof only proves message origin on `X`, not gateway registration).
4. `onAccept` calls `authenticate(request)`, which computes `instance(X)`; since `X` is unregistered, `instance()` returns `address(this) == G`, matching `from`, so authentication passes.
5. `_withdraw()` executes, transferring the victim's escrowed tokens to the attacker's `beneficiary` and marking the order filled — confirming unauthorized fund release without ever registering `X` as a legitimate peer.

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
