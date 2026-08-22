Found a concrete analog. The client message-processing loop enforces a peer-identity check (`src.id != self.config.dst_id`) for every incoming relay message *except* one specific message type (`self_serve::app::v1::RequestState`), which is dispatched before that check and unconditionally trusted — mirroring the zkSync root cause where one privileged operation is properly gated on one path (`isSystemCall`/tx-type check) but an alternate path skips the very same gate.

### Title
Trust-boundary check on relay peer identity is bypassed for `RequestState` messages, allowing unauthenticated resync of last session state - (File: `orb-relay-client/src/client.rs`)

### Summary
`PollerAgent::main_loop` validates every incoming relay payload against the expected paired peer (`src.id != self.config.dst_id`) before it is queued for handling. This is the sole trust-boundary check the client performs on inbound IPC messages, since authentication/session pairing itself is delegated to the relay server. However, the `RequestState` message type is special-cased and dispatched *before* this check is evaluated, so it is processed regardless of whose `src` the relay attaches to it.

### Finding Description
In the `main_loop` `select!` arm handling `relay_connect_response::Msg::Payload`, the code is: [1](#0-0) 

The order of checks is: (1) if the payload matches `self_serve::app::v1::RequestState`, immediately resend `self.last_message` with no identity check at all; (2) else, only if `src.id != self.config.dst_id` fails, the message is dropped; (3) otherwise it's queued via `handle_message`. Every other message type funnels through the `src.id == self.config.dst_id` gate, but `RequestState` structurally cannot ever be rejected by that gate because it returns before reaching it.

This is the same bug class as the zkSync finding: a security-relevant flag/check (`isSystemCall` there, `src.id == dst_id` here) is correctly enforced on the "normal" code path but a differently-typed message/transaction reaches privileged behavior through a branch that was never intended to carry that exemption. In zkSync the alternate path was an L1 priority transaction; here it is the `RequestState` payload type, which takes an early-return branch that structurally cannot be reached by the identity check below it.

### Impact Explanation
Whichever entity (orb or app) is on the receiving end of this client will resend its `last_message` — the most recently sent outbound payload for that session/relay pair, e.g. `AnnounceOrbId`, `SignupEnded`, `StartCapture`, or other `self_serve` session-state payloads used to drive signup flow — to *any* sender of a `RequestState` payload that the relay delivers to this stream, without this client verifying that sender is the actual paired counterparty (`dst_id`). This can cause cross-session/cross-signup state bleed: a party that is not the legitimate paired peer of this session can force replay of the last state message, potentially leaking signup progress/state information (e.g. `SignupEnded` outcome) intended only for the paired app/orb. Because `RequestState` handling is entirely exempt from the client's peer check, this is a concrete violation of the sole authorization boundary the client enforces on inbound messages — analogous to permanently/incorrectly bypassing the one gating check meant to prevent unauthorized privileged effects.

### Likelihood Explanation
No special privilege is required beyond being able to get a `RequestState`-shaped payload routed to the victim client's stream — which is the exact same delivery path used by every other (properly checked) message type in this loop. Any code path or actor capable of causing the relay to deliver a message to this client (the same precondition every other message already assumes as attacker-reachable, per the `src.id` check existing at all) can exploit this branch trivially by using the `RequestState` payload type instead. This requires no cryptographic break, no node/operator privilege, and no hardware access — only the ability to have a `RequestState` message routed into the stream, exactly analogous to the "arbitrary" alternate transaction path in the zkSync report.

### Recommendation
Move the `src.id != self.config.dst_id` check to the top of this match arm so it applies uniformly to all payload types, including `RequestState`, before any type-specific dispatch (including the state-resync short-circuit) is performed: [2](#0-1) 

Only after confirming `src.id == self.config.dst_id` should the code check whether the payload is a `RequestState` message and, if so, resend `self.last_message`.

### Proof of Concept
1. A client instance (e.g., an orb) connects to the relay expecting a paired peer identified by `config.dst_id`.
2. Any entity able to have a message routed to this orb's relay stream sends a payload matching `self_serve::app::v1::RequestState`, with `src` set to an id different from `config.dst_id`.
3. In `main_loop`, execution reaches `self_serve::app::v1::RequestState::matches(&payload).is_some()` at `orb-relay-client/src/client.rs:436` and evaluates true — before the `src.id != self.config.dst_id` branch at line 441 is ever reached.
4. The orb calls `sender_tx.send(self.last_message.clone())` at lines 437-440, resending the last state payload (e.g., last `SignupEnded`/`AnnounceOrbId`) without ever validating that the requester is the legitimate paired peer.

### Citations

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
