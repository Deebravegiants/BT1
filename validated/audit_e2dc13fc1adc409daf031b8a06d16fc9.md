## Analog Found

### Title
Missing relayer allowlist gate in Tron `IntentGatewayV2.onAccept` lets escrow release/refund execute on proof alone — (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The CVE describes a bug class where a privileged/destructive action is permitted because an access-control check that should gate it is missing or evaluated too late relative to the action. The Tron port of `IntentGatewayV2.onAccept` omits the `_checkRelayer` gate that the canonical EVM implementation enforces before acting on any incoming settlement message, so `RedeemEscrow`/`RefundEscrow` delivery is authorized solely by proof/module-address matching, with no independent relayer allowlist check.

### Finding Description
On the reference EVM implementation, `ExtrinsicIntents.onAccept` runs `onlyHost`, then immediately `_checkRelayer(incoming.relayer)` before the body's `RequestKind` byte is even read: [1](#0-0) 

`_checkRelayer` fails closed once armed, rejecting every submitter but the authorised relayer: [2](#0-1) 

This gate is documented as a required, not merely defense-in-depth, control for economically-backed apps — e.g. `BridgeToken` explicitly states its supply "must not mint on the strength of a consensus proof alone": [3](#0-2) 

The delivery-reachability doc confirms `relayer` is simply `msg.sender` on the handler call — it is **not** part of the cryptographically-proven request, so any address can attach itself as "the relayer" by being the one to submit a valid proof: [4](#0-3) 

The Tron variant of `IntentGatewayV2.onAccept`, however, never calls any relayer-check function at all — it goes straight from `onlyHost` to decoding `RequestKind` and, for `RedeemEscrow`/`RefundEscrow`, only calls `authenticate(incoming.request)` (which validates `request.source`'s registered module address, not the delivering relayer) before calling `withdraw`: [5](#0-4) 

A grep of the file confirms there is no `_relayer` state variable, `setRelayer`, or `_checkRelayer` function anywhere in this contract — the allowlist mechanism present in the audited reference implementation is entirely absent here. `withdraw` itself unconditionally transfers escrowed tokens/fees to the beneficiary once called: [6](#0-5) 

This is structurally the same bug class as ALPINE-CVE-2017-15365: an authorization check (ACL/allowlist) that the correct code path performs before the privileged action is either reordered or dropped, allowing the privileged action (here, cross-chain escrow release) to execute using only the weaker check (proof/module-address matching) that the design elsewhere treats as insufficient on its own.

### Impact Explanation
Because `relayer` is attacker-controllable (any caller of the handler with a merely-valid state/consensus proof becomes "the relayer" for that delivery), the missing gate removes the second authorization factor the protocol relies on for high-value asset release. Any party able to produce or await a valid membership/consensus proof for a `RedeemEscrow`/`RefundEscrow` request can submit it and immediately drain the corresponding escrow to the beneficiary named in the proven request — a direct path to concrete theft/loss of escrowed user funds on the Tron deployment, without needing to compromise a trusted relayer allowlist that other chains require.

### Likelihood Explanation
High for the Tron deployment specifically: the check is not merely misordered but absent, and the precondition (submitting a request whose proof will eventually validate, e.g. once the source chain state advances past the relevant commitment) is a normal, unprivileged relayer action — no privileged role or race condition is needed beyond what any ordinary user/relayer already does to deliver settlement messages.

### Recommendation
Add the same `_relayer` allowlist state and `_checkRelayer` gate used in `evm/src/apps/intentsv2/ExtrinsicIntents.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`, invoked as the first check in `onAccept` (and `onGetResponse`) before any `RequestKind` is decoded or acted upon, matching the ordering and fail-closed semantics of the canonical implementation.

### Proof of Concept
1. A user places a cross-chain order on the source chain; escrow is recorded in `_orders[commitment]` on the Tron destination/source contract.
2. Once the order is filled/cancelled and the corresponding `RedeemEscrow`/`RefundEscrow` `PostRequest` becomes provable against the source chain's committed state, any address — not merely a governance-authorised relayer — calls the ISMP handler with the valid proof, becoming `incoming.relayer`.
3. `IntentGatewayV2.onAccept` (Tron) runs no relayer check, only `authenticate(incoming.request)` (module-address match) which the legitimately-formed request passes, then calls `withdraw`, releasing the escrow to the beneficiary named in the request.
4. Compare to the reference `ExtrinsicIntents.onAccept`/`IntentGatewayV2.sol` (main EVM) flow, where the same delivery attempt would first hit `_checkRelayer` and revert with `Unauthorized` unless submitted by the allow-listed relayer, per `testOnAcceptGovernanceRejectsUnlistedRelayer`/`testOnGetResponseRejectsUnlistedRelayer`: [7](#0-6) 

Note: I was unable to determine from the index whether the Tron contract's `_relayer` gate was intentionally omitted for a Tron-specific reason (e.g., different host/consensus trust model) — a background Devin session with full repo access could confirm whether Tron's `EvmHost`/handler analog provides an equivalent guarantee elsewhere.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L75-78)
```text
    function _checkRelayer(address relayer) internal view {
        address authorised = _relayer;
        if (authorised != address(0) && relayer != authorised) revert Unauthorized();
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

**File:** evm/src/apps/BridgeToken.sol (L100-107)
```text
    /**
     * @dev Fails closed: with no relayer set nobody may deliver. The supply of this token is backed
     * by the nexus escrow, so it must not mint on the strength of a consensus proof alone. The
     * handler always forwards a real `msg.sender`, so zero never matches.
     */
    function _checkRelayer(address incomingRelayer) private view {
        if (incomingRelayer != _relayer) revert UnauthorizedRelayer();
    }
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-17)
```markdown
1. A relayer calls `HandlerV2.handlePostRequests` (or `handleGetResponses`). After proof
   verification the handler calls `host.dispatchIncoming(request, _msgSender())`. `_msgSender()` is
   plain `msg.sender`; the handler has no trusted forwarder.
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
3. `ExtrinsicIntents.onAccept` runs `onlyHost`, then `_checkRelayer(incoming.relayer)`, which reverts
   with `Unauthorized` when a relayer is set and the delivery is from anyone else. Only then is the
   first body byte read as a `RequestKind`. `onGetResponse` has the same two steps before touching
   the response.
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4478-4514)
```text
    function testOnAcceptGovernanceRejectsUnlistedRelayer() public {
        // UpgradeContract: a forged upgrade cannot land unless the relayer submits it.
        address implBefore = _implementationOf(address(intentGateway));
        IntentGatewayV2Upgraded newImpl = new IntentGatewayV2Upgraded(address(this));
        PostRequest memory upgrade = _upgradeRequest(host.hyperbridge(), address(newImpl), "");

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: upgrade}));
        assertEq(_implementationOf(address(intentGateway)), implBefore, "implementation unchanged");

        // NewDeployment: the gate runs before the body is decoded, so every kind is covered.
        PostRequest memory deployment = _newDeploymentRequest(bytes("NEW_CHAIN"), address(0xBEEF));
        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onAccept(IncomingPostRequest({relayer: filler, request: deployment}));
        vm.expectRevert(IntentsBase.UnknownInstance.selector);
        intentGateway.instance(bytes("NEW_CHAIN"));

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: deployment}));
        assertEq(intentGateway.instance(bytes("NEW_CHAIN")), address(0xBEEF), "relayer-submitted governance applies");
    }

    function testOnGetResponseRejectsUnlistedRelayer() public {
        (GetResponse memory response, bytes32 commitment, uint256 amount) = _cancelResponse();

        vm.prank(address(host));
        vm.expectRevert(IntentsBase.Unauthorized.selector);
        intentGateway.onGetResponse(IncomingGetResponse({response: response, relayer: user}));
        assertEq(intentGateway._orders(commitment, address(usdc)), amount, "escrow untouched");

        uint256 before = usdc.balanceOf(user);
        vm.prank(address(host));
        intentGateway.onGetResponse(IncomingGetResponse({response: response, relayer: relayer}));
        assertEq(usdc.balanceOf(user) - before, amount, "authorised relayer refunds escrow");
    }
```
