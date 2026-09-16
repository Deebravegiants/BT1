Based on my investigation, I found a genuine authentication weakness, but I could not confirm the exploit chain end-to-end because I ran out of iterations before verifying whether `request.from` on an EVM/Tron ISMP dispatch is forced to `msg.sender` by the host dispatcher (which would make the bug unexploitable) or is attacker-suppliable metadata that only needs to match on the *destination* side (which would make it exploitable).

### Title
Loose peer-instance fallback in Tron `IntentGatewayV2.instance()` defaults unregistered source chains to `address(this)` - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` implements `instance()` and `authenticate()` differently from the canonical EVM implementation. On EVM (`evm/src/apps/intentsv2/IntentsBase.sol`), `_instance()` **reverts** with `UnknownInstance` for any state machine that has not been explicitly registered as a peer. On Tron, `instance()` instead **falls back to `address(this)`** for any unregistered `stateMachineId`.

### Finding Description [1](#0-0) 
```solidity
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
compares to the EVM implementation, which reverts instead of defaulting: [2](#0-1) 

`authenticate()` gates `RedeemEscrow`/`RefundEscrow` withdrawals, called from `onAccept`: [3](#0-2) 

Because `instance()` defaults to `address(this)` for **any** `request.source` not explicitly registered as a peer, an incoming `PostRequest` whose `source` is an unregistered/unconfigured state machine and whose `from` field equals this Tron gateway's own 20-byte address will pass `authenticate()` and be treated as coming from a legitimate peer instance — even though no such peer was ever registered by governance for that chain.

### Impact Explanation
If exploitable, this would let an attacker forge a `RedeemEscrow`/`RefundEscrow` withdrawal request purportedly from a chain the operator never configured as a peer, releasing escrowed funds (theft/unbacked withdrawal from escrow) on the Tron IntentGatewayV2 deployment. This maps to the "concrete theft ... of funds" / "forged message delivery" impact classes in scope.

### Likelihood Explanation
**I could not confirm this is exploitable and I am flagging it as uncertain rather than a confirmed finding.** The critical open question is whether `request.from` delivered to `onAccept` is attacker-controllable metadata that only needs to numerically equal the gateway's address, or whether the underlying ISMP host/dispatcher on the source chain forces `from = msg.sender` at dispatch time (which is the normal ISMP convention, and would mean an attacker would need to deploy a contract at the exact same 20-byte address as the Tron gateway on some other already-supported chain — a much harder, CREATE2-dependent precondition, or effectively infeasible for an unrelated chain). I was not able to locate and read the Tron host's `dispatch()` implementation (or confirm it exists/is in-scope with the same semantics as `evm/src/core/EvmHost.sol`) before running out of tool budget, so I cannot state definitively whether the precondition is trivially attacker-satisfiable (single dispatched transaction from any account) or requires an address-collision that is not realistically reachable.

Separately, this discrepancy could also be intentional/legacy behavior on the Tron contract (e.g., a deliberate "self-instance" fallback for a single-deployment scenario where no cross-chain peers exist yet), which would reduce or eliminate the risk. I have not found a changelog/decision doc in the repo confirming which behavior (revert vs. fallback-to-self) is the intended one for Tron specifically.

### Recommendation
Given the uncertainty, the concrete next step (for a Devin session, not this answer) would be to:
1. Confirm whether `evm/tron/contracts/apps/IntentGatewayV2.sol` is genuinely deployed/in-scope for Tron (separate from the mainline EVM contracts), and whether the Tron ISMP host forces `request.from` to the dispatching contract's own address or allows an unrelated address to be declared.
2. If `from` is attacker-influenceable and/or the address-collision precondition is realistically achievable, align `instance()` in the Tron contract with the EVM `_instance()` semantics — revert with `UnknownInstance` for unregistered chains rather than defaulting to `address(this)`.

### Proof of Concept
Not provided — I do not have sufficient verified evidence (specifically, confirmation of `from`-field control at dispatch time and confirmation that the Tron contract is in-scope/deployed) to construct a concrete, non-speculative PoC. Given the explicit instruction to avoid guesses/speculation, I'm reporting this as an **unconfirmed discrepancy** rather than a validated vulnerability, and recommend it be verified with actual filesystem/dispatcher access before treating it as an approved finding.

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
