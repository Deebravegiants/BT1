Based on the extensive research, I found the tron `IntentGatewayV2.sol` variant lacks the relayer allowlist gate that was added to the EVM version.### Title
Missing relayer authorization gate in Tron `IntentGatewayV2.onAccept` allows any relayer to execute escrow redemption and governance actions - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Keycloak CVE-2020-1725 describes a system where an authorization change (revoking role mappings) fails to actually revoke access for callers that should no longer be trusted. The Hyperbridge codebase implements the analogous protection for `IntentGatewayV2` via a single-relayer allowlist gate (`_checkRelayer`) that must run before any `onAccept` body is decoded, specifically to stop an attacker who forges a consensus proof from directly reaching escrow release and governance logic. The Tron variant of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, never received this authorization check, so this reachable code path silently omits the access-control gate present everywhere else.

### Finding Description
On the canonical EVM implementation, `ExtrinsicIntents.onAccept` (used by `evm/src/apps/IntentGatewayV2.sol`) calls `_checkRelayer(incoming.relayer)` as the very first statement, before the request body's `RequestKind` byte is even read: [1](#0-0) 

`_checkRelayer` rejects any delivery whose reported relayer is not the single authorised one once armed: [2](#0-1) 

The project's own documentation states plainly why this gate exists: without it, a forged consensus proof lets an attacker's controlled "relayer" reach every `onAccept` action — redemptions, refunds, and every governance action including upgrades: [3](#0-2) 

The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, implements the identical `RequestKind` dispatch (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`) inside `onAccept`, but never calls any relayer check — the function goes straight from the `onlyHost` modifier to decoding `RequestKind`: [4](#0-3) 

`onlyHost` only proves the call originated from the local `EvmHost`/handler after a consensus proof was accepted; it says nothing about which relayer delivered the message. On the gated implementations, that is exactly the gap `_checkRelayer` closes: even a call that legitimately arrives through `onlyHost` (i.e., after passing consensus verification) is still refused unless it came from the one relayer the gateway's admin authorised. The Tron contract lacks this second layer entirely, so the authorization decision that the rest of the fleet enforces is effectively "revoked" (never granted) for this deployment target — precisely the incorrect-authorization pattern in the reference CVE, where an intended access restriction fails to actually apply to a reachable resource.

### Impact Explanation
Because the relayer allowlist is the control that specifically defends against a forged/eclipsed consensus proof reaching escrow funds and governance (per the project's own design rationale), its absence on the Tron gateway means:
- Any party able to get a (forged or otherwise illegitimate) consensus proof accepted by the local host can directly trigger `RedeemEscrow`/`RefundEscrow`, releasing escrowed user funds to an attacker-chosen address, with no secondary relayer-identity check.
- `NewDeployment`, `UpdateParams`, and `SweepDust` — governance-only actions — are reachable the same way, allowing unauthorized reconfiguration of gateway parameters, protocol fees, or dust destinations, and forged registration of malicious remote gateway instances (which `_authenticate` would then trust for future escrow authentication).

This is concrete theft-of-funds and unauthorized-app-action exposure on the intents escrow flow, matching the Medium/High severity band required.

### Likelihood Explanation
Exploitation requires the attacker to get a message accepted by the local `EvmHost` (i.e., pass consensus/state proof verification), which is the same bar every other chain's gateway also requires before its relayer gate even runs. The difference is that on every other deployment, clearing that bar is necessary but not sufficient — the relayer gate is a second, independent check. On Tron, clearing the consensus bar alone is sufficient. This significantly lowers the bar relative to the fleet's documented threat model (which explicitly assumes consensus proofs can be forged/eclipsed) and is directly reachable from a single relayed message with no additional privilege.

### Recommendation
Port the `_relayer` / `_checkRelayer` / `setRelayer` / `RelayerUpdated` gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` and `evm/src/apps/intentsv2/IntentsBase.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` as the first statement of `onAccept` (and the equivalent for `onGetResponse`), before the `RequestKind` byte is read, matching the ordering and semantics (fail-open only while unset, fail-closed to any other relayer once armed) used on the EVM implementation.

### Proof of Concept
1. On the Tron deployment, an attacker (or eclipse-attack collaborator) gets a consensus proof for `EvmHost` accepted, allowing `dispatchIncoming` to call `IntentGatewayV2.onAccept` with an `IncomingPostRequest` whose `relayer` field is the attacker's own address (the handler simply forwards `_msgSender()` as the relayer, per `evm/src/core/HandlerV2.sol`'s `dispatchIncoming` flow described in the flow doc).
2. The attacker crafts a `RedeemEscrow`/`RefundEscrow` body targeting an active escrowed order and submits it as that relayer.
3. `onAccept` in `evm/tron/contracts/apps/IntentGatewayV2.sol` reaches `authenticate(incoming.request)` and `withdraw(...)` with no prior relayer check, releasing escrowed funds to the attacker-controlled address — behavior that `testOnAcceptRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol` proves is explicitly blocked on the gated EVM implementation but has no equivalent test/guard for the Tron contract.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L69-78)
```text
    /**
     * @dev Once a relayer is set, rejects deliveries from anyone else before the body is read. The
     * host records the revert as undelivered, so the authorised relayer can resubmit. While unset,
     * every delivery passes: a proxy from before the gate stays open until `migrate` arms it.
     * @param relayer The account that submitted the message to the handler.
     */
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

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-10)
```markdown
# 2026-09-03 — Relayer allowlist on the intent gateway

The gateway now accepts `onAccept` and `onGetResponse` deliveries only from a single authorised
relayer stored at `_relayer` (slot 13, packed behind `_paused`). The check runs before the message
body is decoded, so escrow redemptions, refunds and every governance action, upgrades included, are
covered. A refused delivery reverts, which the host records as undelivered, so the authorised
relayer can submit the same message later. `setRelayer(address)` is callable by the immutable
`_owner` and by the host; the host branch exists so a governance `UpgradeContract` can carry the
call as its migration calldata and arm the relayer in the upgrade transaction (`upgradeToAndCall`
delegatecalls that calldata with the host still as `msg.sender`).
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-644)
```text
    /**
     * @notice Executes an incoming post request.
     * @dev This function is called when an incoming post request is accepted.
     * It is only accessible by the host.
     * @param incoming The incoming post request data.
     */
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return withdraw(body, kind == RequestKind.RefundEscrow);
        }

        // only hyperbridge is permitted to perfom these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            NewDeployment memory body = abi.decode(incoming.request.body[1:], (NewDeployment));
            _instances[keccak256(body.stateMachineId)] = body.gateway;

            emit NewDeploymentAdded({stateMachineId: body.stateMachineId, gateway: body.gateway});
        } else if (kind == RequestKind.UpdateParams) {
```
