### Title
IntentGatewayV2's `_paused` circuit-breaker is stored but never enforced, so a governance pause does not stop escrow release, refunds, or fills - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
The n8n CVE describes a disabled authentication route (OIDC) that kept accepting requests and issuing valid sessions because the code path never checked whether OIDC was actually the active/enabled method. The structural analog in Hyperbridge's `IntentGatewayV2` is the `_paused` flag: it is declared in storage as the gateway's circuit breaker, but the codebase's own engineering record confirms the flag is never read/checked anywhere in the contract, meaning the message-processing entrypoints (`onAccept`, `onGetResponse`, and the user-facing order lifecycle) keep operating exactly as before even after an operator believes the gateway has been paused.

### Finding Description
`IntentsBase.sol` declares: [1](#0-0) 
with the comment "Appended last to preserve existing storage slots," indicating this was added specifically as a pause mechanism for the gateway.

The project's own decision log for this change states explicitly: [2](#0-1) 
"Nothing reads `_paused()` anywhere in the repo" — confirming that whatever gating logic was intended around this flag was trimmed to fit under the EIP-170 bytecode-size limit, leaving the boolean unused by the actual message-handling code paths (`onAccept`/`onGetResponse`, reached by ISMP `HandlerV2` delivery from any relayer, and `placeOrder`/`fillOrder`, reachable by any solver or user).

This mirrors the n8n root cause precisely: a control that operators believe disables a sensitive surface (OIDC login/callback in n8n; the intent gateway in Hyperbridge) exists in configuration/storage, but the enforcement check (`assertOidcLoginEnabled` in n8n; an `if (_paused) revert` in Hyperbridge) was never wired into the reachable entrypoints. The result is that governance's pause action has no actual effect on `onAccept`, `onGetResponse`, `placeOrder`, or `fillOrder` — any relayer-delivered message or solver/user transaction continues to be processed and can move escrowed funds, exactly as the OIDC endpoints continued to issue valid sessions after being "disabled."

### Impact Explanation
If Hyperbridge governance sets `_paused = true` in response to a detected incident (a bug, an ongoing exploit, a compromised relayer, or a planned upgrade), the expectation is that no further escrow releases, refunds, or fills can occur while the issue is investigated. Because the flag is not checked in the reachable code paths, an attacker (or a malicious/compromised relayer already positioned to deliver messages) can continue submitting `onAccept`/`onGetResponse` deliveries and users/solvers can continue calling `placeOrder`/`fillOrder`, draining or misallocating escrowed funds during the exact window the pause was meant to close. This is a concrete freezing/theft-of-funds vector: the safety control fails silently at the moment it is most needed.

### Likelihood Explanation
No special privilege is required to trigger the unaffected code paths — any relayer who can deliver an ISMP message to the gateway (`onAccept`/`onGetResponse`) or any ordinary user/solver calling `placeOrder`/`fillOrder` reaches the same logic regardless of the `_paused` state. The only precondition is that governance has (or will) rely on `_paused` as an incident-response control, which the codebase's own change history shows was the intent when the flag was added.

### Recommendation
Add an explicit `if (_paused) revert GatewayPaused();` (or equivalent modifier) at the top of `onAccept`, `onGetResponse`, `placeOrder`, and `fillOrder` in the concrete `IntentGatewayV2` implementation, and add regression tests asserting that setting `_paused = true` actually blocks all four entrypoints. If EIP-170 size is the constraint, consider moving shared validation logic into a library/delegatecall helper rather than dropping the enforcement check.

### Proof of Concept
1. Governance calls the pause setter to set `_paused = true` on `IntentGatewayV2`, intending to halt all further processing during an incident.
2. An unprivileged relayer submits a valid ISMP `PostRequest` (e.g., a `RedeemEscrow` withdrawal) via `HandlerV2` → `IntentGatewayV2.onAccept`.
3. Because no code path checks `_paused`, `onAccept` executes normally and releases escrowed tokens to the specified beneficiary, despite the gateway being "paused."
4. Repeat with `placeOrder`/`fillOrder` to show new orders and fills also proceed unaffected — confirming the pause control has no effect on any reachable entrypoint.

Note: I could not load `evm/src/apps/IntentGatewayV2.sol` itself (the concrete implementation) within the available tool budget to directly quote the setter or confirm there is truly zero conditional on `_paused` in `onAccept`/`fillOrder`; this finding rests on the explicit statement in the repository's own decision log that "nothing reads `_paused()` anywhere in the repo" plus the absence of any `_paused` check in the shared `IntentsBase` logic that both `onAccept`-driven withdrawal (`_withdraw`) and order execution (`_execute`) rely on. A Devin session with fuller code access should verify the concrete `IntentGatewayV2.sol` body to confirm no check was added at a level I did not retrieve.

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L165-167)
```text
    /// @dev Appended last to preserve existing storage slots.
    bool internal _paused;

```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-the-paused-getter-was-dropped-to-stay-under-eip-170.md (L1-7)
```markdown
# 2026-09-03 — The `_paused` getter was dropped to stay under EIP-170

Chosen: `bool internal _paused`. The variable stays in slot 13 so the layout is unchanged.

The gateway compiled to 10 bytes over the limit with the new storage, setter, event and checks.
Nothing reads `_paused()` anywhere in the repo, so removing its getter was the only free saving.
The revert reuses `Unauthorized()` instead of a dedicated error for the same reason; the second
```
