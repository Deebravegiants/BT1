The strongest analog to the Convex "unbounded external action blocking a required operation forever" bug class in this codebase is the infinite, uncapped retry loop in the personal-custody-package uploader agent, `Agent::upload_pcp` in `src/agents/data_uploader.rs`. It handles the biometric/identity-data ("personal custody package") upload and retention path, is reachable without any privileged actor, and can permanently starve upload capacity and evict pending biometric data due to persistent backend/network errors, mirroring the "forced call in a critical path never completes" dynamic of the referenced report.

### Title
Unbounded retry loop in the personal-custody-package uploader can permanently starve upload slots and cause biometric data eviction - (File: src/agents/data_uploader.rs)

### Summary
`Agent::upload_pcp` retries the `upload_personal_custody_package` backend request in an unconditional `loop` with no retry limit, no backoff cap, and no timeout — it only breaks on success or on an HTTP 4xx client error [1](#0-0) . Because only `PARALLEL_UPLOAD_STREAMS` (4) upload slots exist and a stuck upload never returns to free a slot, any condition that keeps causing non-client-error failures (5xx responses, network errors, or a backend service that never accepts the request) traps upload slots forever, exactly analogous to how the Convex `extraRewards` list forces `claimRewards()` to never complete and blocks the locker.

### Finding Description
The data-uploader agent runs a small fixed pool of concurrent uploaders (`PARALLEL_UPLOAD_STREAMS = 4`) drawn from per-tier queues [2](#0-1) . The main select loop only pulls the next queued item into an uploader slot when a previous uploader future resolves via `uploaders.next()` [3](#0-2) . That resolution depends entirely on `upload_pcp` returning, which it only does on success or a 4xx client error — any other, indefinitely repeating failure condition (e.g. a 5xx from the backend, a persistent network partition, or backend misbehavior) leaves the loop spinning forever without ever returning `(tier, id)` [4](#0-3) .

Meanwhile, incoming `Input::Pcp` pushes keep queuing new packages, and once a queue reaches its per-tier `dropping_threshold` the oldest (by intended design) entry is evicted to make room [5](#0-4) . If all 4 uploader slots are simultaneously wedged in the infinite retry loop, no queue is ever drained, so once the dropping threshold is hit, queued personal-custody packages — encrypted signup/biometric material — are silently discarded via `drop_oldest` [6](#0-5) .

This is structurally the same bug class as the Convex report: a downstream, externally-influenced condition (repeated non-4xx failures from the backend) causes a "must complete" loop to run forever, permanently consuming the limited resource (upload slots) needed to make forward progress, ultimately causing loss/stranding of user data that depended on that forward progress.

### Impact Explanation
If the backend or network path returns persistent non-client errors (which can be triggered by ordinary backend outages, rate limiting responses that aren't flagged as 4xx, or any upstream instability), all upload slots can become permanently occupied. Personal-custody packages (identity/biometric-linked signup data) queued behind the wedged slots are then evicted once the per-tier dropping threshold is reached, resulting in permanent, silent loss of that user's custody data — the upload/retention analog of "assets being stuck" in the source report. This also affects `wait_queues`/`Input::WaitQueues`, which is used to ensure queues are drained (e.g. before shutdown), and will hang forever if `check_blocking` never clears [7](#0-6) .

### Likelihood Explanation
Likelihood is driven by ordinary backend/network reliability, not by any malicious privileged actor — a run of repeated 5xx errors or connection failures from the backend service is a realistic, low-effort-to-trigger condition (no attacker control required, unlike the operator/admin scenario explicitly excluded here). Given the loop has zero retry cap and zero timeout, even a moderate backend outage window is enough to wedge all 4 slots simultaneously.

### Recommendation
Bound the retry loop in `upload_pcp` with a maximum retry count and/or an overall timeout (mirroring the already-bounded `RETRIES_COUNT = 6` pattern used in `upload_pcp_tier_0` in `src/plans/mod.rs`) [8](#0-7) , and on exhaustion release the uploader slot (returning an error/id back to the queue loop) instead of looping indefinitely, so a persistently failing backend cannot permanently consume all parallel upload capacity or trigger silent eviction of queued custody data.

### Proof of Concept
1. Backend endpoint for `upload_personal_custody_package::request` starts returning HTTP 500 (or any non-4xx error/timeout) consistently for all requests.
2. Orb enqueues 4+ personal-custody packages across tiers via `Input::Pcp`; the queue loop fills all `PARALLEL_UPLOAD_STREAMS` slots with `upload_pcp` futures [5](#0-4) .
3. Each `upload_pcp` call enters its `loop`, repeatedly failing with the non-client error branch and never breaking [4](#0-3) .
4. New `Input::Pcp` pushes keep arriving; once a tier's queue length hits `dropping_threshold`, `drop_oldest` is invoked, discarding queued custody packages permanently [9](#0-8) .
5. Once the backend recovers, only the 4 originally-wedged (and now potentially stale/expired) requests will ever complete first; anything evicted in step 4 is unrecoverable, and `Input::WaitQueues` callers remain blocked the entire time.

### Citations

**File:** src/agents/data_uploader.rs (L22-23)
```rust
const PARALLEL_UPLOAD_STREAMS: usize = 4;
const TIERS_COUNT: u8 = 2;
```

**File:** src/agents/data_uploader.rs (L116-133)
```rust
        loop {
            select! {
                biased;
                Some((tier, id)) = uploaders.next() => {
                    queues[usize::from(tier - 1)].commit(id).await;
                    if !check_blocking(&queues) {
                        for tx in take(&mut waiters) {
                            tx.send(()).unwrap();
                        }
                    }
                    for queue in &mut queues {
                        if let Some((pcp, id)) = queue.pop().await {
                            log_queues!(queues);
                            uploaders.push(self.upload_pcp(pcp, id));
                            break;
                        }
                    }
                },
```

**File:** src/agents/data_uploader.rs (L137-152)
```rust
                        Input::Pcp(pcp) => {
                            if !(1..=TIERS_COUNT).contains(&pcp.tier) {
                                tracing::error!("Invalid tier: {}", pcp.tier);
                                continue;
                            }
                            let i = usize::from(pcp.tier - 1);
                            if queues[i].len() == dropping_thresholds[i] as usize {
                                queues[i].drop_oldest().await;
                            }
                            queues[i].push(pcp).await;
                            if uploaders.len() < PARALLEL_UPLOAD_STREAMS {
                                if let Some((pcp, id)) = queues[i].pop().await {
                                    log_queues!(queues);
                                    uploaders.push(self.upload_pcp(pcp, id));
                                }
                            }
```

**File:** src/agents/data_uploader.rs (L153-160)
```rust
                        },
                        Input::WaitQueues(tx) => {
                            if check_blocking(&queues) {
                                waiters.push(tx);
                            } else {
                                tx.send(()).unwrap();
                            }
                        },
```

**File:** src/agents/data_uploader.rs (L170-215)
```rust
    async fn upload_pcp(&self, pcp: Pcp, id: u64) -> (u8, u64) {
        let Pcp { signup_id, user_id, data, checksum, tier } = pcp;
        tracing::info!(
            "Start uploading a personal custody package tier {tier} for signup_id={signup_id}"
        );
        let t = Instant::now();
        loop {
            let response = backend::upload_personal_custody_package::request(
                &signup_id,
                &user_id,
                checksum.as_ref(),
                &data,
                Some(tier),
                &self.config,
            )
            .await;
            match response {
                Ok(()) => {
                    dd_timing!("main.time.signup.upload_custody_images" + format!("t{}", tier), t);
                    tracing::info!(
                        "Personal custody package tier {tier} uploading completed in: {}ms",
                        t.elapsed().as_millis()
                    );
                    break;
                }
                Err(err) => {
                    tracing::error!("UPLOAD PERSONAL CUSTODY PACKAGE TIER {tier} ERROR: {err:?}");
                    dd_incr!(
                        "main.count.http.upload_custody_images.error.network_error",
                        "error_type:normal"
                    );
                    if let Some(reqwest_err) = err.downcast_ref::<reqwest::Error>() {
                        if let Some(status) = reqwest_err.status() {
                            if status.is_client_error() {
                                dd_incr!(
                                    "main.count.signup.result.failure.upload_custody_images",
                                    "type:network_error",
                                    "subtype:signup_request"
                                );
                                break;
                            }
                        }
                    }
                }
            }
        }
```

**File:** src/agents/data_uploader.rs (L343-361)
```rust
    async fn drop_oldest(&mut self) {
        match self {
            Self::Memory { queue } => {
                queue.pop_back();
            }
            Self::Persistent { path, queue, .. } => {
                let Some(id) = queue.pop_back() else { return };
                match ssd::perform_async(fs::remove_dir_all(path.join(id.to_string()))).await {
                    None => {
                        tracing::error!(
                            "Persistent queue is failed during drop_oldest, switching to memory"
                        );
                        *self = Self::new_memory();
                    }
                    Some(()) => {}
                }
            }
        }
    }
```

**File:** src/plans/mod.rs (L1786-1839)
```rust
    ) -> Result<bool> {
        const RETRIES_COUNT: usize = 6;
        tracing::info!("Start uploading personal custody package");
        let t = Instant::now();
        for i in 0..RETRIES_COUNT {
            let response = backend::upload_personal_custody_package::request(
                signup_id,
                user_id,
                checksum.as_ref(),
                &data,
                tier,
                &orb.config,
            )
            .await;
            match response {
                Ok(()) => {
                    dd_timing!("main.time.signup.upload_custody_images", t);
                    tracing::info!(
                        "Personal custody package uploading completed in: {}ms",
                        t.elapsed().as_millis()
                    );
                    return Ok(true);
                }
                Err(err) => {
                    tracing::error!("UPLOAD PERSONAL CUSTODY PACKAGE ERROR: {err:?}");
                    dd_incr!(
                        "main.count.http.upload_custody_images.error.network_error",
                        "error_type:normal"
                    );
                    if let Some(reqwest_err) = err.downcast_ref::<reqwest::Error>() {
                        if let Some(status) = reqwest_err.status() {
                            if status.is_client_error() {
                                dd_incr!(
                                    "main.count.signup.result.failure.upload_custody_images",
                                    "type:network_error",
                                    "subtype:signup_request"
                                );
                                break;
                            }
                        }
                    }
                    if i == RETRIES_COUNT - 1 {
                        dd_incr!(
                            "main.count.signup.result.failure.upload_custody_images",
                            "type:network_error",
                            "subtype:signup_request"
                        );
                    }
                }
            }
        }
        notify_failed_signup(orb, Some(SignupFailReason::UploadCustodyImages));
        Ok(false)
    }
```
