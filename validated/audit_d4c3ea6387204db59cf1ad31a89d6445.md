### Title
Tron `IntentGatewayV2.onAccept`/`onGetResponse` omit the relayer-allowlist check present in the canonical EVM gateway, letting any relayer deliver privileged cross-chain governance and escrow actions - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The canonical EVM `IntentGatewayV2` implementation (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`) gates every `onAccept` and `onGetResponse` delivery with `_checkRelayer(incoming.relayer)` before doing anything else, restricting who may trigger escrow redemption/refund, `NewDeployment`, `UpdateParams`, `SweepDust`, and `Execute` (which reaches `upgradeToAndCall`/`setRelayer`). The Tron port of this same contract (`evm/tron/contracts/apps/IntentGatewayV2.sol`) has no `_relayer` state, no `_checkRelayer`, and no `setRelayer` at all — its `onAccept` (lines 629–683) and `onGetResponse` (lines 738–743) go straight from `onlyHost` to decoding the request body and executing it.

### Finding Description
`onlyHost` in `HyperApp` only proves the call came from the local `IsmpHost`/`TronHost` contract, which itself is proven only through consensus/state-proof verification and delivers messages from **any permissionless relayer** (`EvmHost.dispatchIncoming` → `restrict(_hostParams.handler)` → any `msg.sender` calling `HandlerV2.handlePostRequests`). The relayer identity that actually submitted the proof is passed through as `incoming.relayer`; on the canonical contract this is checked against an owner-settable allowlist (`_checkRelayer`) before any state-mutating branch runs, per the documented decision in `sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md` and `sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md`.

The Tron variant's `onAccept`:
```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
    if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
        authenticate(incoming.request);
        ...
``` [1](#0-0) 

never checks `incoming.relayer` at all — there is no `_relayer` storage variable, no `setRelayer`, and no gate function in the file (confirmed via grep across `evm/tron/contracts/apps/IntentGatewayV2.sol`). `authenticate()` only checks that `request.from`/`request.source` matches a registered gateway `_instance` — it says nothing about which relayer delivered the proof. Likewise `onGetResponse` only checks `incoming.response.values[0].value.length`, again omitting any relayer check: [2](#0-1) 

This mirrors the ERPNext bug class exactly: a security-relevant permission check that exists in sibling code (the source-chain contract this was ported from) was silently dropped in the ported/duplicated function, letting a caller with lesser trust (here, an arbitrary relayer instead of the whitelisted one) perform privileged writes.

### Impact Explanation
On Tron, once a `NewDeployment`, `UpdateParams`, or `SweepDust` governance-style ISMP message is dispatched from Hyperbridge with a valid consensus/state proof, **any relayer** — not just the operator-designated one — can be the one who submits `handlePostRequests`/`handleGetResponses` and thus be recorded as `incoming.relayer`, without the contract rejecting it. Because forged-handler/forged-relayer swap attacks are exactly what the `_checkRelayer` gate was added to defend against elsewhere in the codebase (see the HostManager and BridgeToken decisions), the Tron gateway is missing that defense-in-depth layer: a compromised or malicious consensus/handler configuration, or a relayer race condition, could let an unauthorized relayer front-run legitimate delivery of `SweepDust` (redirecting protocol dust) or manipulate `UpdateParams`/`NewDeployment` before the intended relayer does. This is a state-integrity/authorization issue for escrowed funds and gateway configuration.

### Likelihood Explanation
Reachable from a single relayed message: an unprivileged relayer that observes a pending Hyperbridge-originated dispatch to the Tron gateway (or an attacker abusing a forged/compromised handler as documented in the sibling EVM findings) can be the one to deliver it, since the contract performs no allowlist check on `incoming.relayer`. The likelihood of exploitation is bounded by the same conditions that gate the analogous EVM attack (forged consensus/handler), but the missing check removes a layer of defense that the rest of the codebase treats as required, and it is trivially reachable by any address able to call `HandlerV2`/`TronHost`'s message-delivery entrypoints.

### Recommendation
Port the `_relayer`/`setRelayer`/`_checkRelayer` gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` at the top of both `onAccept` and `onGetResponse` before any branch executes, consistent with the rest of the codebase's relayer-gating pattern.

### Proof of Concept
1. Hyperbridge governance dispatches a `SweepDust` (or `UpdateParams`/`NewDeployment`) POST request addressed to the Tron `IntentGatewayV2`.
2. Instead of the operator's intended relayer, any other relayer submits the proof to `TronHost`/`HandlerV1`, which calls `dispatchIncoming` → `IApp.onAccept(IncomingPostRequest(request, thatRelayer))`.
3. `IntentGatewayV2.onAccept` on Tron only checks `onlyHost` and, for governance kinds, that `request.source` equals Hyperbridge — it never checks `thatRelayer` against an authorized value (there is none), so the action executes exactly as if the intended relayer had delivered it, unlike the EVM contract which would revert with `Unauthorized` via `_checkRelayer` for an unlisted relayer (as exercised by `testOnGetResponseRejectsUnlistedRelayer` and `testOnAcceptGovernanceRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol`, lines 4478–4514). [3](#0-2)

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L629-638)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-743)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4502-4514)
```text
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
