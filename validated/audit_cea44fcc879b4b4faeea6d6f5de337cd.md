### Title
Silent drop of unsent tier1/tier2 biometric self-custody packages in the shared upload queue causes cross-signup data loss while enrollment is reported as successful - (File: src/agents/data_uploader.rs)

### Summary
The external report describes a shared resource (bento `token0`/`token1` balance) being silently consumed by an unrelated accounting path (`collect()`), so that a legitimately owed payout (`claimReward`/`reclaimIncentive`) later fails even though the internal ledger believes the funds are available. The orb-core analog is the `data_uploader` agent's shared, per-tier in-memory/persistent queue that biometric Personal Custody Packages (PCP tier1/tier2) are pushed into for asynchronous upload. When the queue reaches `dropping_threshold`, the oldest queued package — which may belong to a *different, already-completed* signup — is silently evicted (`drop_oldest`) with only a log line, before the new signup's data is pushed in its place.

### Finding Description
`do_signup` in `src/plans/mod.rs` builds the tier1/tier2 self-custody packages and pushes them into the data-uploader queue via `Input::Pcp`, then immediately continues the signup flow without waiting for confirmation of eventual upload success [1](#0-0) . The enrollment result / success flag is computed independently afterward, so the signup is reported as complete/successful even though tier1/tier2 upload is only "queued," not confirmed [2](#0-1) .

The `data_uploader::Agent::run` loop enforces two independent thresholds per tier: a `blocking_threshold` that `wait_queues` respects, and a separate, lower-behaving `dropping_threshold` check performed unconditionally on every incoming `Input::Pcp`, regardless of which signup is pushing: if `queues[i].len() == dropping_thresholds[i]`, the oldest entry in that tier's queue is evicted via `drop_oldest()` before the new item is pushed [3](#0-2) . `drop_oldest()` removes the queue's oldest package outright — for the in-memory queue by `pop_back()` (dropping the data in the accompanying `Vec`), and for the persistent queue by deleting the on-disk directory — with no notification to the originating signup and no way to detect afterward that this occurred [4](#0-3) . Because `wait_queues` only blocks on `blocking_threshold`, not `dropping_threshold`, and `dropping_threshold` is checked on every push independently of whatever earlier signup's item is queued, one signup's PCP push can cause a completely different signup's still-unuploaded biometric self-custody package to be silently discarded.

This mirrors the reported bug class: a shared resource (upload queue capacity / bento token balance) is consumed by activity unrelated to the record that logically "owns" the data/funds, and the consuming/owning code has no way to detect or recover from the loss — the difference being that in orb-core the affected asset is the user's own biometric self-custody package rather than an incentive token payout.

### Impact Explanation
Tier1/tier2 packages contain iris/face biometric image tars and cryptographic key material intended for the user's self-custody bundle. Silent eviction from the upload queue means the orb never retries or reports this failure to the backend or to the affected user's signup record, while `do_signup` has already reported the enrollment as successful based on tier0 confirmation and the pipeline result alone (tier1/tier2 confirmation is not part of the success condition). This creates a permanent, undetectable loss of biometric upload/retention data tied to a specific completed signup, which is explicitly an in-scope impact category (biometric upload and retention).

### Likelihood Explanation
Any unprivileged user performing ordinary signups can trigger this: the `dropping_threshold` is a fixed, shared configuration value applied identically to every incoming `Pcp` push regardless of tenant/signup, so sustained or bursty legitimate signup traffic on a single orb (e.g., multiple people queuing quickly, or slow/throttled uploads to the backend) is sufficient to exceed the dropping threshold and evict another user's not-yet-uploaded package. No malicious input, privilege, or hardware access is required — only normal usage volume/timing, which the rules classify as reachable by an unprivileged actor.

### Recommendation
Do not silently drop queued PCP packages that belong to a different, already-processed signup. Options:
- Track per-tier "confirmed uploaded" state and surface upload failures/drops back to the specific signup's debug report / backend status instead of only logging.
- Increase `dropping_threshold` to be strictly reachable only after `blocking_threshold` is honored by all producers (i.e., make `wait_queues` account for the dropping threshold too), or persist dropped items with a retry/backoff instead of deleting them outright.
- At minimum, emit a metric/alert per dropped signup ID so operators can detect and remediate lost biometric uploads.

### Proof of Concept
1. Configure (or reach in production) `pcp_tier1_dropping_threshold` = N.
2. Complete signup A: `do_signup` builds tier1/tier2 packages and pushes tier1 into the queue via `Input::Pcp` [5](#0-4) . Assume the tier1 backend upload is slow/queued and not yet committed.
3. In quick succession, N more signups (B1..BN) each push their own tier1 `Pcp` before A's item is uploaded, until `queues[0].len() == dropping_thresholds[0]`.
4. On the next push, `data_uploader::Agent::run` executes `queues[i].drop_oldest().await` before pushing the new item [6](#0-5) , deleting signup A's tier1 package (and its underlying data, per `drop_oldest`) [4](#0-3) .
5. Signup A's enrollment result was already reported success in `do_signup` (tier0 confirmation only) [2](#0-1) ; no error, retry, or notification is ever produced for the lost tier1 package.

### Citations

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

**File:** src/plans/mod.rs (L639-662)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
```

**File:** src/agents/data_uploader.rs (L136-146)
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
