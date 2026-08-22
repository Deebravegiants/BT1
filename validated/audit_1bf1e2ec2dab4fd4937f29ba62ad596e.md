Confirmed: `master_plan.run(&mut orb)` is called exactly once in `src/bin/orb-core.rs#L150`, and unless `oneshot`/`has_biometric_input()` is set, `MasterPlan::run` loops internally over many successive signups for the lifetime of the process, per `src/plans/mod.rs#L387-390`.

### Title
Stale `self_serve`/`self_serve_button`/`operator_qr_expiration_time` snapshot lets orb keep running unsupervised self-serve signups after backend disables self-serve mode - (File: src/plans/mod.rs)

### Summary
`MasterPlan::run` reads `self_serve`, `self_serve_button`, and `operator_qr_expiration_time` **once** from the shared config at the very top of the function, before entering its signup loop, and reuses these stale values for every iteration of that loop for as long as the orb process runs. [1](#0-0)  Meanwhile, the backend-pushed config is refreshed independently and continuously in the background `Observer` broker, which downloads and swaps in a new `Config` behind the shared `Arc<Mutex<Config>>` every `CONFIG_UPDATE_INTERVAL`. [2](#0-1)  Because the master signup loop never re-reads these three specific fields, an operator/backend toggle to turn off self-serve mode (or shorten operator-QR expiration) does not take effect until the orb process is restarted, mirroring the reported DeFi bug where a config change (reserve factor) is not propagated into dependent runtime state (interest rate), leaving the system executing under stale parameters.

### Finding Description
`self_serve` gates whether a signup requires an operator to scan a QR code (button-press / operator-mediated flow) or proceeds autonomously via the self-serve flow that is triggered by the user alone. [3](#0-2)  The `Config` struct field doc explicitly frames `self_serve` and `self_serve_button` as behavior toggles for whether operator interaction is required to start a signup.

In `MasterPlan::run`, these values are destructured out of a single, momentary lock of `orb.config` and are then passed by value into `scan_initial_qr_codes` and `idle_wait_for_signup_request` on every iteration of the `loop { ... }`: [4](#0-3) 

The loop runs indefinitely (multiple signups back-to-back) unless the process was started with `oneshot` or a biometric-input file, per the loop's break condition. [5](#0-4)  The `Config` object being sampled here is shared via `Arc<Mutex<Config>>` with the `Observer` broker, which independently downloads and overwrites this shared config every `CONFIG_UPDATE_INTERVAL` in the background, entirely decoupled from the master plan's read. [6](#0-5) 

By contrast, `do_signup` (called from inside the same loop) *does* re-read the config fresh at the start of each call: [7](#0-6)  — this inconsistency (some call sites refresh, the top-level loop does not) is the direct analog of the reported bug: a subset of the derived/dependent state (`self_serve`, `self_serve_button`, `operator_qr_expiration_time` used for idle/QR-scan gating) is never resynchronized with the authoritative config after being cached, exactly like the liquidity rate that is never recomputed after the reserve factor changes.

### Impact Explanation
If an operator/fleet manager disables self-serve mode via the backend config (setting `self_serve: false`) in order to require operator supervision for all subsequent signups (e.g., in response to detected abuse, a compliance requirement, or a fielded orb being moved to an unsupervised environment), the running `orb-core` process will continue to use the previously-cached `self_serve = true` value for `idle_wait_for_signup_request` and `scan_initial_qr_codes` in every following iteration of the master loop. [4](#0-3)  This means the orb keeps accepting unsupervised, user-only-triggered signups instead of enforcing the operator-QR-gated flow the backend just mandated — i.e., signups proceed with an authorization gate that should have been re-enabled but was not, until the process restarts. This is an unauthorized-signup class impact: the enforcement decision (operator supervision required or not) silently diverges from the backend's intended, currently-configured policy for the remaining lifetime of the process.

Additionally, `operator_qr_expiration_time` being stale similarly means a backend-issued tightening of operator-QR validity (e.g., shortening it after a compromised operator badge/QR is reported) will not be honored by the idle loop for existing running sessions, extending the window an already-flagged operator QR remains accepted.

### Likelihood Explanation
This requires no special access beyond normal backend config management (which is the intended trust boundary for changing `self_serve`), and the divergence is triggered automatically and silently by simply pushing a config update while the orb-core process is already running (the common case for a fielded device, since the process is long-lived and only restarted infrequently). No attacker action beyond waiting for a legitimate policy change is needed, and the bug reproduces deterministically every time this specific config value is changed mid-session.

### Recommendation
Re-read `self_serve`, `self_serve_button`, and `operator_qr_expiration_time` from `orb.config` inside the `loop` in `MasterPlan::run` (i.e., on every iteration) instead of once before the loop, mirroring the pattern already used in `do_signup`, so that backend-driven policy changes take effect for the very next signup attempt rather than only after a process restart.

### Proof of Concept
1. Start `orb-core` normally with backend config `self_serve = true` (not `oneshot`, no biometric-input override).
2. `MasterPlan::run` captures `self_serve = true` once at `src/plans/mod.rs#L329-336` and enters its `loop`.
3. While the loop is running (e.g., between signups, or even during the idle-wait phase), the backend operator flips the orb's config to `self_serve = false` via the management API that feeds `backend::config::request`.
4. The background `Observer::config_update` task downloads this new config and swaps the shared `Arc<Mutex<Config>>` at `src/brokers/observer.rs#L196-201`.
5. On the next loop iteration, `MasterPlan::run` still calls `scan_initial_qr_codes`/`idle_wait_for_signup_request` with the original stale `self_serve = true` value captured in step 2, so the orb continues to accept unsupervised, user-QR-only signups exactly as if self-serve were still enabled — contrary to the operator's just-applied policy change — until the orb-core process is restarted.

### Citations

**File:** src/plans/mod.rs (L328-336)
```rust
    pub async fn run(&mut self, orb: &mut Orb) -> Result<()> {
        let Config {
            self_serve,
            self_serve_button,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
```

**File:** src/plans/mod.rs (L345-364)
```rust
        loop {
            self.scan_initial_qr_codes(
                orb,
                &mut initial_qr_codes,
                self_serve,
                operator_qr_expiration_time,
            )
            .await?;
            let Some(qr_codes) = self
                .idle_wait_for_signup_request(
                    orb,
                    &initial_qr_codes,
                    self_serve,
                    self_serve_button,
                    operator_qr_expiration_time,
                )
                .await?
            else {
                continue;
            };
```

**File:** src/plans/mod.rs (L386-391)
```rust

            if self.oneshot || self.has_biometric_input() {
                break Ok(());
            }
            self.ui_idle_delay = Some(time::sleep(Duration::from_secs(10)));
        }
```

**File:** src/plans/mod.rs (L497-506)
```rust
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
```

**File:** src/brokers/observer.rs (L187-203)
```rust
    fn config_update(&mut self, observer: &mut Observer) -> Result<()> {
        if self.before_config_update()? {
            match observer.config_update.as_mut().map(future::FutureExt::now_or_never) {
                Some(None) => return Ok(()),
                Some(Some(result)) => result??,
                None => {}
            }
            let config = Arc::clone(&observer.config);
            let ui = observer.ui.clone();
            observer.config_update = Some(tokio::spawn(async move {
                if let Ok(new_config) = Config::download().await {
                    *config.lock().await = new_config;
                    config.lock().await.propagate_to_ui(ui.as_ref());
                }
                Ok(())
            }));
        }
```

**File:** src/config.rs (L86-93)
```rust
    /// Self-serve mode.
    pub self_serve: bool,
    /// Alternative mode for self-serve: start a signup with a button press.
    pub self_serve_button: bool,
    /// Ask the operator for a QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged: bool,
    /// How long to wait for the operator to scan the QR code when a possibly underaged person is detected.
    pub self_serve_ask_op_qr_for_possibly_underaged_timeout: Duration,
```
