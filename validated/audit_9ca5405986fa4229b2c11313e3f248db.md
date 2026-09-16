## Title
Tron `IntentGatewayV2.onAccept`/`onGetResponse` missing relayer allow-list gate present in the EVM implementation - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The Snipe-IT advisory describes an authorization defect where a legacy code path enforces the *wrong* (weaker) permission for a privileged action, letting an under-privileged actor reach functionality intended only for a more-trusted role. The analogous defect in this repo is the Tron port of `IntentGatewayV2`: it is a parallel/legacy implementation of the same intent-settlement contract that ships without the `_relayer` allow-list gate (`_checkRelayer`) that the canonical EVM `ExtrinsicIntents.sol` enforces on every incoming settlement/governance message. Both contracts are reachable the same way — as the `IApp` callback invoked by the host after ISMP proof verification — but the Tron variant authorizes escrow release, refunds, and even upgrade/governance actions solely on `onlyHost` + `authenticate()`, omitting the extra per-delivery relayer check.

### Finding Description
In the canonical EVM contract, `ExtrinsicIntents.sol`'s `onAccept` first calls `_checkRelayer(incoming.relayer)` before decoding *anything* from the incoming request body, for every request kind (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`): [1](#0-0) 

This gate was added specifically to close a forged-consensus attack: an attacker who can forge a consensus proof could otherwise swap in a `handler` that reports an arbitrary relayer on every delivery and get `onAccept` to execute governance/escrow actions. The design decision doc for this makes the threat explicit: [2](#0-1) [3](#0-2) 

The Tron port at `evm/tron/contracts/apps/IntentGatewayV2.sol` implements the same request-kind dispatch logic (`RedeemEscrow`/`RefundEscrow`/`NewDeployment`/`UpdateParams`/`SweepDust`) in its own `onAccept`, but relies only on `onlyHost` plus `authenticate(incoming.request)` — there is no `_relayer` field, no `_checkRelayer` function, and no gate before `withdraw()` runs for `RedeemEscrow`/`RefundEscrow`: [4](#0-3) 

Its `onGetResponse` (used for source-side cancellation) is likewise ungated by any relayer check, unlike the EVM version's `_checkRelayer(incoming.relayer)` call: [5](#0-4) 
compared to the protected EVM equivalent: [6](#0-5) 

This is the same class of bug as the Snipe-IT advisory: a legacy/parallel code path implementing the same privileged action set but authorizing it with a weaker/incomplete permission check than the hardened, currently-maintained implementation — allowing an under-privileged party (here, any relayer, rather than only the allow-listed one) to execute the action.

### Impact Explanation
On the EVM host, the `_checkRelayer` gate is the last line of defense against a forged-consensus attacker who compromises the handler/consensus client to fabricate an arbitrary "relayer" identity on delivery, per the documented threat model. The Tron deployment of the same intent-settlement logic lacks this defense entirely: any relayer able to get *any* valid ISMP delivery accepted by the Tron host (whether via a legitimate proof under a compromised/forged consensus client, or via a maliciously swapped handler as described in the linked decision doc) can trigger `RedeemEscrow`/`RefundEscrow` to redirect escrowed funds, or `UpdateParams`/`NewDeployment`/`SweepDust` to alter gateway configuration or sweep protocol dust — actions that on EVM chains are restricted to a single allow-listed relayer specifically to prevent this. This is a permanent freezing/theft-of-funds vector on the escrowed intent inputs held by the Tron gateway.

### Likelihood Explanation
Exploitation requires the attacker to first get a delivery accepted by the Tron `EvmHost`-equivalent (i.e., the same forged-consensus or handler-swap precondition documented for the EVM host). This is not a fully permissionless, always-open path; it depends on a companion weakness in consensus/handler integrity being achieved first. However, unlike the EVM implementation, the Tron gateway provides **no additional layer of defense** once that precondition is met — the relayer allow-list that stops the attack on EVM chains simply does not exist here, so the same forged-consensus scenario that is contained on EVM chains fully succeeds on Tron.

### Recommendation
Port the `_relayer` / `setRelayer` / `_checkRelayer` allow-list mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (and `IntentsBase.sol`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`, gating `onAccept` and `onGetResponse` on the authorized relayer before any request-kind branching or state mutation, matching the EVM implementation's defense-in-depth against forged-consensus/handler-swap attacks.

### Proof of Concept
1. Attacker forges (or otherwise compromises) the consensus proof accepted by the Tron host, or arranges for the host's handler to be swapped (per the attack scenario documented in `sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md`), so an arbitrary delivery is accepted as coming "from" a legitimate `IntentGatewayV2` peer instance.
2. Attacker crafts a `PostRequest` body with `RequestKind.RedeemEscrow` (or `RefundEscrow`) naming themselves as `beneficiary`, addressed to the Tron `IntentGatewayV2` instance, sourced from the registered peer instance address so `authenticate()` passes.
3. Any relayer (not an allow-listed one — none exists) submits this to the Tron host; `onAccept` runs `onlyHost` → `authenticate()` → `withdraw()`, releasing escrowed input tokens to the attacker-controlled beneficiary, with **no relayer check** blocking the delivery — unlike the equivalent EVM path where `_checkRelayer` would reject any relayer but the allow-listed one before the body is even decoded (as exercised by `testOnAcceptGovernanceRejectsUnlistedRelayer` / `testOnGetResponseRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol`).

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L330-350)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        RequestKind kind = RequestKind(uint8(incoming.request.body[0]));
        if (kind == RequestKind.RedeemEscrow || kind == RequestKind.RefundEscrow) {
            _authenticate(incoming.request);
            WithdrawalRequest memory body = abi.decode(incoming.request.body[1:], (WithdrawalRequest));
            return _withdraw(body, kind == RequestKind.RefundEscrow, true);
        }

        // only hyperbridge is permitted to perform these actions
        if (keccak256(incoming.request.source) != keccak256(IDispatcher(host()).hyperbridge())) revert Unauthorized();
        if (kind == RequestKind.NewDeployment) {
            _addDeployment(abi.decode(incoming.request.body[1:], (Deployment)));
        } else if (kind == RequestKind.UpdateParams) {
            _updateParams(abi.decode(incoming.request.body[1:], (ParamsUpdate)));
        } else if (kind == RequestKind.SweepDust) {
            _sweepDust(abi.decode(incoming.request.body[1:], (SweepDust)));
        } else if (kind == RequestKind.Execute) {
            Address.functionDelegateCall(ERC1967Utils.getImplementation(), incoming.request.body[1:]);
        }
    }
```

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L360-367)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        _checkRelayer(incoming.relayer);
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        _withdraw(body, true, true);
    }
}
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-hostmanager-deliveries-are-gated-too-and-that-does-not-touch.md (L1-14)
```markdown
# 2026-09-03 — `HostManager` deliveries are gated too, and that does not touch permissionless relaying

Chosen: `HostManager.onAccept` refuses any relayer but the one the host admin set, zero included.

The app gates check an address the host reports, and the host takes it from its handler. The
handler is a host parameter that a `SetHostParam` governance message can replace, and until now
any relayer could deliver that message once its consensus proof verified. Under a forged consensus
an attacker would swap in a handler that reports the whitelisted relayer on every message, and the
app gates would pass. Gating the HostManager closes that route.

It does not weaken the open-relayer model because the HostManager never carries user traffic. Its
first check already rejects anything not sourced from Hyperbridge, so the only messages it ever
sees are Polytope's own `Withdraw` and `SetHostParam`. Third-party relayers keep delivering every
ordinary message to every ordinary app exactly as before.
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md (L1-14)
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

The interface gains `RelayerUpdated(address previous, address current)` and `setRelayer`, keeping
its declarations identical to `IntentsBase`. The unused `_paused` getter was dropped from the gateway
to stay under the EIP-170 size limit; it was never declared here.
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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L738-744)
```text
    function onGetResponse(IncomingGetResponse calldata incoming) external override onlyHost {
        if (incoming.response.values[0].value.length != 0) revert Filled();

        WithdrawalRequest memory body = abi.decode(incoming.response.request.context, (WithdrawalRequest));
        withdraw(body, true);
    }
}
```
