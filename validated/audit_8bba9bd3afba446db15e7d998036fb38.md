### Title
Missing source-authentication check on `RequestState` allows any peer to trigger a repeated resend of the last relay message - (File: `orb-relay-client/src/client.rs`)

### Summary
In `PollerAgent::main_loop`, incoming relay payloads are normally validated against `self.config.dst_id` before being accepted (`else if src.id != self.config.dst_id`). However, the branch that handles `self_serve::app::v1::RequestState` is checked *before* that source-identity validation and unconditionally replies with `self.last_message.clone()`, regardless of who sent the `RequestState` message. [1](#0-0) 

### Finding Description
The relay session between the Orb and the companion App is intended to be a 1:1, authenticated channel scoped by `src_id`/`dst_id` (`Config`) and gRPC token/ZKP auth performed at `connect()`. Every other payload type is gated by the `src.id != self.config.dst_id` check, which drops messages that do not originate from the expected peer. But the `RequestState` handling is special-cased and executed unconditionally before this check:

```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    ...
}
``` [2](#0-1) 

Because the relay backend multiplexes messages by orb/session id and this code path never checks `src.id` for `RequestState`, any entity able to route a `RequestState` payload to this session (whether a malfunctioning/malicious peer connected under the same session, or a misrouted/duplicated message) can repeatedly force the poller to resend `self.last_message` — the most recent state message such as `SignupEnded`, `CaptureEnded`, or `CaptureStarted` — without needing to be re-validated as the legitimate destination peer. This mirrors the `XChainController::sendFundsToVault` root cause: an operation intended to be gated on a specific expected state/counterparty is instead callable idempotently and without ownership/authorization checks, letting an unprivileged caller repeatedly re-trigger a state-transition side effect (in this case, re-emitting signup/session state to a session) purely because the guard was omitted for that one message type.

### Impact Explanation
The impact is bounded to state confusion within the self-serve signup relay flow: repeated forced resends of `last_message` (e.g. `SignupEnded`) could cause the App-side or Orb-side self-serve state machine to receive spurious/duplicate signup lifecycle events out of the expected sequence, potentially causing a UI/state desync analogous to the vault being left in an inconsistent, un-progressable state described in the source report. This is not an information-disclosure or biometric-data leak by itself (it only resends what was already sent to that same channel), but it does violate the intended trust boundary between the relay poller's internal source-authentication gate and message handling, which the source report explicitly flags as the root-cause pattern (guard omitted, allowing repeated/unauthorized triggering of a state action).

### Likelihood Explanation
Likelihood is moderate: exploitation requires the ability to inject a `RequestState` payload attributed to the session (e.g., a compromised/duplicated App-role client, or abuse of the relay routing), which is a more constrained precondition than the fully open, ungated `sendFundsToVault` call in the original report. It is not achievable by a fully external, unauthenticated party without at least session-level access, but the check bypass itself is unconditional and requires no state precondition to trigger repeatedly.

### Recommendation
Move the `src.id != self.config.dst_id` validation ahead of the `RequestState` handling so that the source-identity check applies uniformly to all inbound payload types, including `RequestState`:

```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}: {payload:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else {
    self.handle_message(...).await?;
}
```

### Proof of Concept
Not independently verifiable from static analysis alone — a full PoC would require driving the `orb-relay` backend/session-routing to attribute a `RequestState` payload to an unexpected `src.id` within an active Orb↔App session and observing that `last_message` is resent despite the identity mismatch, since the current code performs no such check for this message type. This is noted as unverified/uncertain due to lack of access to the relay server-side routing behavior within this index.

### Citations

**File:** orb-relay-client/src/client.rs (L425-452)
```rust
                message = response_stream.next() => {
                    match message {
                        Some(Ok(RelayConnectResponse {
                            msg:
                                Some(relay_connect_response::Msg::Payload(RelayPayload {
                                    src: Some(src),
                                    dst,
                                    seq,
                                    payload: Some(payload),
                                })),
                        })) => {
                            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                                sender_tx
                                    .send(self.last_message.clone())
                                    .await
                                    .wrap_err("Failed to send outgoing message")?;
                            } else if src.id != self.config.dst_id {
                                tracing::error!(
                                    "Skipping received message from unexpected source: {:?}: {payload:?}",
                                    src.id
                                );
                            } else {
                                self.handle_message(
                                    RelayPayload { src: Some(src), dst, seq, payload: Some(payload) },
                                    message_buffer,
                                )
                                .await?;
                            }
```
