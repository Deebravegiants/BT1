Confirmed: the Tron variant of `IntentGatewayV2.onAccept` only enforces `onlyHost` plus `authenticate(incoming.request)` before processing `RedeemEscrow`/`RefundEscrow` — it never calls a relayer-allowlist check. This is the exact protection that was added to the canonical EVM implementation (`evm/src/apps/intentsv2/ExtrinsicIntents.sol`) via `_checkRelayer(incoming.relayer)`.

### Title
Missing relayer allowlist gate on Tron `IntentGatewayV2.onAccept` allows any relayer to trigger escrow redemption/refund - ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Phemex hack was fundamentally an access-control failure: the same weak authorization scheme was replicated across dozens of chains, and the attacker only needed to find and hit the weakest link to drain funds chain by chain. Hyperbridge's `IntentGatewayV2` has an analogous multi-chain deployment story — the canonical EVM implementation and the Tron fork are separate copies of the same contract, and a security control that was added to one was not propagated to the other, leaving that chain's deployment as the "weakest link."

### Finding Description
`evm/src/apps/intentsv2/ExtrinsicIntents.sol` gates every `onAccept`/`onGetResponse` delivery with `_checkRelayer(incoming.relayer)` before decoding or acting on the request body: [1](#0-0) 

This relayer allowlist was deliberately added (per the changelog/decision docs) so that only a single governance-designated relayer can deliver `onAccept` calls, closing off delivery from arbitrary relayers once armed: [2](#0-1) [3](#0-2) 

However, the Tron deployment of the identical contract, `evm/tron/contracts/apps/IntentGatewayV2.sol`, has `onAccept` gated only by `onlyHost` (plus `authenticate` for the `from` field check) — there is no `_relayer` state variable, no `setRelayer`, and no `_checkRelayer` call anywhere in the file: [4](#0-3) 

Since `EvmHost.dispatchIncoming` forwards `_msgSender()` of whichever address called `HandlerV2.handlePostRequests` as the `relayer` field with no trusted-forwarder restriction, and `HandlerV2`'s handler functions are explicitly permissionless ("Access: Permissionless (can be called by anyone)"): [5](#0-4) [6](#0-5) 

the Tron gateway accepts a `RedeemEscrow`/`RefundEscrow` delivery from any account that submits a valid state/consensus proof, rather than requiring the specific relayer the rest of the fleet requires. This is the same "one chain didn't get the fix, so it becomes the door that swings open" pattern rekt.news describes for Phemex's multi-chain hot wallets, applied to smart-contract authorization logic instead of private keys.

### Impact Explanation
The relayer allowlist on the canonical `ExtrinsicIntents`/`IntentGatewayV2` is a deliberate second layer of defense on top of proof verification, explicitly designed to prevent, among other things, forged/undesired deliveries and to give governance a chokepoint to pause bad message flows (e.g., during a compromised handler or forged proof scenario, per `testForgedHandlerSwapIsRefused` and the relayer-gate flow doc). Its absence on the Tron deployment means that chain lacks this defense-in-depth: any account capable of assembling a valid consensus/state proof for a delivered order (including a self-relayed one, which the SDK explicitly supports) can trigger escrow release logic without going through the governance-designated relayer, undermining the uniform security guarantee the fleet is supposed to provide and potentially enabling unauthorized release/refund flows that the allowlisted-relayer design was meant to prevent.

### Likelihood Explanation
High, in the sense that it requires no privileged access, no admin/key compromise, and no unusual capability — an attacker only needs to be able to submit `handlePostRequests` calldata (permissionless by design) against the Tron `IntentGatewayV2`, exactly the normal "self-relay" path documented in the SDK. This mirrors the reachability bar for the analog (a single relayed message/proof), and the divergence between the two copies of the contract is a straightforward audit/config-drift class of bug rather than a theoretical edge case.

### Recommendation
Backport the relayer-allowlist gate from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` (the `_relayer` storage slot, `setRelayer`/`_setRelayer`, and the `_checkRelayer` call at the top of `onAccept`/`onGetResponse`) into `evm/tron/contracts/apps/IntentGatewayV2.sol`, and audit all other per-chain forks of shared app contracts (Tron, and any other bespoke chain implementations) for the same kind of security-patch drift.

### Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` on Tron as governance does, with an order placed and escrowed cross-chain per the normal `placeOrder`/`fillOrder` flow.
2. An attacker (not the governance relayer) independently assembles a valid `PostRequestMessage` proof for the `RedeemEscrow`/`RefundEscrow` request (using publicly available consensus/state proofs, exactly as the SDK's self-relay tooling would) and calls `HandlerV2.handlePostRequests` directly, which is permissionless.
3. `EvmHost.dispatchIncoming` forwards `msg.sender` (the attacker) as `incoming.relayer` and calls `IntentGatewayV2.onAccept`.
4. `onAccept` only checks `onlyHost` and `authenticate(incoming.request)` (source/from validation) — since there is no `_checkRelayer`, the attacker's delivery proceeds to `withdraw(...)`, releasing escrow funds, even though the account is not the relayer designated by governance for that deployment (contrast with `testOnAcceptRejectsUnlistedRelayer` in `evm/tests/foundry/IntentGatewayV2Test.sol`, which shows this exact call is expected to revert on the canonical EVM contract).

Note: I could not independently confirm from the index whether Tron's `IntentGatewayV2` is currently deployed/live in production or is a work-in-progress fork; this should be verified before treating this as an active exploitable instance versus a pre-deployment gap.

### Citations

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L325-337)
```text
     *   still `msg.sender`, so the host-only functions (`upgradeToAndCall`, `setRelayer`) are
     *   reachable. Reverts bubble up unchanged. Only Hyperbridge may dispatch this request.
     *
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

**File:** sdk/packages/core/docs/ai/decisions/2026-09-05-gateway-setrelayer-is-host-only-and-the-only-writer-unset-means.md (L1-15)
```markdown
# 2026-09-05 — Gateway `setRelayer` is host-only and the only writer; unset means open

Chosen: `setRelayer` lives in `ExtrinsicIntents` behind `onlyHost`, `initialize` does not touch the
relayer, and `_checkRelayer` passes every delivery while `_relayer` is zero. This supersedes the
2026-09-03 decision below that zero fails closed.

The owner branch existed so a fresh proxy could be armed locally; it also let the owner key
redirect every cross-chain delivery without a governance message. Removing it leaves the host as
the only caller, reachable solely from `UpgradeContract` migration calldata. Carrying the relayer
in the init data was tried and rejected: the relayer is operational state that governance owns,
not part of what fixes a proxy's address. With no local or init-time arming left, the message that
arms a fresh proxy is a governance delivery, so the unarmed proxy has to accept it; an unset
relayer therefore gates nothing, and `setRelayer(address(0))` reopens the gate. The window is the
one between deployment and the `upgrade_gateway` that arms it, and closing it is governance's
first act on a new chain.
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L623-636)
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

```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** docs/content/developers/evm/api/ihandler.mdx (L85-118)
```text
### handlePostRequests()

Processes and delivers POST requests to destination applications.

```solidity lineNumbers
function handlePostRequests(
    IHost host,
    PostRequestMessage calldata request
) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `IHost` | The IHost contract |
| `request` | `PostRequestMessage` | Struct containing proof and requests |

**Access:** Permissionless (can be called by anyone)

**Process:**
1. Verifies state proof against stored commitment
2. For each request:
   - Validates destination matches this chain
   - Checks request hasn't timed out
   - Checks for duplicate delivery
   - Dispatches to destination application
   - Stores request receipt with relayer address

**Reverts:**
- `InvalidMessageDestination()` - Request not for this chain
- `MessageTimedOut()` - Request exceeded timeout
- `DuplicateMessage()` - Request already delivered
- `InvalidProof()` - State proof verification failed
- `HostFrozen()` - Host is frozen

```
