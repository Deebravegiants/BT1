## Analog Found

### Title
Signup state cleanup skipped on early return via `?` in `MasterPlan::run` — inconsistent signup "stack" analogous to the FA-withdrawal bug ([File: src/plans/mod.rs])

### Summary
The reported Tezos bug describes a pattern where an "enter" call (`begin_inter_transaction`) is followed by fallible sub-calls using `?`, so that any error skips the matching "exit" cleanup (`end_inter_transaction`), leaving the transaction stack inconsistent. `orb-core`'s top-level signup state machine, `MasterPlan::run`, has the exact same shape: it "enters" a signup by setting a shared flag and activating hardware/agents/relay, then calls `do_signup` with `?`. If `do_signup` returns `Err`, every corresponding "exit"/cleanup step is skipped.

### Finding Description
In `MasterPlan::run`, the signup lifecycle is bracketed like a transaction: [1](#0-0) 

```
dd_incr!("main.count.signup.during.general.signup_started");
self.signup_flag.store(true, Ordering::Relaxed);
let signup_result = Box::pin(self.do_signup(orb, qr_codes, dbus.as_ref())).await?;   // <-- '?' here
let success = signup_result.success;
Box::pin(self.after_signup(orb, signup_result)).await?;
self.signup_flag.store(false, Ordering::Relaxed);

orb.disable_image_notary();
...
orb.orb_relay = None;
self.reset_hardware_except_led(orb).await?;
if let Some(dbus_ctx) = dbus.as_ref() {
    dbus::Signup::signup_finished(dbus_ctx, success).await?;
}
```

`self.signup_flag.store(true, ...)` marks "enter signup" — this is the analog of `begin_inter_transaction`. `do_signup` internally performs many fallible operations (network calls, agent IPC, relay announce, etc.) and itself uses `?` extensively, e.g. inside its own body: [2](#0-1) 

If any of these fail, the error propagates with `?` all the way out of `do_signup` and then, because of the `?` on line 368, out of `MasterPlan::run` itself — **before** any of the "exit" steps run:
- `self.signup_flag.store(false, ...)` is never reached, so the flag stays `true`.
- `orb.disable_image_notary()` is never called, so the image-notary agent (which holds an active `signup_id` and buffered biometric frames/log) is never told to finalize: [3](#0-2) [4](#0-3) 

- The `orb_relay` connection (tied to the real `user_id`/session from the scanned QR codes) is never gracefully shut down and `orb.orb_relay` is never reset to `None`.
- `reset_hardware_except_led` is skipped, leaving IR/RGB cameras, liquid lens, mirror, etc. in a signup-active configuration.
- `dbus::Signup::signup_finished` is never emitted, so downstream consumers of the D-Bus `Signup` interface never learn the signup ended: [5](#0-4) 

The shared `signup_flag` is also read by the separate `Observer` broker task to choose a battery-shutdown voltage threshold: [6](#0-5) 

If `signup_flag` is stuck `true` (because the "exit" path was skipped), the Observer will keep using the lower `SIGNUP` battery-shutdown threshold indefinitely instead of the higher `IDLE` threshold intended for the idle state, since `signup_flag` is a long-lived `Arc<AtomicBool>` shared across the whole process lifetime, independent of whether `MasterPlan::run` itself keeps looping or the top-level error causes `run()` in `src/bin/orb-core.rs` to return.

This mirrors the report's root cause precisely: an "enter" operation paired with a "?"-guarded fallible body and an "exit"/cleanup operation that is only reached on the success path.

### Impact Explanation
Because the "exit" cleanup is skipped:
- The image-notary agent's `FinalizeSignup`/cleanup for the just-attempted signup is never issued, so captured biometric artifacts (IR/RGB frames, identification images tied to a real `signup_id`) for that aborted signup are not finalized/removed as intended by the normal happy-path flow — a retention-lifecycle inconsistency for biometric data.
- The `signup_flag` used by the independent `Observer` broker can remain permanently in the "signup" state, changing safety-relevant battery-shutdown behavior for the remainder of the process's life.
- The orb-relay session associated with a specific user/session id is left connected/un-shut-down rather than being gracefully torn down, and `orb.orb_relay` is not cleared, so residual session state can bleed into how the next loop iteration (if reached) treats relay state — a state-bleed concern between signup attempts.
- No `signup_finished` signal is emitted, so any component (backend supervisor, UI state listener) relying on that D-Bus signal to know a signup concluded will not be informed, which can desynchronize actual device state from what other subsystems believe.

This is rated similarly to the original "Medium" severity: it is not a directly exploitable authorization bypass by itself, but it produces an inconsistent internal state machine after any transient error (network hiccup, agent IPC failure, relay failure) during a signup, with impact spanning device safety behavior (battery-based shutdown threshold), biometric data lifecycle, and stale session/relay state.

### Likelihood Explanation
`do_signup` contains numerous `?`-propagated fallible operations (D-Bus calls, agent port sends, relay `send_blocking`/`connect`, config locks, data uploader queue waits). Any one of these failing during a real, unprivileged, in-field signup attempt (e.g., a flaky network condition or an agent hiccup) is sufficient to trigger the skipped-cleanup path — this does not require a malicious actor, only an ordinary error condition during a normal signup, making it reasonably likely to occur in production over time.

### Recommendation
Do not use `?` directly on `do_signup(...).await` inside the "entered" signup region. Either:
1. Wrap the entered-signup body (from `signup_flag.store(true, ...)` to the cleanup at the bottom of the loop) in a `catch`/helper `async fn` and always run the cleanup (`after_signup`, `disable_image_notary`, `reset_hardware_except_led`, clearing `orb_relay`, resetting `signup_flag`, emitting `signup_finished`) regardless of `Ok`/`Err`, similar to a `finally` block, e.g. by capturing the result and unconditionally executing the teardown before propagating/handling the error; or
2. Use an RAII guard (a struct whose `Drop` resets `signup_flag` and clears `orb.orb_relay`) so that clean-up cannot be skipped even if control flow exits abnormally through `?`.

### Proof of Concept
Because this is a live-hardware-driven state machine, a runnable PoC isn't directly executable here, but the fault-injection PoC is straightforward to construct: inject a transient failure into any of the fallible calls performed by `do_signup` (e.g., force `orb_relay_announce_orb_id` or one of the `port.send(...).await?` calls inside `do_signup`/its callees to return `Err`) during an in-progress signup. Observe that:
1. `self.signup_flag` remains `true` after `MasterPlan::run`'s call to `do_signup` fails, verified by reading the shared `Arc<AtomicBool>` from the `Observer` broker.
2. `dbus::Signup::signup_finished` is never emitted for that attempt (no signal captured on the D-Bus `org.worldcoin.OrbCore1.Signup` interface).
3. `orb.orb_relay` remains `Some(..)` connected to the aborted session instead of being set to `None`, since the cleanup block after the `?` is never reached.

**Note:** I was not able to fully trace whether `src/bin/orb-core.rs`'s top-level `run()` restarts the entire `MasterPlan`/`Observer` pair on error (which would reset `signup_flag` afresh) or whether the process exits and is restarted by an external supervisor — this affects how long the "stuck" `signup_flag` state persists in practice, and I could not verify it within the available context. The core inconsistent-state defect (skipped cleanup on `?`) itself is confirmed directly from the code shown above.

### Citations

**File:** src/plans/mod.rs (L366-391)
```rust
            dd_incr!("main.count.signup.during.general.signup_started");
            self.signup_flag.store(true, Ordering::Relaxed);
            let signup_result = Box::pin(self.do_signup(orb, qr_codes, dbus.as_ref())).await?;
            let success = signup_result.success;
            Box::pin(self.after_signup(orb, signup_result)).await?;
            self.signup_flag.store(false, Ordering::Relaxed);

            orb.disable_image_notary();
            if let Some(r) = orb.orb_relay.as_mut() {
                r.graceful_shutdown(
                    orb_relay_shutdown_wait_for_pending_messages,
                    orb_relay_shutdown_wait_for_shutdown,
                )
                .await;
            }
            orb.orb_relay = None;
            self.reset_hardware_except_led(orb).await?;
            if let Some(dbus_ctx) = dbus.as_ref() {
                dbus::Signup::signup_finished(dbus_ctx, success).await?;
            }

            if self.oneshot || self.has_biometric_input() {
                break Ok(());
            }
            self.ui_idle_delay = Some(time::sleep(Duration::from_secs(10)));
        }
```

**File:** src/plans/mod.rs (L490-512)
```rust
    #[allow(clippy::too_many_lines)]
    async fn do_signup(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        dbus: Option<&zbus::SignalContext<'_>>,
    ) -> Result<SignupResult> {
        let Config {
            self_serve,
            pcp_v3,
            orb_relay_announce_orb_id_retries,
            orb_relay_announce_orb_id_timeout,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
        let mut result = self.start_signup(orb, dbus).await?;
        let Some(qr_codes) =
            self.scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time).await?
        else {
            return Ok(result);
        };
```

**File:** src/agents/image_notary.rs (L286-298)
```rust
    fn run(mut self, mut port: port::Inner<Self>) -> Result<(), Self::Error> {
        let rt = runtime::Builder::new_current_thread().enable_all().build()?;
        'signup: while let Some(input) = rt.block_on(port.next()) {
            self.signup_id = match input.value {
                Input::InitializeSignup { signup_id } => signup_id,
                input => bail!("Unexpected image_notary input: {input:?}"),
            };
            ensure_enough_space().wrap_err("auto deletion")?;
            tracing::debug!(
                "There is {} bytes available on the SSD before signup",
                ssd::available_space()
            );
            self.initialize_signup();
```

**File:** src/brokers/orb.rs (L868-879)
```rust
    /// Stops the image notary agent.
    ///
    /// # Panics
    ///
    /// If the agent is not enabled.
    pub async fn stop_image_notary(&mut self) -> Result<image_notary::Log> {
        let image_notary = self.image_notary.enabled().expect("image_notary is not enabled");
        image_notary.send(port::Input::new(image_notary::Input::FinalizeSignup)).await?;
        let image_notary_log = image_notary::take_log(image_notary).await?;
        self.disable_image_notary();
        Ok(image_notary_log)
    }
```

**File:** src/dbus.rs (L6-20)
```rust
/// `Signup` is a DBus interface that emits signals related to signup events.
///
/// At the moment, the only signal emitted is for signups starting.
pub struct Signup;

#[dbus_interface(name = "org.worldcoin.OrbCore1.Signup")]
impl Signup {
    /// Emits a signal when a signup is started.
    #[dbus_interface(signal)]
    pub async fn signup_started(ctxt: &SignalContext<'_>) -> Result<()>;

    /// Emits a signal when a signup is completed
    #[dbus_interface(signal)]
    pub async fn signup_finished(ctx: &SignalContext<'_>, success: bool) -> Result<()>;
}
```

**File:** src/brokers/observer.rs (L568-585)
```rust
                if self.signup_flag.load(Ordering::Relaxed) {
                    if battery_voltage_sum_mv < BATTERY_VOLTAGE_SHUTDOWN_SIGNUP_THRESHOLD_MV {
                        tracing::info!(
                            "Shutting down during SIGNUP state because of low battery voltage: {} \
                             mV",
                            battery_voltage_sum_mv
                        );
                        self.ui.shutdown(false);
                        return Ok(BrokerFlow::Break);
                    }
                } else if battery_voltage_sum_mv < BATTERY_VOLTAGE_SHUTDOWN_IDLE_THRESHOLD_MV {
                    tracing::info!(
                        "Shutting down during idle state because of low battery voltage: {} mV",
                        battery_voltage_sum_mv
                    );
                    self.ui.shutdown(false);
                    return Ok(BrokerFlow::Break);
                }
```
