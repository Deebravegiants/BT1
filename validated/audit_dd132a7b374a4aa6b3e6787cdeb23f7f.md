### Title
`ensure_enough_space` evicts oldest SSD signup directory purely by creation time, deleting not-yet-uploaded biometric data - (File: src/agents/image_notary.rs)

### Summary
`ensure_enough_space` in `src/agents/image_notary.rs` frees SSD space by walking `DATA_ACQUISITION_BASE_DIR`, picking the single oldest top-level directory by filesystem creation time, and unconditionally calling `fs::remove_dir_all` on it. It has no concept of "uploaded/finalized-and-acknowledged" vs "pending upload", so a signup directory that has completed capture (`finalize_signup` wrote identification images/custody evidence) but has not yet been picked up by the uploader agent is just as eligible for eviction as any stale leftover directory.

### Finding Description
`ensure_enough_space` is invoked at the start of every new signup, before `initialize_signup` creates the new signup's directory: [1](#0-0) 

Its eviction loop only compares directory creation timestamps and deletes the oldest one it finds, with zero check of whether that directory has already been uploaded/acknowledged by `image_uploader`, or is still awaiting upload: [2](#0-1) 

Because the orb device only supports one active signup at a time (the agent thread's outer loop blocks on `InitializeSignup` and processes captures sequentially), an attacker cannot make their *own* concurrent capture collide with another user's in-progress capture. However, `finalize_signup` writes the completed signup's identification images/custody evidence to disk and returns without waiting for or recording an "uploaded" marker: [3](#0-2) 

That directory then sits in `DATA_ACQUISITION_BASE_DIR` until the separate `image_uploader` agent eventually uploads and removes it — which can be delayed by network conditions outside the attacker's control. If an attacker repeatedly performs their own (real, physically-presented) signups in quick succession, SSD usage grows and `ensure_enough_space` triggers before earlier, still-unuploaded signups (which could belong to other users, or even the attacker's own earlier finalized-but-not-yet-uploaded signup evidence) have been uploaded. Since eviction is strictly creation-time based with no upload-status gate, the oldest pending (not-yet-uploaded) directory — not necessarily the attacker's own — gets `remove_dir_all`'d, permanently destroying that signup's identification images/custody evidence before it can ever reach the backend.

No other check in this file (or `src/ssd.rs::perform`, which only gates on SSD mount/failure state) restores or protects unuploaded directories from this eviction path.

### Impact Explanation
This breaks the invariant that biometric identification images and self-custody evidence must be retained until successfully uploaded/acknowledged per policy. An unprivileged attacker who can only initiate their own physical signups can nonetheless cause permanent, unrecoverable loss of another (or their own) still-pending signup's biometric evidence, before the backend ever verifies or archives it. This maps to a data-integrity / data-loss impact under the Worldcoin/Orb bounty categories (loss of custody evidence / retention-policy violation), since the deletion is irreversible and defeats the purpose of local retention pending upload.

### Likelihood Explanation
Preconditions: attacker must be able to physically trigger multiple real signups in succession on the orb (no privileged access required) while the SSD is close to `MIN_AVAILABLE_SSD_SPACE_BEFORE_SIGNUP`, and while at least one other signup's directory is still unuploaded (e.g., due to network latency/outage or upload backlog). Given that upload is asynchronous and independent of capture rate, an attacker capable of performing signups faster than the uploader can drain the backlog can reliably trigger this condition. The exploit requires no cryptographic bypass, no MCU access, and no social engineering — only repeated legitimate use of the signup flow, making it moderately feasible and fully repeatable.

### Recommendation
Track upload/acknowledgement state per signup directory (e.g., a sentinel file or metadata written by `image_uploader` upon successful upload) and have `ensure_enough_space` only consider directories marked as uploaded/finalized-and-acked as eviction candidates. If no such directory exists, the function should refuse to evict (fail closed) rather than deleting the oldest pending, not-yet-uploaded signup.

### Proof of Concept
Integration test plan:
1. Create `DATA_ACQUISITION_BASE_DIR` with two subdirectories representing two different `SignupId`s, both containing sample identification image files, with distinct `created` timestamps (e.g., using `filetime::set_file_times` to backdate one).
2. Mark one directory as "uploaded" (write a sentinel/marker, or simulate via whatever mechanism `image_uploader` would use) and leave the other as "pending" (no marker), asserting the pending one is strictly older via metadata.
3. Set `ssd::available_space()` (test cfg returns `MIN_AVAILABLE_SSD_SPACE_BEFORE_SIGNUP`) to a value forcing `ensure_enough_space`'s while-loop condition to trigger eviction.
4. Call `ensure_enough_space()` and assert that:
   - The uploaded/finalized directory is the one removed (or, with a fix, only uploaded directories are eligible), and
   - The pending (not-yet-uploaded) signup directory of the "other user" survives.
5. Without a fix, the current implementation will remove strictly the oldest-by-creation-time directory regardless of upload status, demonstrating that a still-pending signup's identification images can be destroyed — proving the vulnerability.

### Citations

**File:** src/agents/image_notary.rs (L288-298)
```rust
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

**File:** src/agents/image_notary.rs (L364-376)
```rust
    #[cfg(feature = "internal-data-acquisition")]
    fn finalize_signup(&mut self) -> Result<()> {
        ssd_save_png(|| {
            save_sharpest_frames(
                &self.sharpest_frames,
                &self.signup_id,
                &self.save_dir,
                &mut self.log,
            )?;
            Ok(())
        })?;
        Ok(())
    }
```

**File:** src/agents/image_notary.rs (L930-978)
```rust
fn ensure_enough_space() -> Result<()> {
    while ssd::available_space() < MIN_AVAILABLE_SSD_SPACE_BEFORE_SIGNUP {
        let mut oldest_entry_path = None;
        let mut oldest_entry_created = None;
        ssd::perform(|| {
            if let Err(e) = std::fs::create_dir_all(Path::new(DATA_ACQUISITION_BASE_DIR)) {
                tracing::error!(
                    "Failed to create {DATA_ACQUISITION_BASE_DIR} (ssd stats: {:?}, is mounted: \
                     {}): {e}",
                    ssd::stats(),
                    ssd::is_mounted()
                );
                Err(e)
            } else {
                Ok(())
            }
        });
        for entry in WalkDir::new(DATA_ACQUISITION_BASE_DIR).min_depth(1).max_depth(1) {
            let Ok(entry) = entry else {
                tracing::error!(
                    "walking: {DATA_ACQUISITION_BASE_DIR} failed (ssd stats: {:?}, is mounted: {})",
                    ssd::stats(),
                    ssd::is_mounted()
                );
                return Ok(());
            };
            let entry_created = entry.metadata()?.created()?;
            if oldest_entry_created.map_or(true, |oldest| entry_created < oldest) {
                oldest_entry_created = Some(entry_created);
                oldest_entry_path = Some(entry.path().to_owned());
            }
        }
        if let (Some(oldest_entry_path), Some(oldest_entry_created)) =
            (oldest_entry_path, oldest_entry_created)
        {
            tracing::info!(
                "Removing signup dir {} created at {}",
                oldest_entry_path.display(),
                OffsetDateTime::from(oldest_entry_created).format(&Rfc2822)?,
            );
            dd_incr!("main.count.data_acquisition.cleanups");
            fs::remove_dir_all(oldest_entry_path)?;
        } else {
            tracing::error!(
                "Not enough space on the SSD while {DATA_ACQUISITION_BASE_DIR} is empty"
            );
            break;
        }
    }
```
