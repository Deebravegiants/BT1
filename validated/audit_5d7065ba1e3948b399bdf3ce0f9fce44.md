This is a real finding in `data_uploader.rs`: the tier-1/tier-2 PCP upload queue uses per-tier `dropping_thresholds`, and when a queue is full, `Queue::drop_oldest` unconditionally evicts whatever package is at the back of that shared queue — regardless of which signup/user it belongs to.

### Title
Cross-user biometric data (PCP) silently dropped from a shared upload queue without per-signup segregation - (File: `src/agents/data_uploader.rs`)

### Summary
`data_uploader::Agent` maintains a single shared, in-memory `Queue` per PCP tier that mixes personal-custody packages (PCP tier 1/tier 2, containing encrypted iris/face biometric data) from *any* signup/user. When a queue fills up to `dropping_thresholds[i]`, the agent calls `queues[i].drop_oldest().await` before pushing the newly arriving package, with no check of whose `signup_id`/`user_id` the dropped entry belongs to. [1](#0-0) [2](#0-1) 

### Finding Description
Each signup enqueues its tier-1 and tier-2 PCP packages into a shared, un-segregated `VecDeque<Pcp>` (or persistent-queue analog) via `Input::Pcp`. [3](#0-2)  The dropping logic is purely capacity-based and identity-agnostic:

```
if queues[i].len() == dropping_thresholds[i] as usize {
    queues[i].drop_oldest().await;
}
queues[i].push(pcp).await;
``` [4](#0-3) 

`drop_oldest` simply pops from the back of the queue (memory or persistent variant) and discards the associated data on disk with no notification, retry, or record of which user was affected. [2](#0-1) 

This mirrors the H-1 bug class: a single shared pool (queue) commingles distinct users' not-yet-persisted assets (their PCP/biometric enrollment packages), and a housekeeping/capacity-management operation (`drop_oldest`) indiscriminately destroys whichever entry happens to occupy the "victim" slot — exactly like `withdrawNative` sweeping the whole WETH balance without knowing which portion belonged to an unclaimed user order. Here, the "asset" is a completed signup's biometric enrollment package (tier 1/2 PCP) that is queued for backend upload; the calling code in `plans/mod.rs` assumes this send always succeeds and proceeds to report signup success without verifying the tier-1/tier-2 packages were actually delivered. [5](#0-4) 

### Impact Explanation
If the queue for a tier reaches its `dropping_thresholds` limit (e.g., during backend outages, network congestion, or bursts of signups), an in-flight user's tier-1/tier-2 PCP package can be silently and permanently discarded before ever being uploaded, while orb-core still reports the signup as `Success` (enrollment success is determined earlier, independent of whether tier1/tier2 async uploads complete). [6](#0-5)  This is a genuine loss of a specific user's enrolled biometric custody data with no recovery path, distinct from any other user's fault — a direct analog of "loss of assets for the victim due to lack of segregation of a shared pool."

### Likelihood Explanation
Requires only normal operational conditions (queue backlog from network/backend slowness or a burst of consecutive signups reaching `pcp_tier1_dropping_threshold`/`pcp_tier2_dropping_threshold`), not any malicious operator/node/hardware access. It is fully in the production, non-test, non-internal-only code path (unlike the `internal-data-acquisition`-gated debug image saving, which is explicitly for internal R&D only and excluded from consideration).

### Recommendation
Segregate the drop decision by signup/user rather than purely by pool position: track per-signup delivery state and refuse/park new pushes (backpressure) instead of silently evicting another user's already-queued package, or persist an explicit record of drops tied to `signup_id`/`user_id` so failures can be retried or surfaced rather than lost. At minimum, `enroll_user`/`do_signup` should verify tier1/tier2 delivery (or receipt of a drop event) before treating the signup as fully successful.

### Proof of Concept
1. Configure/observe a backend slowdown or a burst of signups such that queue length for tier 1 or tier 2 reaches `pcp_tier1_dropping_threshold`/`pcp_tier2_dropping_threshold`.
2. User A's tier-1/tier-2 PCP is enqueued and sits at the back of the queue as the oldest entry once other newer signups' packages are pushed.
3. A new signup (User B) pushes its PCP; since `queues[i].len() == dropping_thresholds[i]`, `drop_oldest()` is invoked, popping/deleting User A's oldest entry regardless of ownership. [7](#0-6) 
4. User A's package is deleted from disk/memory with no signal back to `plans/mod.rs`; the earlier signup is still reported `Status::Success` to the operator/user, while the tier1/tier2 custody data is permanently unrecoverable.

### Citations

**File:** src/agents/data_uploader.rs (L34-55)
```rust
pub enum Input {
    /// Push a personal-custody package to the upload queue.
    Pcp(Pcp),
    /// Wait for all queues to be not full.
    WaitQueues(oneshot::Sender<()>),
}

/// Personal-custody package to upload.
#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Pcp {
    /// Signup ID.
    pub signup_id: SignupId,
    /// User ID.
    pub user_id: String,
    /// Package contents.
    #[serde(skip)]
    pub data: Vec<u8>,
    /// Package checksum.
    pub checksum: Vec<u8>,
    /// Package tier.
    pub tier: u8,
}
```

**File:** src/agents/data_uploader.rs (L142-147)
```rust
                            let i = usize::from(pcp.tier - 1);
                            if queues[i].len() == dropping_thresholds[i] as usize {
                                queues[i].drop_oldest().await;
                            }
                            queues[i].push(pcp).await;
                            if uploaders.len() < PARALLEL_UPLOAD_STREAMS {
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
