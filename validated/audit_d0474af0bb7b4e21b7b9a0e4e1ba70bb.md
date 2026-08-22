### Title
Stale pending messages are replayed across relay reconnects without being cleared, allowing cross-session control-message bleed - ([File: orb-relay-client/src/client.rs])

### Summary
`PollerAgent::pending_messages` (a `BTreeMap<u64, (RelayConnectRequest, Option<oneshot::Sender<()>>)>`) is created once per `Client::connect()` call and is never cleared when the connection is torn down and re-established, whether via `Command::Reconnect`, a stream error, or a failed `ConnectResponse`. Every reconnect path calls `replay_pending_messages`, unconditionally resending everything still queued from the prior connection/session.

### Finding Description
`Client::connect()` spawns a task that creates a single `PollerAgent` with `pending_messages: Default::default()` and then loops calling `agent.main_loop(...)` repeatedly on any error or on `shutdown_token` not being cancelled: [1](#0-0) 

Because `agent` (and therefore `pending_messages`) is created *outside* this reconnect loop, it survives every reconnection triggered by:
- `Command::Reconnect`, which simply `return Ok(())`s from `main_loop`, causing the outer loop to reconnect and immediately call `self.replay_pending_messages(&sender_tx)` again: [2](#0-1) [3](#0-2) 
- A transport-level stream error (e.g., malformed frames) or a `ConnectResponse{success:false}` returned by `wait_for_connect_response`, both of which propagate an `Err` out of `main_loop`, hit the `tracing::error!` branch, and loop back to reconnect+replay: [4](#0-3) [5](#0-4) 

`replay_pending_messages` resends every entry in the map verbatim, regardless of how old or contextually stale it is: [6](#0-5) 

Nothing in `Client` or `PollerAgent` clears `pending_messages` based on session/signup boundaries — there is no API such as `reset()`/`clear_pending()` exposed on `Client`, and `graceful_shutdown` only sleeps/retries, it does not purge the map before drop: [7](#0-6) 

The orb-side signup flow that owns the relay client, `orb_relay_announce_orb_id`, explicitly calls `relay.reconnect().await?` in its retry loop on failed sends, which is exactly the `Command::Reconnect` path that triggers a bulk replay of anything still queued: [8](#0-7) 

Once this function succeeds, the resulting `Client` (with whatever `pending_messages` accumulated) is stored on the long-lived `Orb` broker state as `orb.orb_relay = Some(relay)`: [9](#0-8) 

I could not fully confirm from the available index whether `do_signup` always tears down and recreates `orb.orb_relay` (calling `orb_relay_announce_orb_id` fresh, which does construct a brand-new `Client`/`PollerAgent`/empty `pending_messages` via `Client::new_as_orb`) on every single signup attempt, or whether the same `Client` can be carried over into a second signup attempt on the same orb session without being dropped/recreated. This is the one open question that determines whether the bleed is strictly intra-connection (already provable) or also crosses `do_signup` invocations.

### Impact Explanation
Regardless of the open question above, the core bug is concretely provable and reachable by an unprivileged attacker who can destabilize the relay connection (malformed frames causing a `Streaming` error, or a backend/self-serve app sending `ConnectResponse{success:false}`): stale queued `RelayPayload`s (e.g. `AnnounceOrbId`, `SignupEnded`, or other self-serve control messages) get resent to whatever session is current at the time of the next successful connect, since the `dst_id`/`src_id` embedded in `RelayPayload` are fixed at `Client` construction and not re-validated against a "current session" concept. Worst case, this causes stale/duplicated control messages (e.g., a stale `SignupEnded{success:true}`) to be delivered into a session that did not generate them, corrupting client-visible signup state without any cryptographic or session-freshness check. This maps to a signup-state integrity / cross-session bleed impact, not to biometric disclosure or signing/attestation forgery.

### Likelihood Explanation
Triggering repeated reconnects is fully within the described unprivileged threat model — an attacker controlling their own signup session or the app-side connection can cause connection instability (bad frames, dropped stream, or a rejected `ConnectResponse`), and the orb's own retry logic (`orb_relay_announce_orb_id`) already calls `reconnect()` on failure, so the replay path is reachable without any special privilege. The intra-connection replay of stale `pending_messages` is deterministic and repeatable. The cross-`do_signup` variant's likelihood depends on the unconfirmed lifecycle of `orb.orb_relay` across signups.

### Recommendation
- Clear `pending_messages` (and reset `seq`/`last_message`) whenever a reconnect is not a pure resume-of-same-logical-session — at minimum, clear it on `Command::Reconnect` triggered by an explicit caller-level session change, and take an explicit "session id" or generation counter that is checked before replay.
- Add a `Client::reset_state()`/equivalent that is called whenever a new signup/session begins, purging any `Client` instance's outgoing/pending buffers before it participates in a new signup, instead of relying on implicit `Client` recreation.
- Bound the replay to messages that are still relevant to the *current* signup/session context, e.g. by tagging pending messages with the session/signup id they belong to and dropping any whose tag doesn't match the active one at replay time.

### Proof of Concept
Integration test in `orb-relay-client`:
1. Start a mock relay server that accepts a connection, then send a `ConnectResponse{success:false}` (or drop the stream) to force `PollerAgent::main_loop` to error out and reconnect.
2. Before the induced failure, use `Client::send_blocking` to queue a message (it lands in `pending_messages` per line 498 of `client.rs`).
3. Assert the mock server observes the message being sent twice — once originally, once via `replay_pending_messages` after the forced reconnect — with `expected assertions`: `pending_messages.len()` (via `Client::has_pending_messages`) is non-zero after the failed round-trip, and the mock server's received-message log shows a duplicate/stale `seq`/payload after reconnect, without an intervening explicit call that logically starts a "new session."
4. Extend the test to call `Client::reconnect()` explicitly (simulating the retry path in `orb_relay_announce_orb_id`) and assert the same stale message reappears on the wire on the new connection, proving no session-boundary reset occurs in `client.rs`.

### Citations

**File:** orb-relay-client/src/client.rs (L218-249)
```rust
        tokio::spawn(async move {
            let mut agent = PollerAgent {
                config: &config,
                pending_messages: Default::default(),
                last_message: no_state,
                seq: 0,
            };
            let mut connection_established_tx = Some(connection_established_tx);

            loop {
                if let Err(e) = agent
                    .main_loop(
                        &message_buffer,
                        shutdown_token.clone(),
                        &mut outgoing_rx,
                        &mut command_rx,
                        connection_established_tx.take(),
                    )
                    .await
                {
                    tracing::error!("Connection error: {e}");
                }

                if shutdown_token.is_cancelled() {
                    tracing::info!("Connection shutdown");
                    break;
                }

                tracing::info!("Reconnecting in {}s ...", config.reconnect_delay.as_secs());
                tokio::time::sleep(config.reconnect_delay).await;
            }
            shutdown_completed_tx.send(()).ok();
```

**File:** orb-relay-client/src/client.rs (L335-365)
```rust
    pub async fn graceful_shutdown(
        &mut self,
        wait_for_pending_messages: Duration,
        wait_for_shutdown: Duration,
    ) {
        // Let's wait for all acks to be received
        if self.has_pending_messages().await.map_or(false, |n| n > 0) {
            tracing::info!(
                "Giving {}ms for pending messages to be acked",
                wait_for_pending_messages.as_millis()
            );
            tokio::time::sleep(wait_for_pending_messages).await;
        }
        // If there are still pending messages, we retry to send them
        if self.has_pending_messages().await.map_or(false, |n| n > 0) {
            tracing::info!("There are still pending messages, replaying...");
            if let Ok(()) = self.replay_pending_messages().await {
                tokio::time::sleep(wait_for_pending_messages).await;
            }
        }

        // Eventually, there not much more we can do, so we shutdown the client
        self.shutdown();

        if let Some(shutdown_completed) = self.shutdown_completed.take() {
            match tokio::time::timeout(wait_for_shutdown, shutdown_completed).await {
                Ok(_) => tracing::info!("Shutdown completed successfully."),
                Err(_) => tracing::warn!("Timed out waiting for shutdown to complete."),
            }
        }
    }
```

**File:** orb-relay-client/src/client.rs (L400-413)
```rust
        let (mut response_stream, sender_tx) = match self.connect().await {
            Ok(ok) => ok,
            Err(e) => {
                shutdown_token.cancel();
                return Err(e);
            }
        };

        if let Some(tx) = connection_established_tx {
            let _ = tx.send(());
        }

        self.replay_pending_messages(&sender_tx).await?;

```

**File:** orb-relay-client/src/client.rs (L510-513)
```rust
                        Command::Reconnect => {
                            tracing::info!("Reconnecting...");
                            return Ok(());
                        }
```

**File:** orb-relay-client/src/client.rs (L527-543)
```rust
    async fn replay_pending_messages(
        &mut self,
        sender_tx: &Sender<RelayConnectRequest>,
    ) -> Result<()> {
        if !self.pending_messages.is_empty() {
            tracing::warn!("Replaying pending messages: {:?}", self.pending_messages);
            for (_key, (msg, sender)) in self.pending_messages.iter_mut() {
                sender_tx.send(msg.clone()).await.wrap_err("Failed to send pending message")?;
                // If there's a sender, send a signal and set it to None. We are coming from a reconnect or a manual
                // retry, so we don't care about the acks.
                if let Some(tx) = sender.take() {
                    let _ = tx.send(());
                }
            }
        }
        Ok(())
    }
```

**File:** orb-relay-client/src/client.rs (L610-631)
```rust
    async fn wait_for_connect_response(
        &self,
        response_stream: &mut Streaming<RelayConnectResponse>,
    ) -> Result<()> {
        while let Some(message) = response_stream.next().await {
            let message = message?.msg.ok_or_eyre("ConnectResponse msg is missing")?;
            if let relay_connect_response::Msg::ConnectResponse(ConnectResponse {
                success,
                error,
                ..
            }) = message
            {
                return if success {
                    tracing::info!("Successful connection");
                    Ok(())
                } else {
                    Err(eyre::eyre!("Failed to establish connection: {error:?}"))
                };
            }
        }
        Err(eyre::eyre!("Connection stream ended before receiving ConnectResponse"))
    }
```

**File:** src/plans/mod.rs (L2127-2164)
```rust
    for _ in 0..reties {
        let now = Instant::now();
        if let Ok(()) = relay
            .send_blocking(
                common::v1::AnnounceOrbId {
                    orb_id: ORB_ID.to_string(),
                    mode_type: if is_self_serve_enabled {
                        common::v1::announce_orb_id::ModeType::SelfServe.into()
                    } else {
                        common::v1::announce_orb_id::ModeType::Legacy.into()
                    },
                    hardware_type: if identification::HARDWARE_VERSION.contains("Diamond") {
                        common::v1::announce_orb_id::HardwareType::Diamond.into()
                    } else {
                        common::v1::announce_orb_id::HardwareType::Pearl.into()
                    },
                },
                timeout,
            )
            .await
        {
            // Happy path. We have successfully announced and acknowledged the OrbId.
            dd_timing!("main.time.orb_relay.announce_orb_id", now);
            orb.orb_relay = if is_self_serve_enabled {
                Some(relay)
            } else {
                relay.graceful_shutdown(wait_for_pending_messages, wait_for_shutdown).await;
                None
            };
            return Ok(());
        }
        dd_incr!("main.count.orb_relay.retry.send.announce_orb_id");
        tracing::error!("Relay: Failed to AnnounceOrbId. Retrying...");
        relay.reconnect().await?;
        if relay.has_pending_messages().await? > 0 {
            sleep(Duration::from_secs(1)).await;
        }
    }
```
