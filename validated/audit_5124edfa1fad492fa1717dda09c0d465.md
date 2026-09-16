### Title
Tron `IntentGatewayV2.onAccept` / `onGetResponse` lack the relayer allowlist gate present in the audited EVM version, letting any relayer force escrow settlement decisions - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2` implements `onAccept` and `onGetResponse` with only an `onlyHost` modifier and, for privileged governance actions, a `hyperbridge`-source check ` [1](#0-0) `. It never calls a `_checkRelayer`/relayer-allowlist gate before branching on `RequestKind` or paying out escrow, unlike the canonical EVM `ExtrinsicIntents.onAccept`, which runs `_checkRelayer(incoming.relayer)` first, before decoding the body, specifically to close this class of authorization gap ` [2](#0-1) `.

### Finding Description
On the main EVM `IntentGatewayV2`/`ExtrinsicIntents`, the project deliberately added a relayer allowlist so that only one authorised relayer's proof delivery is accepted for `onAccept`/`onGetResponse`, covering escrow redemptions, refunds and governance actions, per the documented decision and changelog ` [3](#0-2) ` and the runtime check `_checkRelayer` ` [4](#0-3) `.

The Tron contract `evm/tron/contracts/apps/IntentGatewayV2.sol` does not carry this gate at all: `onAccept` is `onlyHost` only, decodes `RequestKind` immediately, and for `RedeemEscrow`/`RefundEscrow` only calls `authenticate(incoming.request)` (source-module check), never a relayer check, before calling `withdraw()` which pays tokens out of escrow ` [5](#0-4) `. Likewise `onGetResponse` performs no relayer check before calling `withdraw(body, true)` ` [6](#0-5) `.

Since the host's `dispatchIncoming` forwards `msg.sender` of whoever called the `HandlerV2` (any address that submits a valid proof, i.e. any unprivileged relayer) as the `relayer` field on the `IncomingPostRequest`/`IncomingGetResponse` ` [7](#0-6) `, and the Tron gateway makes no use of that field for access control, any address capable of submitting a correctly-proved message through `HandlerV2` (which itself is a permissionless entrypoint open to "an unprivileged message dispatcher, relayer... intent solver") can trigger escrow settlement (`withdraw`), governance param changes, or `SweepDust`/`NewDeployment` handling on the Tron deployment ahead of, or instead of, the intended/authorised relayer. This mirrors the CVE-2023-22251 bug class: a low-privileged, but still-authenticated (proof-verified) actor can reach functionality/paths meant to be restricted to a privileged party (the allowlisted relayer), because the authorization check that exists on the sibling EVM implementation was omitted here.

### Impact Explanation
While message content is still constrained by proof verification (state commitment/consensus) and by the `authenticate()`/hyperbridge-source checks for governance kinds, the missing relayer gate removes an authorization layer the rest of the codebase treats as load-bearing (per the 2026-09-03 decision docs, closing exactly this "any relayer" route was the stated fix for the EVM contract, and a forged-handler/relayer-swap scenario is explicitly tested against in `HostManagerTest.sol`). On Tron, order settlement ordering and delivery timing controls (which the relayer gate exists to give the intended relayer/operator exclusive control over) are bypassable by any third party able to relay a valid proof, letting an unauthorized party force `withdraw`/`SweepDust`/governance-kind execution paths to run through a different, unauthorised submitter than the protocol's operational model intends. This is a genuine deviation from the hardened path and a concrete "unauthorized app action" per the validation criteria, though it is Tron-specific and does not by itself let an attacker forge message content (proofs are still checked upstream).

### Likelihood Explanation
Reaching this requires only what any relayer can already do: submit a legitimately-provable request/response through the Tron `HandlerV2`-equivalent flow and have it delivered to the gateway; there is no privileged key, admin, or governance role needed to exploit the missing gate, matching the CVE's "low-privileged authenticated attacker" threat model. Because HandlerV2/host delivery is open to anyone submitting valid proofs (per `docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md`), likelihood of triggering the unguarded path is high once a valid message exists.

### Recommendation
Port the `_relayer`/`_checkRelayer` gate from `ExtrinsicIntents.sol` (or the equivalent `_checkRelayer` pattern used in `BridgeToken.sol`/`SimplexPaymaster.sol`) into the Tron `IntentGatewayV2.sol`: store an authorised relayer, check `incoming.relayer` against it at the very start of `onAccept` and `onGetResponse` before any `RequestKind` decoding or `withdraw()` call, and provide a governance-gated `setRelayer` setter consistent with the EVM implementation.

### Proof of Concept
1. An order is placed and awaits a legitimate `RedeemEscrow`/`RefundEscrow`/GET-response delivery to the Tron `IntentGatewayV2`.
2. Any third-party account (not the intended/authorised relayer) submits the already-available valid proof through the host/handler so that `EvmHost.dispatchIncoming`/`dispatchIncoming(GetResponse,...)` calls `onAccept`/`onGetResponse` with their own address as `incoming.relayer` ` [7](#0-6) `.
3. `IntentGatewayV2.onAccept` (Tron) validates only `onlyHost` and, for escrow kinds, `authenticate(incoming.request)` — never the relayer — and proceeds straight to `withdraw()` ` [5](#0-4) `, and `onGetResponse` likewise settles escrow without any relayer check ` [6](#0-5) `, demonstrating that any relayer, not just the one the protocol's operational/governance model designates as authorised, can force these code paths to execute.

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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L328-341)
```text
     * @param incoming The incoming post request from Hyperbridge.
     */
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

**File:** evm/src/core/EvmHost.sol (L824-833)
```text
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));
```
