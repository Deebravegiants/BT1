### Title
Faulty Access Control in Orb-Relay Client Allows Any Sender to Trigger State Replay Bypassing Source Validation - (File: `orb-relay-client/src/client.rs`)

### Summary
In the `PollerAgent::main_loop` message-handling branch, incoming relay messages are checked for their source (`src.id != self.config.dst_id`) before being accepted into the client's message buffer. However, this authorization check is only applied in the final `else` branch; a `RequestState` message is unconditionally honored before the source check runs, causing the client to reply with `self.last_message` to any sender, regardless of whether that sender is the paired session counterpart.

### Finding Description
The relay client's core message dispatch logic is: [1](#0-0) 

```rust
message = response_stream.next() => {
    match message {
        Some(Ok(RelayConnectResponse {
            msg: Some(relay_connect_response::Msg::Payload(RelayPayload {
                src: Some(src), dst, seq, payload: Some(payload),
            })),
        })) => {
            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                sender_tx.send(self.last_message.clone()).await...
            } else if src.id != self.config.dst_id {
                tracing::error!("Skipping received message from unexpected source: ...");
            } else {
                self.handle_message(...).await?;
            }
        }
        ...
```

The intended access-control invariant is that only messages whose `src.id` equals the client's configured session counterpart (`self.config.dst_id`) should be processed — this is precisely the check performed in the `else if` arm (`src.id != self.config.dst_id`). This is structurally identical to the reported `Set.sol#claimSetFees` bug: the authorization predicate (`caller_ != owner` in the report, `src.id != self.config.dst_id` here) is written as a condition that is only reached in one branch of an `if/else if/else` chain, while a separate, unauthenticated code path (the report's "anyone specifying themselves as caller" case; here, the `RequestState`-matching branch) bypasses it entirely. Any relay peer — orb or app — that is able to send a message addressed to this client's queue can send a `RequestState` payload and have the client immediately reply with `self.last_message` (the last outgoing session-state message this client sent), without ever being checked against `self.config.dst_id`.

`self.config.dst_id` is the identifier of the paired counterpart for this signup session (session id for an Orb client, orb id for an App client), established at connect time via `new_as_orb`/`new_as_app`/`new_as_app_zkp`: [2](#0-1) 

The `last_message` re-sent on `RequestState` is the most recent outgoing session/state announcement (`AnnounceOrbId`, `SignupEnded`, etc., as seen in the manual test harness), i.e., orb/session state tied to a specific signup: [3](#0-2) 

### Impact Explanation
Because the `RequestState` branch is evaluated before the sender-identity check, any entity that can reach this client's relay inbox (i.e., any other authenticated relay participant, not necessarily the actual session-paired Orb/App) can force it to disclose its most recent session-state payload. This is a cross-session state disclosure: session/orb-identity and signup-state messages intended only for the paired counterpart can be exfiltrated by an unrelated, unauthorized relay peer, which matches the "cross-signup state bleed" impact category. It does not require the attacker to hold any operator/admin privilege — only the ability to act as a normal relay client (an App or another Orb session) is needed, i.e., a no-privilege attacker profile.

### Likelihood Explanation
Exploitability depends on whether the underlying Orb-Relay server enforces strict routing so that only the paired counterpart's messages reach a given client's queue. Nothing in this client code enforces that invariant itself — the `src.id != self.config.dst_id` check exists specifically because the client cannot otherwise trust that only the intended counterpart's messages arrive, which shows the client-side code assumes messages from unintended sources are reachable and must be filtered. The `RequestState` branch defeats exactly this filter, making the bug reachable whenever any other relay-authenticated entity can address a message to this destination queue (e.g., by knowing/guessing the session id or orb id, which are used directly as relay addressing identifiers). This is a logic error in shipped production code and is deterministically triggerable once such a message reaches the stream, with no cryptographic or timing constraints.

### Recommendation
Move the source validation ahead of the `RequestState`-specific handling so that the same authorization check applies uniformly to every payload type, e.g.:

```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}: {payload:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await.wrap_err("Failed to send outgoing message")?;
} else {
    self.handle_message(RelayPayload { src: Some(src), dst, seq, payload: Some(payload) }, message_buffer).await?;
}
```
Add regression tests asserting that a `RequestState` message from an unexpected `src.id` is rejected (mirroring the report's recommendation to add regression tests for the fixed `claimSetFees` check).

### Proof of Concept
1. Client A connects as the legitimate session counterpart (`dst_id` = A) to Client B's relay session; B sends normal session-state traffic, updating `self.last_message` each time.
2. Attacker C, authenticated to the relay backend under its own identity (not A), addresses a `RequestState` payload to B's queue.
3. In `main_loop`, the match on `RelayConnectResponse` payload hits the first branch (`RequestState::matches(&payload).is_some()` is true) before the `src.id != self.config.dst_id` check is ever evaluated.
4. B replies by sending `self.last_message.clone()` back through `sender_tx`, delivering the last session-state message to whichever channel routed C's request — disclosing session state to C despite C not being the paired counterpart `A`.

Note: Full verification that C can address a message directly to B's inbox depends on server-side routing/authorization in the Orb-Relay backend service, which is outside this repository and could not be directly inspected; this finding documents the client-side logic flaw precisely mirroring the reported bug class.

### Citations

**File:** orb-relay-client/src/client.rs (L144-174)
```rust
    /// Create a new client that sends messages from an Orb to an App
    #[must_use]
    pub fn new_as_orb(url: String, token: String, orb_id: String, session_id: String) -> Self {
        Self::new(url, Auth::Token(TokenAuth { token }), orb_id, session_id, Mode::Orb)
    }

    /// Create a new client that sends messages from an App to an Orb
    #[must_use]
    pub fn new_as_app(url: String, token: String, session_id: String, orb_id: String) -> Self {
        Self::new(url, Auth::Token(TokenAuth { token }), session_id, orb_id, Mode::App)
    }

    /// Create a new client that sends messages from an App to an Orb (using ZKP as auth method)
    #[must_use]
    pub fn new_as_app_zkp(
        url: String,
        root: String,
        signal: String,
        nullifier_hash: String,
        proof: String,
        session_id: String,
        orb_id: String,
    ) -> Self {
        Self::new(
            url,
            Auth::ZKP(ZkpAuth { root, signal, nullifier_hash, proof }),
            session_id,
            orb_id,
            Mode::App,
        )
    }
```

**File:** orb-relay-client/src/client.rs (L425-453)
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
                        }
```

**File:** orb-relay-client/src/bin/manual-test.rs (L292-294)
```rust
    let now = Instant::now();
    app_client.send(self_serve::app::v1::RequestState {}).await?;
    tracing::info!("Time took to send RequestState from the app: {}ms", now.elapsed().as_millis());
```
