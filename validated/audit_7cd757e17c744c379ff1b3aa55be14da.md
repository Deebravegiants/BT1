Based on my investigation, the production `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`) uses `IntentsBase._instance`, which reverts with `UnknownInstance` when a gateway is unregistered for a given state machine [1](#0-0) . This is the safe pattern and is not vulnerable to the analog.

However, the Tron-specific `IntentGatewayV2.sol` (`evm/tron/contracts/apps/IntentGatewayV2.sol`) implements a different `instance()` function that silently falls back to `address(this)` when no gateway is registered for a `stateMachineId`, instead of reverting:

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
``` [2](#0-1) 

This mirrors the reported bug class: an unset/default trust value (in the original report, `trustedRemoteConnext[_origin] == address(0)`, matched by a spoofable zero sender) is treated as a valid credential instead of being rejected. Here, an unregistered `stateMachineId` maps to `address(this)` — a value an attacker could match by deploying a contract at the identical address on any chain not yet registered as a peer (e.g., via a deterministic CREATE2 factory with the same salt/bytecode, a well-known technique for reproducing addresses cross-chain). I was not able to fully verify from the index whether `_instance`/`authenticate` in the Tron variant is reachable from an actual `onAccept`/`onGetResponse` override (the file I read only goes to line 330 and doesn't show the full override), so I could not fully confirm end-to-end exploitability (e.g., whether cross-chain deposits/withdrawals are actually gated by this exact `authenticate()` call, or what funds it protects). This uncertainty should be resolved with a full read of `evm/tron/contracts/apps/IntentGatewayV2.sol` beyond line 330, which the index did not return.

Given the strong structural analogy but incomplete confirmation of full exploit reachability and impact within the index's coverage, I can report this as a plausible but not fully-confirmed finding.

### Title
Unregistered-instance fallback in Tron `IntentGatewayV2.authenticate` accepts forged cross-chain messages from any chain claiming to be the contract itself - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
`IntentGatewayV2.instance()` in the Tron variant of the IntentGateway falls back to `address(this)` when no gateway address is registered for a given `stateMachineId`, rather than reverting. `authenticate()` uses this value to validate `request.from`, so any message purportedly originating from an unregistered chain, where `request.from` equals the local contract's own address, passes authentication.

### Finding Description
`instance()` returns `address(this)` whenever `_instances[keccak256(stateMachineId)]` is unset (zero) [3](#0-2) . `authenticate()` then compares this fallback value against `module`, the address decoded from the incoming `PostRequest.from` field [4](#0-3) . This is structurally identical to the reported `XProvider.onlySource` bug: an "unset" trust anchor (there, `trustedRemoteConnext[_origin] == address(0)`; here, `_instances[keccak256(stateMachineId)] == address(0)`) resolves to a specific, guessable/forgeable value (there, the zero address matched via Connext's fast-path default; here, `address(this)`, matched by deploying an identically-addressed contract on an unregistered chain via deterministic CREATE2). The production EVM `IntentGatewayV2` avoids this by reverting with `UnknownInstance` on an unregistered peer via `IntentsBase._instance` [1](#0-0) , but the Tron-specific contract diverges from this safe pattern.

### Impact Explanation
If reachable from `onAccept`/`onGetResponse`, this would let an attacker deploy a contract at the same address as the Tron `IntentGatewayV2` on any chain not yet registered as a peer, then dispatch a forged `PostRequest` (with `request.source` set to that unregistered chain and `request.from` set to that matching address) that `authenticate()` incorrectly accepts as coming from a trusted peer instance. Depending on which functions gate on `authenticate()` (e.g. `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust` per the `RequestKind` enum [5](#0-4) ), this could allow unauthorized escrow redemption/refund, unauthorized parameter updates, or unauthorized dust sweeps — a route to theft or state corruption of the Tron intents gateway.

### Likelihood Explanation
Exploitability depends on (a) confirming `authenticate()` is actually invoked from a reachable `onAccept`/`onGetResponse` override for cross-chain requests in this file, and (b) an attacker's ability to get a consensus-verified request accepted with an arbitrary `request.source` not already registered as a peer. I could not fully verify (a) from the available index (the file content beyond line 330 was not returned), so likelihood cannot be confirmed as high with full confidence; this needs direct code inspection to close.

### Recommendation
Change `instance()` in `evm/tron/contracts/apps/IntentGatewayV2.sol` to revert (e.g., with an `UnknownInstance` error) when `_instances[keccak256(stateMachineId)]` is unset, matching the pattern already used in `IntentsBase._instance` for the production EVM gateway, instead of silently falling back to `address(this)`.

### Proof of Concept
1. Attacker identifies that `_instances[keccak256(stateMachineIdX)]` is unset on the Tron `IntentGatewayV2` for some `stateMachineIdX` not yet registered as a peer.
2. Attacker deploys a contract at the same address as the Tron `IntentGatewayV2` on a chain corresponding to `stateMachineIdX` (or otherwise produces a valid, consensus-verified request whose `from` field is `abi.encodePacked(address(this))` for the target Tron gateway) and dispatches a `PostRequest` with `source = stateMachineIdX`, `from = abi.encodePacked(<intentGatewayAddress>)`.
3. On delivery, `authenticate()` calls `instance(stateMachineIdX)`, which returns `address(this)` (the fallback) since no peer is registered, matching `module` decoded from `request.from`, and authentication incorrectly succeeds [4](#0-3) .

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L63-77)
```text
    /**
     * @dev Enum representing the different kinds of incoming requests that can be executed.
     */
    enum RequestKind {
        /// @dev Identifies a request for redeeming an escrow.
        RedeemEscrow,
        /// @dev Identifies a request for recording new contract deployments
        NewDeployment,
        /// @dev Identifies a request for updating parameters.
        UpdateParams,
        /// @dev Identifies a request for sweeping accumulated dust
        SweepDust,
        /// @dev Identifies a request for refunding an escrow (cancellation from destination chain)
        RefundEscrow
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
