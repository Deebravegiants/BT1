## Title
Governance rotation of an IntentGateway remote deployment (`NewDeployment`) permanently strands in-flight escrow settlement and cancellation messages - (`evm/src/apps/intentsv2/IntentsBase.sol`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol`)

### Summary
The Union Finance finding is a class of bug where an external registry mapping (`uTokens[token]`) is upgraded to point at a new address, while code elsewhere continues to authorize/authenticate actions based on a stale assumption tied to the *current* registry value, causing balances/authorization checks to run against the wrong party and lock or misdirect funds. `IntentGatewayV2`'s cross-chain settlement path has the same structural weakness: the `_instances[keccak256(stateMachineId)]` registry (updated via the privileged `NewDeployment` request) is re-read at *delivery time* rather than being pinned to the deployment that was live when the order was placed/filled. Any escrow-settlement or cancellation message already in flight when the registry entry changes will be rejected or misrouted against a peer that no longer matches the message's origin/target, freezing escrowed funds.

### Finding Description
`IntentsBase._instance()` resolves the trusted peer gateway address for a state machine from `_instances[keccak256(stateMachineId)]`: [1](#0-0) 

This mapping is mutated only through the `NewDeployment` request kind, gated to Hyperbridge governance: [2](#0-1) 

`ExtrinsicIntents._authenticate()` re-derives the "known instance" for an incoming `RedeemEscrow`/`RefundEscrow` message strictly from the *current* value of `_instances`, not the value that was in effect when the counterpart message was originally dispatched: [3](#0-2) 

The same current-value dependency exists in `_cancelFromSource`, which builds the GET storage-proof key against `_instance(order.destination)` at cancellation time, and in `_post`/`_fillCrossChain`, which dispatch the settlement `RedeemEscrow` message `to` whatever `_instance(order.source)` currently resolves to: [4](#0-3) [5](#0-4) 

Concretely:
1. A user places a cross-chain order on chain A, escrowing input tokens. `order.destination` records chain B; at fill time chain B's peer gateway for chain A is whatever `_instances[keccak256(A)]` currently is on chain B, and chain A's peer gateway for chain B is whatever `_instances[keccak256(B)]` currently is on chain A.
2. A solver fills the order on chain B (`_fillCrossChain`), delivering output tokens to the beneficiary and dispatching a `RedeemEscrow` post request back to chain A's currently-registered gateway address (`_instance(order.source)` as known on chain B at fill time).
3. Before this message is relayed and delivered, governance rotates the IntentGateway deployment address for chain B (a legitimate operational event — e.g. migrating to a new proxy/implementation address) via `NewDeployment`, overwriting `_instances[keccak256(B)]` on chain A.
4. When the `RedeemEscrow` message finally arrives on chain A, `onAccept` calls `_authenticate`, which compares the message's `request.from` (the *old* chain-B gateway address that actually dispatched it) against `_instance(request.source)` (now the *new* chain-B gateway address). These no longer match, so the message reverts with `Unauthorized`.
5. The solver, who already paid the beneficiary the output tokens on chain B, can never redeem the escrowed input tokens on chain A through the normal `onAccept` path — the message is permanently unauthenticatable since `request.from` is baked into the already-signed/dispatched ISMP message and cannot be changed. The escrow sits in `_orders[commitment][token]` on chain A indefinitely.
6. The user-initiated fallback (`cancelOrder` → `_cancelFromSource`) is equally broken: after the deadline, it dispatches a GET request whose key is built from `_instance(order.destination)` — the *current* (rotated) chain-B address — reading a storage slot at the *new* gateway contract, not the one that actually processed the fill and holds the true `_filled` value. This returns "unfilled" (empty storage at the new, unrelated contract), and `onGetResponse` on chain A will refund the user's escrow even though the order was already filled and the solver already paid out on chain B — a double-spend/fund-loss risk on the settlement side (the solver's already-delivered output tokens are not recoverable, while the escrowed input funds are also refunded to the user).

This is the direct analog of the Union report: `uTokens[token]` upgrade → old uToken silently demoted to "normal user" for `_checkSenderBalance` → funds locked/stolen. Here: `_instances[chain]` upgrade → in-flight messages from the old gateway silently rejected/misrouted for `_authenticate`/GET-proof addressing → escrow permanently locked, and/or refunded twice via mismatched proof target.

### Impact Explanation
This breaks fund-safety guarantees for the Intent Gateway's cross-chain escrow settlement flow, an unprivileged, user/solver-reachable path (placing orders, filling orders, cancelling orders are all permissionless actions). A routine, non-malicious governance action (rotating a deployment address, e.g. after a contract migration) can:
- Permanently freeze escrowed user funds on the source chain because the legitimate `RedeemEscrow`/`RefundEscrow` message can never pass `_authenticate` again (the `request.from` in an already-dispatched ISMP message is immutable).
- Cause the source-chain cancellation path to read the `_filled` storage slot of the *wrong* (new) contract, incorrectly reporting an order as unfilled and refunding escrow to the user for an order that was already filled and paid out by a solver on the destination chain — a direct loss of solver funds and/or a double payout.

This satisfies "permanent freezing of funds" and "unsound/forged message delivery/authorization" criteria for a valid finding.

### Likelihood Explanation
Deployment-address rotations are an expected, routine governance operation (contract migrations, redeployments, fixing a compromised/buggy gateway) rather than a rare edge case, and the codebase already provides the `NewDeployment` request specifically to support this. Any cross-chain order that is filled or in cancellation while such a rotation is pending naturally hits this race — no attacker action is required, only ordinary operational timing between message dispatch, relaying, and a parameter update. The larger a chain's order volume and the more the deployment address is expected to change over time (upgrades, migrations, disaster recovery), the more certain this occurs.

### Recommendation
- Do not silently overwrite `_instances[chain]` on `NewDeployment`. Instead, maintain a set (or history) of previously-valid gateway addresses per chain, and accept `_authenticate`/authorize against any address that was valid at the time the counterpart message could have been dispatched (e.g., keep old entries valid for at least the maximum in-flight message lifetime/timeout window before removal).
- Alternatively, pin the peer gateway address used for a given order's settlement/cancellation at `placeOrder`/`fillOrder` time (store it as part of order state) so that `_authenticate` and the GET storage-proof key always target the address that was actually used to dispatch/fill that specific order, independent of later `NewDeployment` updates.
- For the cancellation GET-proof path in particular, build the storage-proof key from the address recorded at fill time (or an allow-listed historical address), not from the live `_instances` mapping, to prevent the proof from being read against an unrelated contract.
- Add an explicit migration procedure that requires draining/settling all in-flight orders for a state machine before rotating its gateway address, or provide a dedicated migration message type that atomically informs both ends and preserves authorization for pending in-flight settlements.

### Proof of Concept
Conceptual reproduction (matches existing test scaffolding in `evm/tests/foundry/IntentGatewayV2Test.sol`, which already exercises `NewDeployment`/`instance()` and the `RedeemEscrow` `onAccept` flow):
1. Register `_instances[keccak256("CHAIN_B")] = gatewayB_v1` on chain A via `NewDeployment` (see `testOnAcceptNewDeployment`, `evm/tests/foundry/IntentGatewayV2Test.sol:2746-2784`).
2. User places a cross-chain order on chain A with `destination = "CHAIN_B"`, escrowing USDC.
3. Solver fills the order on chain B via `_fillCrossChain`, which dispatches a `RedeemEscrow` post request with `from = gatewayB_v1` to chain A.
4. Before the message is delivered/relayed, governance dispatches a new `NewDeployment` on chain A setting `_instances[keccak256("CHAIN_B")] = gatewayB_v2` (a legitimate migration).
5. The relayer delivers the original `RedeemEscrow` message (`request.from = gatewayB_v1`, `request.source = "CHAIN_B"`) to chain A's `onAccept`. `_authenticate` computes `_instance("CHAIN_B") == gatewayB_v2 != gatewayB_v1`, reverting with `Unauthorized` (see `_authenticate`, `evm/src/apps/intentsv2/ExtrinsicIntents.sol:63-67`). The message can never be resubmitted successfully because `request.from` is fixed to `gatewayB_v1`.
6. The escrowed input tokens remain locked in `_orders[commitment][usdc]` on chain A, while the solver has already delivered output tokens to the beneficiary on chain B and cannot recover the escrow.
7. Separately, if the user instead calls `cancelOrder`/`_cancelFromSource` after the deadline, the GET request key is built with `_instance(order.destination) == gatewayB_v2` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:258`), reading the `_filled` slot of `gatewayB_v2` (which never processed this order and shows empty), causing `onGetResponse` to refund the user even though the order was already filled and paid out on `gatewayB_v1` — producing a double payment (solver's output + user's refunded input).

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L401-405)
```text
    function _instance(bytes calldata stateMachineId) internal view returns (address) {
        address gateway = _instances[keccak256(stateMachineId)];
        if (gateway == address(0)) revert UnknownInstance();
        return gateway;
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L63-67)
```text
    function _authenticate(PostRequest calldata request) internal view {
        if (request.from.length != 20) revert InvalidInput();
        address module = address(bytes20(request.from));
        if (_instance(request.source) != module) revert Unauthorized();
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L126-142)
```text
    /// @dev Posts `body` to the gateway on the order's source chain, paying `nativeFee` in native
    /// tokens when non-zero and in the fee token otherwise.
    function _post(Order calldata order, bytes memory body, uint256 relayerFee, uint256 nativeFee) internal {
        DispatchPost memory request = DispatchPost({
            dest: order.source,
            to: abi.encodePacked(_instance(order.source)),
            body: body,
            timeout: 0,
            fee: relayerFee,
            payer: msg.sender
        });
        if (nativeFee > 0) {
            IDispatcher(host()).dispatch{value: nativeFee}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L240-275)
```text
    function _cancelFromSource(Order calldata order, CancelOptions calldata options, bytes32 commitment) internal {
        if (order.user != bytes32(uint256(uint160(msg.sender)))) revert Unauthorized();

        if (options.height <= order.deadline) revert NotExpired();

        uint256 inputsLen = order.inputs.length;
        for (uint256 i; i < inputsLen;) {
            if (_orders[commitment][address(uint160(uint256(order.inputs[i].token)))] == 0) revert UnknownOrder();

            unchecked {
                ++i;
            }
        }

        bytes memory context =
            abi.encode(WithdrawalRequest({commitment: commitment, tokens: order.inputs, beneficiary: order.user}));

        bytes[] memory keys = new bytes[](1);
        keys[0] = bytes.concat(abi.encodePacked(_instance(order.destination)), _calculateCommitmentSlotHash(commitment));
        DispatchGet memory request = DispatchGet({
            dest: order.destination,
            keys: keys,
            timeout: 0,
            height: options.height,
            fee: options.relayerFee,
            context: context,
            payer: msg.sender
        });

        address hostAddr = host();
        if (msg.value > 0) {
            IDispatcher(hostAddr).dispatch{value: msg.value}(request);
        } else {
            dispatchWithFeeToken(request);
        }
    }
```
