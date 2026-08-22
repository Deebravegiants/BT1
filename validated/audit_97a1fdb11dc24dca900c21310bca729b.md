### Title
Infinite retry loop in `data_uploader::Agent::upload_pcp` permanently occupies upload slots and blocks all future signups - (File: src/agents/data_uploader.rs)

### Summary
`data_uploader::Agent::upload_pcp` retries a personal-custody-package (PCP) upload in an unbounded `loop` that only exits on success or on an HTTP 4xx client error. Any other failure mode (5xx server error, timeout, connection reset, DNS failure, etc.) causes the loop to retry forever with no backoff limit and no way to abort. Because only `PARALLEL_UPLOAD_STREAMS` (4) uploads run concurrently, a small number of signups whose uploads reliably fail with a non-4xx error can permanently occupy every upload slot. Once occupied, the queue never drains, `check_blocking` never clears, and `data_uploader::wait_queues` — called by every subsequent signup before it can even start its own tier-0 upload — blocks forever, freezing signup for the entire Orb.

### Finding Description
`Agent::upload_pcp` is defined as: [1](#0-0) 

The `loop` only has two exit paths: `Ok(())` (success) or an `Err` whose downcast is a `reqwest::Error` with a client-error (4xx) status. Any other error — including retriable 5xx server errors, network timeouts, or connection resets — falls through with no `break`, so the loop retries indefinitely with no delay and no cap on iteration count.

This loop runs inside the agent's main task loop, which only pops a new item from `queues[i]` into `uploaders` when a slot is free (`uploaders.len() < PARALLEL_UPLOAD_STREAMS`) and only advances the queue (`commit`) when an uploader in `uploaders` resolves: [2](#0-1) 

Because `upload_pcp` never resolves for a persistently-failing (but non-4xx) target, the corresponding `FuturesUnordered` future in `uploaders` never completes. If enough signups produce uploads that fail this way, all `PARALLEL_UPLOAD_STREAMS` slots become permanently occupied, and the tier-1/tier-2 queues fill up until they hit `pcp_tier1_blocking_threshold`/`pcp_tier2_blocking_threshold` (defaults 12 and `u32::MAX`/12 respectively): [3](#0-2) 

Every subsequent signup calls `data_uploader::wait_queues` before it is allowed to proceed with its own uploads: [4](#0-3) 

`wait_queues` blocks the caller on a oneshot channel that is only resolved once `check_blocking` becomes `false` again — which requires the stuck uploaders to complete, which they never will: [5](#0-4) [6](#0-5) 

Note the contrast with the bounded-retry logic used for tier-0 uploads in `upload_pcp_tier_0`, which correctly caps retries at `RETRIES_COUNT` and gives up: [7](#0-6) 

`upload_pcp` (used for tier 1/2, PCP v3 flow) has no such bound.

### Impact Explanation
This is directly analogous to the referenced report: a small number of "unblockable" items (there, a blacklisted address that can never receive a transfer; here, uploads that can never succeed with a non-4xx status) occupy a shared, limited resource pool forever, and this permanently locks out an unrelated shared operation for all future, legitimate users (`withdrawExcessRewards()` there; all future orb signups via `wait_queues` here). Once triggered, the Orb can no longer complete any signup requiring tier-1/tier-2 PCP upload (PCP v3 path) until the process is restarted, denying service to every subsequent legitimate user of that Orb.

### Likelihood Explanation
Reaching the "all slots and queue full" state does not require a malicious operator or hardware access — it can be triggered purely through the normal, unprivileged signup path (an ordinary signup that ends up producing a PCP upload target/response that always yields a retriable, non-4xx failure, e.g., a transient or persistent backend 5xx, an intentionally malformed but non-4xx-triggering request, or network conditions that repeatedly cause timeouts). Because it only takes filling the small number of parallel upload slots (4) plus the queue threshold (as low as 12), the number of affected signups needed to fully lock the subsystem is small, and no elevated privileges are required.

### Recommendation
Bound the retry loop in `Agent::upload_pcp` the same way `upload_pcp_tier_0` is bounded: cap the number of retries (or apply an exponential backoff with a maximum), and on exhaustion, drop/fail the item (or move it to a dead-letter path) instead of looping forever. Ensure `check_blocking`/`wait_queues` cannot be blocked indefinitely by a single unresolvable item — e.g., allow items exceeding a retry/time budget to be dropped from the queue and counted separately, so legitimate signups are not denied service by another user's persistently failing upload.

### Proof of Concept
1. Configure/trigger a signup (PCP v3 enabled, `pcp_version >= 3`) whose personal-custody-package upload endpoint responds with a persistent 5xx (or times out) rather than a 4xx.
2. `do_signup` enqueues the tier-1/tier-2 packages via `data_uploader::Input::Pcp` as shown in `src/plans/mod.rs` (lines 613-636).
3. `Agent::upload_pcp` (src/agents/data_uploader.rs:169-217) enters its `loop`, repeatedly hits the non-client error branch, and never `break`s — the future in `uploaders` never resolves, permanently occupying one of the 4 `PARALLEL_UPLOAD_STREAMS`.
4. Repeat with enough such signups to occupy all 4 upload slots and/or fill the tier1/tier2 queues to `pcp_tier1_blocking_threshold`/`pcp_tier2_blocking_threshold`.
5. Any subsequent legitimate signup calls `data_uploader::wait_queues(...)` (src/plans/mod.rs:599) before its own upload can proceed; since `check_blocking` never returns `false` again, this call blocks forever, and the signup — along with every future signup on the Orb — never completes.

### Citations

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

**File:** src/agents/data_uploader.rs (L154-160)
```rust
                        Input::WaitQueues(tx) => {
                            if check_blocking(&queues) {
                                waiters.push(tx);
                            } else {
                                tx.send(()).unwrap();
                            }
                        },
```

**File:** src/agents/data_uploader.rs (L169-217)
```rust
impl Agent {
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
        (tier, id)
    }
```

**File:** src/agents/data_uploader.rs (L364-369)
```rust
/// Waits for all queues to be not full.
pub async fn wait_queues(port: &mut port::Outer<Agent>) -> Result<()> {
    let (tx, rx) = oneshot::channel();
    port.send(port::Input::new(Input::WaitQueues(tx))).await?;
    Ok(rx.await?)
}
```

**File:** src/config.rs (L432-435)
```rust
            pcp_tier1_blocking_threshold: 12,
            pcp_tier1_dropping_threshold: u32::MAX,
            pcp_tier2_blocking_threshold: u32::MAX,
            pcp_tier2_dropping_threshold: 12,
```

**File:** src/plans/mod.rs (L599-599)
```rust
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
```

**File:** src/plans/mod.rs (L1787-1836)
```rust
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
```
