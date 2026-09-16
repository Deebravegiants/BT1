Confirmed: the Tron `IntentGatewayV2` contract has no `_relayer` state, no `_checkRelayer` function, and no `setRelayer` — the relayer-gate mechanism that exists on the canonical EVM `ExtrinsicIntents.sol` is entirely absent from the Tron port. This is a structural omission, not a conditional bypass of an existing check.

### Title
Missing relayer-gate check on Tron `IntentGatewayV2.onAccept` allows unauthorized escrow redemption/refund - (File: evm/tron/contracts/apps/IntentGatewayV2.sol)

### Summary
The EVM reference implementation of the Intent Gateway (`ExtrinsicIntents.sol`) enforces a relayer allowlist on every incoming ISMP delivery before any request body is interpreted. The Tron port of the same contract (`IntentGatewayV2.sol`), which implements the identical `onAccept` dispatch entry point and the identical `RequestKind` action set (including `RedeemEscrow`/`RefundEscrow`), omits this check entirely.

### Finding Description
On the canonical EVM implementation, `onAccept` runs `_checkRelayer(incoming.relayer)` unconditionally as the very first statement, before the `RequestKind` byte is even read: [1](#0-0) 

The Tron `IntentGatewayV2.onAccept` implements the same message-kind dispatch (`RedeemEscrow`, `RefundEscrow`, `NewDeployment`, `UpdateParams`, `SweepDust`) but has no equivalent gate — it goes straight from `onlyHost` to decoding `RequestKind` and calling `authenticate(incoming.request)`/`withdraw(...)`: [2](#0-1) 

A grep of the file confirms there is no `_checkRelayer`, `_relayer` state variable, or `setRelayer` function anywhere in the Tron contract — the relayer-gate primitive documented as part of the delivery-integrity model simply does not exist there. This is architecturally the same bug class as CVE-2026-82474: a security policy (here, "only the designated relayer's delivery of a cross-chain message may be trusted enough to decode and act on") is enforced on one code path (`ExtrinsicIntents.onAccept` on EVM chains) but not on a second, functionally equivalent entry point that reaches the identical privileged operation (`IntentGatewayV2.onAccept` on Tron) — exactly as sudo's intercept policy covered `execve` but not the equivalent `execveat`/`fexecve` entry point.

The relayer gate exists specifically because `EvmHost.dispatchIncoming` reports whatever `relayer` address the handler (`_hostParams.handler`) passes it, and a forged/malicious handler swap could report an arbitrary address as `incoming.relayer`: [3](#0-2) 
On Tron, that same untrusted `incoming.relayer` field is accepted with no allowlist check, so any address the handler names is treated as the authorized deliverer.

### Impact Explanation
`RedeemEscrow`/`RefundEscrow` deliveries drive `withdraw(...)`, which releases escrowed intent tokens to a beneficiary derived from the request body: [4](#0-3) 
Without the relayer gate that the EVM implementation relies on as a defense-in-depth measure against a compromised/malicious handler or a still-unauthenticated authentication path, any actor who can get `onAccept` invoked with a favorable `relayer` value skips a layer of the delivery-integrity model the rest of the protocol assumes is uniformly present. Given the "in-scope" impact bar (unauthorized app action / theft of escrowed funds), this is a Medium-to-High severity gap: it does not by itself forge an ISMP proof, but it removes a check other Hyperbridge apps rely on to fail closed against a compromised handler or misreported relayer, widening the blast radius of any handler-level compromise specifically on Tron deployments.

### Likelihood Explanation
Exploitation requires the handler-swap or relayer-misreport precondition described in the referenced flow doc (i.e., a compromised/forged `_hostParams.handler`), which the EVM host itself defends against via the `HostManager` governance gate. The vulnerability here is that the Tron app-layer omits the second line of defense present on EVM, so if that precondition is ever met on a Tron deployment, there is no additional obstacle — whereas on EVM there is. This makes it a lower-likelihood-but-nonzero defense-in-depth gap rather than a directly, unconditionally exploitable bug from a single transaction today.

### Recommendation
Port the `_relayer` state, `_checkRelayer`, and `setRelayer` mechanism from `evm/src/apps/intentsv2/ExtrinsicIntents.sol` into `evm/tron/contracts/apps/IntentGatewayV2.sol`, and call `_checkRelayer(incoming.relayer)` unconditionally at the top of `onAccept`, mirroring the EVM contract exactly so both deployments enforce the identical delivery-integrity policy.

### Proof of Concept
1. Assume the Tron host's registered handler misreports `incoming.relayer` for a delivered `PostRequest` (e.g., through a handler bug or compromise, as covered generically by the flow doc referenced above).
2. The forged/mis-attributed request carries `RequestKind.RedeemEscrow` with a `WithdrawalRequest` body naming an attacker-controlled beneficiary.
3. `IntentGatewayV2.onAccept` on Tron calls `authenticate(incoming.request)` and `withdraw(...)` without ever checking `incoming.relayer` against an allowlist — unlike `ExtrinsicIntents.onAccept` on EVM, which would revert with `Unauthorized` at `_checkRelayer` before this point.
4. Escrowed tokens are released to the attacker-controlled beneficiary on the Tron deployment, where the equivalent EVM deployment would have refused the same delivery.

Note: I could not fully verify whether `authenticate(incoming.request)` in the Tron contract performs an independent source/gateway check equivalent enough to fully compensate for the missing relayer gate — the index did not surface its full body. If a Devin session confirms `authenticate` provides equivalent protection, this finding should be downgraded accordingly.

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

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L691-700)
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
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L7-21)
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

So a delivery from anyone but the authorised relayer never decodes the body, never runs
`_authenticate`, and leaves no receipt. The authorised relayer submitting the same message later
takes the normal path. A gateway whose `_relayer` is zero accepts every relayer: that is the state
```
