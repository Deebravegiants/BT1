Found one clear analog. In `BandwidthManager.onAccept` there's a missing check that its sibling contracts (`ExtrinsicIntents`, `HostManager`) always run before acting on governance-sourced messages: a relayer allowlist / `_checkRelayer` gate.

### Title
Missing relayer-authorization check on `BandwidthManager.onAccept` allows any relayer to trigger `Withdraw`/`SetTiers` actions - ([File: evm/src/apps/BandwidthManager.sol])

### Summary
`BandwidthManager.onAccept` (evm/src/apps/BandwidthManager.sol:208-232) only checks `onlyHost` and that `request.source` equals Hyperbridge. It never checks `incoming.relayer` (the address that submitted the delivery to `HandlerV2`/`EvmHost.dispatchIncoming`), unlike every other app contract in this codebase that accepts governance-style inbound messages, all of which gate on a `_checkRelayer` allow-list before acting on the decoded body.

### Finding Description
Every other Hyperbridge application contract that accepts privileged, pallet-originated `onAccept` payloads enforces a relayer allow-list in addition to `onlyHost` + source checks:

- `ExtrinsicIntents._checkRelayer(incoming.relayer)` runs before decoding *any* `RequestKind`, including governance actions (`NewDeployment`, `UpdateParams`, `SweepDust`, `Execute`) — `evm/src/apps/intentsv2/ExtrinsicIntents.sol:331` and the changelog `sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-the-intent-gateway.md`.
- `HostManager.onAccept` runs the same relayer check before decoding governance actions (per `sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md`).
- `HyperFungibleToken`/`BridgeToken` gained the same `_checkRelayer` gate specifically because "both callbacks mint, so both are gated" (`sdk/packages/core/docs/ai/changelog/2026-09-03-relayer-allowlist-on-hyperfungibletoken-fail-closed-on-the.md`).
- `SimplexPaymaster` "governance deliveries gated on one relayer" per its changelog.

`BandwidthManager.onAccept`, which processes the exact same class of privileged governance actions — `SetTiers` (repricing every future purchase) and `Withdraw` (unconditionally transferring ERC20 or native funds out of the contract to an attacker-controlled `beneficiary`) — has no such gate:

```solidity
function onAccept(IncomingPostRequest calldata incoming) external override onlyHost {
    PostRequest calldata request = incoming.request;
    if (!request.source.equals(IDispatcher(_host).hyperbridge())) revert UnauthorizedAction();
    OnAcceptActions action = OnAcceptActions(uint8(request.body[0]));
    ... // SetTiers / Withdraw decoded and executed unconditionally
}
```
(evm/src/apps/BandwidthManager.sol:208-232)

This is structurally the same class of bug as the pyftpdlib advisory: a permission check that the sibling operations/commands consistently enforce (the relayer allow-list, analogous to the `l` permission requirement other FTP list commands enforced) is simply missing on this one code path, letting an unprivileged actor reach privileged functionality (`MLST` listing directories / here, `Withdraw` draining funds) that should have been gated.

`onlyHost` alone is insufficient protection here because `EvmHost.dispatchIncoming` (evm/src/core/EvmHost.sol) calls `onAccept` for *every* message the handler relays regardless of which relayer (`_msgSender()` in `HandlerV2`) submitted it — `msg.sender` on the call into the app is always the host, but the actual relayer identity is only available via `incoming.relayer`, which is exactly the value every other app checks and `BandwidthManager` ignores.

### Impact Explanation
If `pallet-bandwidth` ever dispatches a legitimate `Withdraw` or `SetTiers` PostRequest (source == Hyperbridge, to == `PALLET_BANDWIDTH_MODULE_ID`), any relayer — not just the one Hyperbridge/governance designates as trusted — can be the one to deliver it. More importantly, because there is no relayer allow-list distinguishing "this delivery is trusted" from "this delivery merely has the right source/module", any relayer that races to deliver such a message controls exactly which withdrawal/tier-update executes and when, with no ability for governance to restrict delivery to an audited relayer set the way it does for the intents gateway and the fungible tokens. This directly threatens the treasury funds (`Withdraw` sends ERC20 or native token to an attacker/arbitrary `beneficiary` decided by whatever body Hyperbridge encoded) and the pricing integrity (`SetTiers`) — High severity per the theft/fund-safety criteria, since it is a fund-movement code path guarded by a control that is present on every comparable contract but absent here.

### Likelihood Explanation
Reaching this path only requires that Hyperbridge itself dispatch a `Withdraw`/`SetTiers` message once (an expected governance operation for a "storefront" contract whose whole purpose is to be topped up and drained by the pallet) and that message be observed and relayed by any permissionless relayer, which `handlePostRequests` allows anyone to do. No malicious governance/admin/collator action is needed — this is the day-to-day intended flow, just missing the relayer restriction its sibling contracts consider mandatory for the same class of action.

### Recommendation
Add a `_checkRelayer(incoming.relayer)` (or equivalent allow-list) gate to `BandwidthManager.onAccept`, mirroring `ExtrinsicIntents`/`HostManager`/`HyperFungibleToken`, so that `Withdraw` and `SetTiers` can only be delivered by a designated, governance-set relayer, consistent with how every other privileged `onAccept` handler in this codebase is protected.

### Proof of Concept
1. Hyperbridge (`pallet-bandwidth`) dispatches a `Withdraw` PostRequest addressed to `BandwidthManager`, with `beneficiary` set to the treasury per normal governance flow.
2. Instead of the relayer Hyperbridge/governance intends, any third-party relayer observes the pending request/proof and calls `HandlerV2.handlePostRequests` to deliver it themselves.
3. `EvmHost.dispatchIncoming` invokes `BandwidthManager.onAccept(IncomingPostRequest(request, thirdPartyRelayer))`.
4. `onAccept` checks only `onlyHost` and `request.source == hyperbridge`; it never inspects `incoming.relayer`, so the withdrawal executes regardless of who delivered it — unlike `ExtrinsicIntents`/`HyperFungibleToken`, which would revert with `Unauthorized`/`UnauthorizedRelayer` for the same scenario once a relayer allow-list is armed.