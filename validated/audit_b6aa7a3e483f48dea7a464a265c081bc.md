### Title
Orb-Relay client answers `RequestState` from any sender without validating session binding, allowing cross-signup state disclosure - ([File: orb-relay-client/src/client.rs])

### Summary
The `orb-relay-client`'s connection loop enforces a sender-identity check (`src.id != self.config.dst_id`) for every incoming relay message *except* one: `self_serve::app::v1::RequestState`. For that message type, the client immediately replays its last sent message to the sender without checking that the sender actually is the bound counterparty (`dst_id`) for the current signup session. This mirrors the reported Primitive `Option.exercise` flaw, where a privileged callback (`primitiveFlash`) was invoked without verifying that the caller was the legitimate, expected party — allowing anyone to trigger the action on a victim's behalf.

### Finding Description
In the client's connection event loop: [1](#0-0) 

incoming `RelayPayload`s are branched as follows:
1. If the payload matches `self_serve::app::v1::RequestState`, the client immediately sends back `self.last_message.clone()` — **with no check that `src.id == self.config.dst_id`**.
2. Otherwise, if `src.id != self.config.dst_id`, the message is dropped and logged as "unexpected source".
3. Otherwise, the message is buffered normally via `handle_message`.

The `src.id == dst_id` check is the only place in this client where the identity of the remote party (the specific App/Orb pair bound to a given `session_id`/`orb_id`) is verified. Every other message type is protected by it, but `RequestState` explicitly bypasses it. This means any entity that can authenticate to the relay backend as an "App" (or "Orb", since both use the same `Client` and same `main_loop`) can craft a `RequestState` message with an arbitrary `src` and receive a reflection of `self.last_message` — which holds the most recently sent payload for that specific Orb/App session, e.g. `AnnounceOrbId`, `CaptureStarted`, `SignupEnded`, or state used to drive the self-serve signup flow.

This is architecturally identical to the reported bug class: a function/handler that performs a sensitive action (replying with internal state / triggering a flow) trusts that the request came from the intended, bound counterparty, but fails to verify the caller's identity for that specific code path, even though identity checks exist and are enforced elsewhere in the same function. [2](#0-1) 
The `wait_for_msg`/`check_for_msg` primitives built on top of `get_buffered_messages` (used by `proceed_with_biometric_capture` in `src/plans/mod.rs` to gate the self-serve signup flow) trust that anything sitting in the message buffer already passed the identity check — an assumption broken by the `RequestState` fast path, which populates the same session's outgoing channel but not necessarily the buffer, though it does directly leak `last_message` to an unverified sender.

### Impact Explanation
An unprivileged attacker who can obtain any valid App-role relay credential (or otherwise reach the relay endpoint) can request and receive whatever the Orb (or App) most recently sent for a target signup session — such as signup lifecycle messages, capture-trigger acknowledgments, or self-serve state — without being the actual bound counterparty for that `orb_id`/`session_id` pair. This is a cross-signup state disclosure / misattribution: state intended only for the legitimate paired app can be replayed to a third party, undermining the session-binding guarantee that the rest of the code relies on to keep concurrent signups isolated.

### Likelihood Explanation
Exploitability depends only on the ability to open a relay connection with the `App` (or `Orb`) role and knowledge/guessability of a target `orb_id`/`session_id` — no cryptographic bypass is required because the `RequestState` handling path in `client.rs` unconditionally skips the `src.id == dst_id` check that guards all other traffic. Given that self-serve signup flows explicitly rely on this relay channel to gate biometric capture (`proceed_with_biometric_capture` in `src/plans/mod.rs`), the likelihood of this being reachable in production self-serve deployments is high.

### Recommendation
Apply the same `src.id == self.config.dst_id` (session-binding) check to `RequestState` handling before replying with `self.last_message`, so that only the legitimate, bound counterparty for the current session can request state reflection. If replaying state to an unauthenticated/unbound party is an intentional feature (e.g., for reconnect-recovery), document this explicitly and restrict the replayed payload to non-sensitive data, or require an additional session-specific credential/nonce to authorize the replay.

### Proof of Concept
1. Orb and its legitimate App connect via `orb-relay-client` with a given `orb_id`/`session_id`, and the Orb sends state (e.g. `AnnounceOrbId`, `CaptureStarted`) which becomes `self.last_message` on the Orb-side client.
2. A second, unrelated `App`-role client connects to the relay backend with attacker-controlled credentials but crafts/sends a `self_serve::app::v1::RequestState` payload with `src` set to an arbitrary or spoofed entity id (not matching the legitimate app bound to that session).
3. Per `orb-relay-client/src/client.rs:436-440`, the Orb-side client replies with `self.last_message` regardless of the sender's identity, leaking the target session's most recent state to the attacker — without ever hitting the `src.id != self.config.dst_id` rejection path that protects all other message types.

### Citations

**File:** orb-relay-client/src/client.rs (L260-274)
```rust
    pub async fn wait_for_msg<T: PayloadMatcher>(&self, wait: Duration) -> Result<T::Output> {
        let start_time = tokio::time::Instant::now();
        loop {
            if let Some(payload) = self.check_for_msg::<T>().await {
                return Ok(payload);
            }
            if start_time.elapsed() >= wait {
                return Err(eyre::eyre!(
                    "Timeout waiting for payload of type {:?}",
                    std::any::type_name::<T>()
                ));
            }
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
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
