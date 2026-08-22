### Title
Permanent loss of unuploaded Personal Custody Package (biometric) data on queue overflow — ([File: src/agents/data_uploader.rs])

### Summary
The reported bug describes `LiquidityFarming.withdraw()` deleting `nftInfo`, which unconditionally erases `nft.unpaidRewards` that had not yet been paid out — permanently destroying value owed to the user without checking whether it was zero first. The analogous pattern exists in `orb-core`'s data-uploader agent: when a tier queue reaches its `dropping_threshold`, the oldest queued `Pcp` (personal custody package, i.e., biometric/iris data awaiting upload) is unconditionally evicted and deleted via `drop_oldest()`, with no check on whether that package has ever been successfully uploaded to the backend.

### Finding Description
In the `data-uploader` agent's main loop, when a new `Pcp` is pushed and the queue for its tier is already at `dropping_thresholds[i]`, the code calls `queue.drop_oldest().await` before pushing the new item: [1](#0-0) 

`drop_oldest()` unconditionally discards the oldest entry — for the in-memory queue it just pops it from the `VecDeque`, and for the persistent queue it removes the entire directory (`meta.json` + `data.bin`) from disk via `fs::remove_dir_all`: [2](#0-1) 

Nowhere in this path is there a check for whether the discarded package has actually been confirmed uploaded (`commit()` is only invoked from the separate `uploaders.next()` branch, not from `drop_oldest()`). This exactly mirrors the root cause in the external report: state representing "value not yet delivered/paid" (`unpaidRewards` vs. an un-uploaded `Pcp`) is deleted unconditionally instead of guarding the deletion with `require(unpaidRewards == 0)`-style logic (e.g., only dropping entries once confirmed committed, or refusing to drop and instead blocking/retrying).

### Impact Explanation
A `Pcp` represents tiered personal-custody biometric data (iris codes, identification images, checksums) tied to a specific `signup_id`/`user_id`, queued for asynchronous upload to the backend as part of the signup pipeline (`src/plans/mod.rs`, `do_signup`). If uploads are slow or backend requests repeatedly fail (see the retry loop in `upload_pcp`, which only breaks out on success or a client-error HTTP status, otherwise looping forever) while new signups keep enqueuing packages, the queue can reach the `dropping_threshold` and silently and permanently discard older, still-unconfirmed biometric packages. This causes irrecoverable loss of biometric enrollment data for the affected signup(s) — the tier-1/tier-2 PCP for that user is gone with no possibility of retry, similar in class to the reported loss of user-owed rewards. This can manifest as an orphaned/incomplete signup where the on-orb enrollment succeeded but the durable biometric custody package was never delivered, undermining biometric-upload-and-retention guarantees.

### Likelihood Explanation
This is not a hypothetical attack requiring a malicious peer/operator — it is triggered by ordinary operational conditions: sustained backend unavailability, network issues, or a burst of signups causing the dropping threshold to be reached before uploads complete. The thresholds (`pcp_tier1_dropping_threshold`, `pcp_tier2_dropping_threshold`) are configurable but the drop logic itself has no safety check tied to actual delivery confirmation, making the loss path fully reachable under realistic conditions.

### Recommendation
Mirror the report's recommended fix pattern: before evicting/deleting a queued package in `drop_oldest()`, ensure it is not counted as "in flight/unconfirmed" state that the system still owes the user — e.g., only allow dropping of entries that are not the oldest un-uploaded record, prefer blocking new signups (as already exists via `blocking_thresholds`/`WaitQueues`) instead of destructively dropping, or persist dropped packages to a durable dead-letter location for manual recovery rather than calling `fs::remove_dir_all` outright. At minimum, treat reaching the dropping threshold as a signup-pipeline failure condition that is surfaced/alerted rather than a silent, permanent data loss.

### Proof of Concept
1. Configure or observe a scenario where backend upload of PCP packages is failing/slow (e.g., `upload_personal_custody_package::request` returns retryable errors repeatedly) as in `upload_pcp` retry loop: [3](#0-2) 
2. Continue performing signups so that `Input::Pcp` pushes accumulate in `queues[i]` faster than they drain.
3. Once `queues[i].len() == dropping_thresholds[i]`, the next `Pcp` push triggers `queues[i].drop_oldest().await`, deleting the oldest still-unuploaded package's data.
4. That signup's biometric custody package is now permanently unrecoverable — there is no code path that re-adds or retries a dropped entry. [4](#0-3)

### Citations

**File:** src/agents/data_uploader.rs (L136-153)
```rust
                    Some(input) => match input.value {
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
                        },
```

**File:** src/agents/data_uploader.rs (L176-215)
```rust
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
