Confirmed: the Tron `IntentGatewayV2.sol` at `evm/tron/contracts/apps/IntentGatewayV2.sol` has no `_relayer`/`_checkRelayer`/`setRelayer` machinery at all — a `grep_search` for those identifiers in `evm/tron/**` returns zero matches, while the EVM `ExtrinsicIntents.sol` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`) implements this relayer allowlist gate as a deliberate, documented security fix (`sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md`) specifically to close a bug class where a forged/compromised handler or unlisted relayer could deliver privileged actions to the gateway.

### Title
Tron `IntentGatewayV2.onAccept` is missing the relayer-allowlist permission check present in the EVM gateway, letting any relayer that gets a message past the host trigger escrow releases and governance actions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The EVM `IntentGatewayV2`/`ExtrinsicIntents.onAccept` (`evm/src/apps/intentsv2/ExtrinsicIntents.sol:330-350`) gates every incoming delivery with `_checkRelayer(incoming.relayer)` before decoding the request body, restricting `RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust` and `Execute` actions to a single authorized relayer once one is configured. The Tron port of the same contract, `evm/tron/contracts/apps/IntentGatewayV2.sol:629-683`, implements `onAccept` with the same `RequestKind` dispatch logic but never calls any relayer check — there is no `_relayer` storage, `_checkRelayer`, or `setRelayer` in that file at all.

### Finding Description
`onAccept` is reachable by anyone who can get a `HandlerV2`/host delivery through (`onlyHost` only restricts the caller to the host contract, not to a specific relayer identity). On the EVM side, the host passes along `relayer` (the address that actually submitted the proof-carrying transaction), and `ExtrinsicIntents.onAccept` explicitly checks `_checkRelayer(incoming.relayer)` first: [1](#0-0) 
This was added specifically because a forged handler/consensus swap could otherwise let an arbitrary relayer's delivery reach the gateway's privileged logic: [2](#0-1) 

The Tron `IntentGatewayV2.onAccept` has the identical `RequestKind` dispatch (`RedeemEscrow`/`RefundEscrow` via `authenticate`, and `NewDeployment`/`UpdateParams`/`SweepDust` gated only by `request.source == hyperbridge`) but is missing the relayer check entirely: [3](#0-2) 
A `grep_search` across `evm/tron/**` for `_relayer|checkRelayer|setRelayer|RelayerUpdated` returns no matches, confirming the allowlist mechanism simply does not exist on this contract, unlike the EVM/Solidity mainline it was ported from. This is analogous to the Fogbugz Jenkins plugin bug: an endpoint that should require a higher trust level (the specific authorized relayer/module) instead accepts any caller who satisfies a weaker check (merely `onlyHost`, i.e., anyone whose proof the host will forward), letting them trigger privileged state changes (`NewDeployment`, `UpdateParams`, `SweepDust`) — the same class of "authorization performed at the wrong trust boundary" defect, just missing on this chain's port.

### Impact Explanation
If a consensus proof can be forged or a compromised/malicious handler is installed on the Tron deployment (the exact scenario the EVM changelog cites as the motivation for adding this gate), any relayer — not just the one Hyperbridge governance designates — can deliver `SweepDust` (sweeping protocol dust to an attacker-chosen beneficiary), `UpdateParams` (rewriting protocol fee configuration), or `NewDeployment` (registering an attacker-controlled gateway instance for a state machine, which subsequently lets that instance's forged `RedeemEscrow`/`RefundEscrow` messages authenticate successfully via `_instance(request.source)`). This can lead to theft of escrowed funds and unauthorized protocol governance changes on the Tron IntentGateway.

### Likelihood Explanation
Reaching `onAccept` still requires a message to pass the host's consensus/state proof verification and `request.source == hyperbridge` check for governance actions, so this is not exploitable by a completely unprivileged party under normal, uncompromised consensus. However, unlike the EVM contract, the Tron contract has *no* additional relayer-identity check at all, so the entire "malicious/forged handler" and "unlisted relayer" threat model that the EVM side was hardened against in the 2026-09-03 change remains fully open here — any relayer whose delivery the host accepts (which, per the flow doc, is any relayer while the host's handler behaves honestly) can drive privileged actions that EVM restricts to a single designated relayer.

### Recommendation
Port the `_relayer`/`_checkRelayer`/`setRelayer` allowlist gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` to `evm/tron/contracts/apps/IntentGatewayV2.sol`, calling `_checkRelayer(incoming.relayer)` as the first statement in `onAccept` (and the equivalent in `onGetResponse` if present), consistent with the EVM implementation and its documented rationale.

### Proof of Concept
1. Deploy/observe the Tron `IntentGatewayV2` bound to a Tron ISMP host configured with a given `handler`.
2. Any relayer (not a governance-designated one) submits a `NewDeployment` or `SweepDust` `PostRequest` whose `source` matches `hyperbridge`, through the host's delivery path.
3. Because `onAccept` (`evm/tron/contracts/apps/IntentGatewayV2.sol:629`) only checks `onlyHost` and `request.source == hyperbridge` — never the identity of `incoming.relayer` — the action executes regardless of which relayer submitted it, unlike the EVM gateway which reverts with `Unauthorized` for any relayer other than the one set via `setRelayer` (see `testOnAcceptRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol:4461-4476`).

### Citations

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
