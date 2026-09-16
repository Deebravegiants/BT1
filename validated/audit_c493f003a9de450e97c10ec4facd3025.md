### Title
Unregistered-chain fallback in `IntentGatewayV2.instance()` lets attacker forge cross-chain authentication and drain escrow - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
`instance(bytes stateMachineId)` returns `address(this)` whenever no peer gateway has been explicitly registered for that source chain, instead of treating "unregistered" as "untrusted". This is the same bug class as CVE-2018-20685: a sentinel/default value (`address(0)` / unregistered chain, analogous to `scp`'s `.`/empty filename) is silently reinterpreted as a privileged target ("self") rather than being rejected, letting a message crafted on any chain with valid consensus support — but no explicit `_instances` registration — pass the `authenticate()` check that gates fund-releasing `onAccept` logic. [1](#0-0) 

### Finding Description
`instance()` is used to resolve the trusted peer-gateway address for a given source `StateMachine`: [2](#0-1) 

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

`_instances[keccak256(stateMachineId)]` defaults to `address(0)` for every `StateMachine` the gateway operator has not explicitly registered via the `NewDeployment`/registration path. The `instance()` accessor treats that default (unset) value as equivalent to "the address of this very contract on the counterparty chain," rather than as "unknown/untrusted source." `authenticate()` then accepts any `PostRequest` whose attacker-controlled `request.from` bytes equal `address(this)` (the destination contract's own address encoded as 20 bytes), for *any* `request.source` that has a valid Hyperbridge consensus client but no explicit gateway registration.

`request.from` is set by whatever dispatched the message on the *source* chain and is not tied to `msg.sender` by any cross-chain enforced binding known to this contract — the only gate is this `authenticate()` check. Because Hyperbridge supports many EVM/Substrate/L2 state machines via generic consensus clients (BEEFY, SP1, sync-committee, GRANDPA, BSC, Tendermint, Pharos, L2 clients) independent of whether a specific app (IntentGatewayV2) has registered a peer instance there, an attacker can:
1. Pick (or deploy on) any state machine that Hyperbridge already verifies consensus for, but for which this `IntentGatewayV2` deployment has never called its registration path (`_instances[...]` is still zero).
2. Dispatch a `PostRequest` from that chain with `from = abi.encodePacked(address(thisIntentGatewayV2))` and a `RequestKind` body (e.g. `RedeemEscrow`/withdrawal) targeting a real, previously escrowed order commitment on the destination chain.
3. Relay the message with a valid membership proof for that (unregistered but consensus-verified) source chain.
4. `authenticate()` computes `instance(request.source) == address(this)` (fallback branch) `== module` (attacker's forged `from`), passes, and the withdrawal logic in `IntentsBase._withdraw` releases escrowed funds to an attacker-chosen `beneficiary`.

This mirrors the CVE precisely: a special/default value (`.`/empty filename ↔ unset `_instances` entry / `address(0)`) is silently treated as referring to a privileged object (the current directory/permission target ↔ "this contract, i.e., myself") instead of being rejected, bypassing the intended access restriction (only writable by the owning process ↔ only acceptable from a registered peer instance).

### Impact Explanation
This allows unauthorized forged message delivery that the `authenticate()` gate is specifically meant to prevent ("IntentGateway only accepts incoming assets from itself or known instances"). A successful forgery lets an attacker trigger `_withdraw` to release escrowed order funds (input/output tokens and accumulated fees) to an address of their choosing — concrete theft of escrowed funds, satisfying the required "concrete theft ... or unauthorized app action" bar.

### Likelihood Explanation
Reachable from a single relayed cross-chain message (an unprivileged relayer/message dispatcher action) with a valid state/consensus proof for any consensus-supported-but-unregistered source chain — no privileged role, governance, or admin action is required on the attacker's part. The only requirement is that the operator has not (yet) called the registration function for that particular `StateMachine`, which is the default/initial state for every chain before an explicit `NewDeployment`/instance registration — a very plausible operational window (new chain support added to consensus before the app-level peer registration, or chains intentionally left unregistered).

### Recommendation
Change `instance()` to distinguish "unregistered" from "self": either (a) return a dedicated sentinel/`address(0)` for unregistered chains and have `authenticate()` explicitly reject when `instance(source) == address(0)`, or (b) only allow the "self" fallback when `request.source == host()`'s own state machine (i.e., same-chain loopback), never for an arbitrary unregistered remote chain. Do not conflate "no entry" with "trust this request as if it came from myself."

### Proof of Concept
1. Deploy `IntentGatewayV2` on chain `D`; never call the registration path for state machine `S` (Hyperbridge already has a working consensus client for `S`, so `S` proofs verify, but `_instances[keccak256(S)] == address(0)`).
2. On `S`, dispatch (via that chain's `IDispatcher`) a `PostRequest` with `from = abi.encodePacked(address(intentGatewayV2_on_D))`, `to = abi.encodePacked(intentGatewayV2_on_D)`, and a body encoding `RequestKind.RedeemEscrow` (or equivalent withdrawal) referencing a real order `commitment` with escrowed tokens on `D`, `beneficiary = attacker`.
3. Relay the message to `D` with a valid membership proof for `S` at the proven height.
4. On delivery, `authenticate()` computes `instance(S) == address(this) == module` → passes; `_withdraw` sends the escrowed tokens to `attacker`. [3](#0-2)

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
