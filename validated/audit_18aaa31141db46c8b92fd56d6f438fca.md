### Title
Personal Custody Package tiers 1 & 2 are queued only in volatile memory and are permanently lost on Orb reset/restart before upload completes - (File: `src/agents/data_uploader.rs`)

### Summary
The bug report describes funds that are supposed to be forwarded to a `PayoutManager` for later withdrawal, but instead are only reachable in a narrow time window and are lost if the system is reset before that transfer happens. The analogous flaw in `orb-core` is in the `data_uploader` agent: biometric custody data ("Personal Custody Package" tiers 1 and 2) is handed off to an in-memory-only queue for asynchronous background upload to the backend. If the Orb process crashes, is rebooted, or the signup pipeline is otherwise reset before the background upload completes, the queued biometric package is silently and permanently lost, with no on-disk persistence or retry across process restarts.

### Finding Description
The `data_uploader::Agent::run` task maintains upload queues built as `Queue::new_memory()`: [1](#0-0) 

The `Queue` type has both a `Memory` variant (a plain in-process `VecDeque<Pcp>`) and a `Persistent` variant backed by a file path, but the `Persistent` variant is unused and explicitly marked `#[allow(dead_code)]`, and construction always uses the memory-only variant: [2](#0-1) 

In the signup flow, tier 0 of the Personal Custody Package is uploaded synchronously with retries before the signup is allowed to be reported as successful (`upload_pcp_tier_0`), but tiers 1 and 2 — which contain the iris/normalized-iris/face image tars encrypted for the user's self-custody as well as the fraud-relevant tier2 payload — are simply pushed onto the `data_uploader` agent's in-memory queue and handled fire-and-forget: [3](#0-2) 

The agent then attempts uploads in a background loop with indefinite retries on network errors (breaking only on client errors): [4](#0-3) 

Because the queue lives only in the `data_uploader` agent's process memory (`VecDeque`), any Orb reset/crash/process restart that occurs after `Input::Pcp` is enqueued but before `upload_pcp` succeeds will drop the queued tier1/tier2 package irrecoverably — there is no persisted state to resume the upload on the next run, mirroring the reported bug class where a critical hand-off ("send funds to PayoutManager" / here, "send custody package to backend") is not reliably completed and is lost across a reset boundary.

### Impact Explanation
Tier 1 and tier 2 of the Personal Custody Package carry the user's biometric material (iris/face images and derived embeddings) encrypted for backend and self-custody keys, which is used for downstream identity verification and dispute/fraud resolution workflows. If this data is silently dropped due to a reset, the signup can be recorded as "successful" (since only tier 0 upload gates that path) while the associated biometric evidence for that signup never reaches the backend, resulting in incomplete/missing biometric records for a completed signup with no automatic recovery.

### Likelihood Explanation
Orb devices in the field are subject to reboots, crashes, power loss, and process restarts, especially given ongoing continuous operation and hardware reset routines (`reset_hardware`, `reset_hardware_except_led`) invoked around every signup cycle: [5](#0-4) [6](#0-5) 
Any such event that races with an in-flight or queued tier1/tier2 upload will trigger the loss, making this a realistically reachable condition rather than a purely theoretical one.

### Recommendation
Use the already-defined `Queue::Persistent` variant (or an equivalent durable queue) to persist enqueued tier1/tier2 `Pcp` packages to disk before acknowledging the push, and reload/resume any pending uploads on agent startup, so that a reset or process restart cannot cause silent, unrecoverable loss of biometric custody data that was reported as part of a "successful" signup.

### Proof of Concept
1. Complete a signup so that `do_signup` builds the PCP and sends tier1/tier2 via `data_uploader::Input::Pcp` [3](#0-2) .
2. Before the background `upload_pcp` task completes (e.g., under slow/unstable network conditions), kill or restart the `orb-core` process (simulating a reset/crash).
3. On restart, `data_uploader::Agent::run` reinitializes `queues` via `Queue::new_memory()` with empty `VecDeque`s [7](#0-6) , so the previously queued tier1/tier2 package for that signup is gone and never retried, even though the signup itself was already marked successful.

### Citations

**File:** src/agents/data_uploader.rs (L57-68)
```rust
enum Queue {
    Memory {
        queue: VecDeque<Pcp>,
    },
    #[allow(dead_code)]
    Persistent {
        path: PathBuf,
        queue: VecDeque<u64>,
        next_id: u64,
        in_progress: u64,
    },
}
```

**File:** src/agents/data_uploader.rs (L95-106)
```rust
    async fn run(self, mut port: port::Inner<Self>) -> Result<(), Self::Error> {
        let Config {
            pcp_tier1_blocking_threshold,
            pcp_tier1_dropping_threshold,
            pcp_tier2_blocking_threshold,
            pcp_tier2_dropping_threshold,
            ..
        } = *self.config.lock().await;
        let blocking_thresholds = [pcp_tier1_blocking_threshold, pcp_tier2_blocking_threshold];
        let dropping_thresholds = [pcp_tier1_dropping_threshold, pcp_tier2_dropping_threshold];
        let mut queues: [_; TIERS_COUNT as usize] = array::from_fn(|_| Queue::new_memory());
        let mut uploaders = FuturesUnordered::new();
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

**File:** src/plans/mod.rs (L342-342)
```rust
        self.reset_hardware(orb, Duration::from_secs(10)).await?;
```

**File:** src/plans/mod.rs (L382-382)
```rust
            self.reset_hardware_except_led(orb).await?;
```

**File:** src/plans/mod.rs (L613-636)
```rust
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
```
