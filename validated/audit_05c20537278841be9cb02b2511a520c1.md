### Title
Persistent PCP upload queue resets its ID counter while older entries are still queued, causing cross-signup biometric-package ID collisions - (File: src/agents/data_uploader.rs)

### Summary
The Reserve Protocol report describes a class of bug where a piece of mutable counter/limit state (`totalSupply`) is reset/changed based on a *local* view of in-flight state, without accounting for other outstanding queued operations, letting an attacker exploit the mismatch to redirect value that should belong to one party to another. The analogous pattern in `orb-core` is the personal-custody-package (PCP) upload queue's `Queue::commit()` logic in `src/agents/data_uploader.rs`, where the on-disk directory-ID counter (`next_id`) is reset to `0` purely based on `in_progress == 0`, without checking whether the `queue: VecDeque<u64>` still holds unpopped entries with higher, already-assigned IDs from a *different* signup.

### Finding Description
The persistent queue variant stores each pending personal-custody package (containing biometric data: iris codes, iris masks, face images, etc., see `Pcp` struct at [1](#0-0) ) on disk under a directory named by a monotonically incrementing `next_id`.

`push()` assigns the current `next_id` to a new PCP package and increments the counter: [2](#0-1) 

`pop()` removes an ID from the front of `queue` and reads back the on-disk package, incrementing `in_progress`: [3](#0-2) 

`commit()` is called after a package finishes uploading; it decrements `in_progress` and, critically, resets `next_id` back to `0` **solely because `in_progress` reached zero** — with no check on whether `queue` (the list of already-assigned-but-not-yet-popped IDs) is empty: [4](#0-3) 

Sequence that produces a collision (analogous to the Reserve bug's "state reset while other operations are still outstanding, then hot-swapped"):
1. Two PCP packages are pushed: IDs `0` and `1` are assigned (`next_id` becomes `2`); `queue = [0, 1]`.
2. `pop()` is called, taking ID `0` off the front of `queue` (`queue = [1]`), and `in_progress = 1`.
3. Upload of ID `0` completes; `commit(0)` runs. `in_progress` drops to `0`, so **`next_id` is reset to `0`**, even though `queue` still contains the un-popped entry `1` (which belongs to a different signup/PCP package still sitting on disk in directory `1`).
4. Two new pushes occur before ID `1` is popped (e.g., a fast subsequent signup, or tier-1/tier-2 packages for the same signup queued rapidly as in `do_signup`'s handling of `packages.tier1`/`packages.tier2`, see [5](#0-4) ). The first new push reuses ID `0` (harmless, `0` was already removed). The **second** new push reuses ID `1`, calling `fs::write(path.join("1")/meta.json, ...)` and overwriting the on-disk `meta.json`/`data.bin` for the still-queued, not-yet-uploaded package belonging to the *original* signup.
5. When the original queue entry `1` is eventually popped and uploaded (`upload_pcp`), it will read the **overwritten** files — i.e., a completely different signup's biometric package (data, checksum, `signup_id`, `user_id`) gets uploaded as tier N of the wrong signup, while the package that was legitimately queued under ID `1` is silently lost/corrupted.

This is directly analogous to the Reserve bug's root cause: a counter (`totalSupply` / `next_id`) that gates or indexes a subsequent privileged action is reset/manipulated based on incomplete state (ignoring outstanding queued/in-flight items), letting one flow's action consume or overwrite state that rightfully belongs to another flow.

### Impact Explanation
If triggered, this results in unauthorized biometric-data disclosure/misattribution between different signups: a personal-custody package (containing raw iris codes/images and a `user_id`/`signup_id`) belonging to one signup can be silently overwritten by, or attributed to, a different signup's upload slot. This is a concrete cross-signup state bleed of biometric data as flagged in the allowed impact categories, since the backend would then receive tier data tagged to the wrong `signup_id`/`user_id`, potentially uploading the wrong custody package under someone else's signup, or corrupting/losing a legitimate one.

### Likelihood Explanation
Exploitability depends on how frequently the persistent queue's `in_progress` count can drop to `0` while other IDs remain queued but unpopped — this requires either upload throughput exceeding push throughput momentarily or bursts of near-simultaneous pushes/pops (e.g., tier0/tier1/tier2 packages queued in quick succession per signup, and multiple concurrent signups). I could not fully verify from static analysis whether the `Persistent` queue variant is actually constructed in the running production code path — the `Persistent` variant and its `new()` constructor are both marked `#[allow(dead_code)]` in the source I reviewed, and I found no call site instantiating `Queue::new(path)` outside of the unit tests in this file. Grepping the codebase, `Queue::Persistent`/`Queue::new(` appear only within `src/agents/data_uploader.rs` itself; I was not able to confirm from the indexed code whether some other file (not fully covered by the search index) wires this into `Agent::run`'s `queues` array with `Queue::new(path).await` instead of `Queue::new_memory()`. This is a material uncertainty that affects whether this is reachable in the shipped binary — if the memory-only queue is what's actually used in production, this specific bug is not exploitable, though the code path exists and is exercised by the persistent-queue unit tests (`test_persistent_queue`).

### Recommendation
In `Queue::commit()`, only reset `next_id` to `0` when **both** `in_progress == 0` **and** `queue.is_empty()` (i.e., no assigned-but-unconsumed IDs remain). Alternatively, remove the ID-recycling optimization entirely and let `next_id` grow monotonically (as already guarded by the `checked_add` overflow assertion in `push()`), eliminating any possibility of directory-ID reuse colliding with an outstanding queued entry.

### Proof of Concept
Extend the existing `test_persistent_queue` test in `src/agents/data_uploader.rs` ( [6](#0-5) ) as follows:
1. `push` two PCPs (IDs `0`, `1` assigned).
2. `pop` ID `0`, then `commit(0)` — this drives `in_progress` to `0` and resets `next_id` to `0` while `queue` still holds `[1]`.
3. `push` two more distinct PCPs (e.g., payloads `"A"` and `"B"`), which will be assigned IDs `0` and `1` respectively by the reset counter.
4. Assert that the on-disk `meta.json`/`data.bin` at path `1` now contains payload `"B"`, silently clobbering the still-queued original package (formerly ID `1`), demonstrating the collision and data loss/misattribution.

### Citations

**File:** src/agents/data_uploader.rs (L42-55)
```rust
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

**File:** src/agents/data_uploader.rs (L262-290)
```rust
    async fn push(&mut self, pcp: Pcp) {
        match self {
            Self::Memory { queue } => {
                queue.push_back(pcp);
            }
            Self::Persistent { path, queue, next_id, .. } => {
                let ssd_perform = ssd::perform_async(async {
                    let path = path.join(next_id.to_string());
                    let meta = serde_json::to_string(&pcp)?;
                    fs::create_dir_all(&path).await?;
                    fs::write(path.join("meta.json"), meta).await?;
                    fs::write(path.join("data.bin"), &pcp.data).await?;
                    Ok(())
                });
                match ssd_perform.await {
                    None => {
                        tracing::error!(
                            "Persistent queue is failed during push, switching to memory"
                        );
                        *self = Self::Memory { queue: vec![pcp].into() };
                    }
                    Some(()) => {
                        queue.push_back(*next_id);
                        *next_id = next_id.checked_add(1).expect("shouldn't grow so fast");
                    }
                }
            }
        }
    }
```

**File:** src/agents/data_uploader.rs (L292-319)
```rust
    async fn pop(&mut self) -> Option<(Pcp, u64)> {
        match self {
            Self::Memory { queue } => queue.pop_front().map(|pcp| (pcp, 0)),
            Self::Persistent { path, queue, in_progress, .. } => {
                let id = queue.pop_front()?;
                let ssd_perform = ssd::perform_async(async {
                    let path = path.join(id.to_string());
                    let meta = fs::read_to_string(path.join("meta.json")).await?;
                    let mut pcp = serde_json::from_str::<Pcp>(&meta)?;
                    pcp.data = fs::read(path.join("data.bin")).await?;
                    Ok(pcp)
                });
                match ssd_perform.await {
                    None => {
                        tracing::error!(
                            "Persistent queue is failed during pop, switching to memory"
                        );
                        *self = Self::new_memory();
                        None
                    }
                    Some(pcp) => {
                        *in_progress += 1;
                        Some((pcp, id))
                    }
                }
            }
        }
    }
```

**File:** src/agents/data_uploader.rs (L321-341)
```rust
    async fn commit(&mut self, id: u64) {
        match self {
            Self::Memory { .. } => {}
            Self::Persistent { path, next_id, in_progress, .. } => {
                *in_progress = in_progress.checked_sub(1).expect("shouldn't go negative");
                match ssd::perform_async(fs::remove_dir_all(path.join(id.to_string()))).await {
                    None => {
                        tracing::error!(
                            "Persistent queue is failed during commit, switching to memory"
                        );
                        *self = Self::new_memory();
                    }
                    Some(()) => {
                        if *in_progress == 0 {
                            *next_id = 0;
                        }
                    }
                }
            }
        }
    }
```

**File:** src/agents/data_uploader.rs (L426-537)
```rust
    #[allow(clippy::too_many_lines)]
    #[tokio::test]
    async fn test_persistent_queue() {
        let tempdir = tempdir().unwrap();
        let mut queue = Queue::new(tempdir.path().to_path_buf()).await;
        assert!(matches!(queue, Queue::Persistent { .. }));
        queue
            .push(Pcp {
                signup_id: SignupId::default(),
                user_id: "test".to_string(),
                data: vec![1, 2, 3],
                checksum: vec![4, 5, 6],
                tier: 0,
            })
            .await;
        queue
            .push(Pcp {
                signup_id: SignupId::default(),
                user_id: "test".to_string(),
                data: vec![7, 8, 9],
                checksum: vec![10, 11, 12],
                tier: 0,
            })
            .await;
        assert_eq!(
            queue.pop().await,
            Some((
                Pcp {
                    signup_id: SignupId::default(),
                    user_id: "test".to_string(),
                    data: vec![1, 2, 3],
                    checksum: vec![4, 5, 6],
                    tier: 0,
                },
                0
            ))
        );
        assert_eq!(
            queue.pop().await,
            Some((
                Pcp {
                    signup_id: SignupId::default(),
                    user_id: "test".to_string(),
                    data: vec![7, 8, 9],
                    checksum: vec![10, 11, 12],
                    tier: 0,
                },
                1
            ))
        );
        assert_eq!(queue.pop().await, None);

        // Uncommited changes, simulating a crash.
        let mut queue = Queue::new(tempdir.path().to_path_buf()).await;
        assert_eq!(
            queue.pop().await,
            Some((
                Pcp {
                    signup_id: SignupId::default(),
                    user_id: "test".to_string(),
                    data: vec![1, 2, 3],
                    checksum: vec![4, 5, 6],
                    tier: 0,
                },
                0
            ))
        );
        assert_eq!(
            queue.pop().await,
            Some((
                Pcp {
                    signup_id: SignupId::default(),
                    user_id: "test".to_string(),
                    data: vec![7, 8, 9],
                    checksum: vec![10, 11, 12],
                    tier: 0,
                },
                1
            ))
        );
        assert_eq!(queue.pop().await, None);
        queue.commit(0).await;
        queue.commit(1).await;
        queue
            .push(Pcp {
                signup_id: SignupId::default(),
                user_id: "test".to_string(),
                data: vec![13, 14, 15],
                checksum: vec![16, 17, 18],
                tier: 0,
            })
            .await;
        assert_eq!(
            queue.pop().await,
            Some((
                Pcp {
                    signup_id: SignupId::default(),
                    user_id: "test".to_string(),
                    data: vec![13, 14, 15],
                    checksum: vec![16, 17, 18],
                    tier: 0,
                },
                0
            ))
        );
        queue.commit(0).await;

        // The directory should be empty now.
        let mut queue = Queue::new(tempdir.path().to_path_buf()).await;
        assert_eq!(queue.pop().await, None);
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
