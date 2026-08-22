### Title
Unconditional Persistent→Memory queue switch on SSD I/O failure orphans undeleted, unrouted Personal Custody Package (biometric) data on device storage - (File: src/agents/data_uploader.rs)

### Summary
`Queue::commit`, `Queue::pop`, and `Queue::push` in the data-uploader agent perform a filesystem operation against the on-disk persistent queue and, on any I/O failure, unconditionally discard the persistent state and replace it with a fresh in-memory queue via `*self = Self::new_memory()`. This mirrors the `updateYieldStrategy` bug class: a state transition proceeds unconditionally even though the underlying withdrawal/cleanup operation (here, deleting an uploaded package's directory, or reading a queued package back from disk) did not complete, leaving assets ("Personal Custody Package" biometric data) behind and permanently unreachable by the new state.

### Finding Description
The `Queue` enum tracks Personal Custody Packages (PCPs) — encrypted biometric bundles containing iris codes, iris images, normalized iris data, and face embeddings — either in memory or persisted on the SSD as directories keyed by numeric id [1](#0-0) .

In `commit`, after a package has been uploaded, the code attempts `fs::remove_dir_all` for the corresponding on-disk directory. If that fails, instead of retrying or preserving the remaining queue state, it unconditionally replaces the whole `Persistent` state with `Self::new_memory()`, discarding the in-memory `queue: VecDeque<u64>` of ids still awaiting deletion/upload tracking: [2](#0-1) 

The same unconditional-switch pattern exists in `pop` (discarding the remaining `queue` of not-yet-popped ids on a read failure) and in `push` (discarding the `next_id`/tracking state on a write failure), while the actual files that were already written to `path` are never revisited or cleaned up once the enum variant becomes `Memory`: [3](#0-2) 

Because the switch to `Memory` is permanent for the life of the agent (there is no code path that re-opens the `path` directory once `Persistent` has been abandoned), any PCP directories still present under `path` — including ones referenced by the discarded `queue` ids — are never uploaded and never deleted. This is directly analogous to `updateYieldStrategy` in the referenced report: a fallible sub-operation (`withdrawAll` / `remove_dir_all`/`read_to_string`) is not verified to fully succeed before the code unconditionally transitions to a new state (`new strategy` / `Queue::Memory`), stranding the remaining assets (funds / biometric package files) under the old, now-unreachable state (old strategy / abandoned `path`).

The PCP payload pushed into this queue is the encrypted biometric enrollment package built in `src/plans/personal_custody_package.rs`, containing iris codes, normalized iris images/masks, and face embeddings, tied to a specific `signup_id`/`user_id` [4](#0-3) .

### Impact Explanation
Encrypted biometric enrollment data (Personal Custody Packages) that is supposed to be either successfully uploaded to the backend and deleted from local storage, or retried until it can be, instead becomes permanently orphaned on the orb's local SSD whenever a transient filesystem error coincides with an in-flight persistent queue operation. This violates the intended biometric data retention lifecycle: data that should be transient on the device persists indefinitely, unmonitored and unmanaged by any queue logic, increasing the exposure window for that biometric data on a device that is also subject to field servicing, repair, and physical handling. It is a concrete violation of biometric upload/retention guarantees, matching the "frozen funds" pattern described in the source report where a partial failure combined with an unconditional state switch leaves protected assets stuck and disconnected from the system that is supposed to manage them.

### Likelihood Explanation
The trigger condition (an SSD/filesystem I/O failure during `remove_dir_all`, `read_to_string`/`read`, or `write` while packages are queued) is not attacker-controlled and can occur during normal operation under storage pressure, wear, or transient I/O errors — the `ssd::perform_async` wrapper strongly suggests this class of failure is anticipated and handled elsewhere in the codebase for exactly this reason. Given that every signup produces PCP tier uploads that flow through this queue, and the switch-to-memory fallback exists specifically to handle disk failures, this is a realistically reachable path during ordinary device operation.

### Recommendation
On a persistent-queue operation failure, do not silently discard queue state and switch to `Memory`. Instead:
- Preserve any ids/queue entries that have not been confirmed deleted/uploaded rather than dropping them via `Self::new_memory()`.
- On `commit` failure, keep the id in a "pending deletion" set and retry cleanup, rather than losing track of it.
- On `pop`/`push` failure, avoid abandoning the entire persistent directory; consider surfacing the error so an explicit reconciliation/deletion pass can run, or scan and delete/re-ingest orphaned directories in `Queue::new` at agent start.

### Proof of Concept
1. Start a signup and let a PCP tier be pushed to the persistent queue (`Queue::push`) and successfully written to disk.
2. Have the SSD reject the delete operation during `commit` (e.g., simulate `fs::remove_dir_all` failure) right after a successful upload.
3. Observe `*self = Self::new_memory()` executes: the `queue: VecDeque<u64>` of any other still-persisted, not-yet-uploaded PCP ids is dropped, and the just-uploaded package's directory (whose deletion failed) remains on disk.
4. No further code path ever revisits `path`; the orphaned PCP directories (containing encrypted iris/face biometric package data) remain on the SSD indefinitely, outside of any upload/retention tracking, as shown by the absence of any post-switch usage of `path` in `Queue::Memory` handling [5](#0-4) .

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

**File:** src/agents/data_uploader.rs (L220-341)
```rust
impl Queue {
    fn new_memory() -> Self {
        Self::Memory { queue: VecDeque::new() }
    }

    #[allow(dead_code)]
    async fn new(path: PathBuf) -> Self {
        let ssd_perform = ssd::perform_async(async {
            fs::create_dir_all(&path).await?;
            let mut ids = BTreeSet::new();
            let mut read_dir = fs::read_dir(&path).await?;
            while let Some(entry) = read_dir.next_entry().await? {
                if let Some(name) = entry.path().file_name() {
                    if let Ok(id) = name.to_string_lossy().parse::<u64>() {
                        assert!(ids.insert(id), "duplicate entry in data uploader directory");
                    } else {
                        tracing::error!(
                            "Data uploader directory contains a non-integer entry: {name:?}",
                        );
                        return Ok(None);
                    }
                }
            }
            Ok(Some(ids.into_iter().collect::<VecDeque<_>>()))
        });
        match ssd_perform.await {
            None | Some(None) => Self::new_memory(),
            Some(Some(queue)) => {
                let next_id =
                    queue.back().map_or(0, |id| id.checked_add(1).expect("shouldn't grow so fast"));
                Self::Persistent { path, queue, next_id, in_progress: 0 }
            }
        }
    }

    fn len(&self) -> usize {
        match self {
            Self::Memory { queue } => queue.len(),
            Self::Persistent { queue, .. } => queue.len(),
        }
    }

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

**File:** src/plans/personal_custody_package.rs (L41-55)
```rust
    pub signup_id: SignupId,
    pub identification_image_ids: IdentificationImages,
    pub capture: biometric_capture::Capture,
    pub pipeline: Pipeline,
    pub credentials: Credentials,
    pub signup_reason: SignupReason,
    pub location_data: LocationData,
}

/// The credentials used to build the personal custody package.
#[allow(missing_docs)]
#[allow(clippy::struct_field_names)]
pub struct Credentials {
    pub operator_qr_code: qr_scan::user::Data,
    pub user_qr_code: qr_scan::user::Data,
```
