The code is present and the logic is traceable. Here is the analysis:

---

### Title
Off-by-one in `valid_entries()` permanently includes the last-expired image hash in the allowed set — (`crates/contract/src/tee/proposal.rs`)

### Summary

`AllowedDockerImageHashes::valid_entries()` uses `rposition` to find the rightmost (most recently added) expired entry, then returns the slice `[cutoff_index..]`. Because the slice **starts at** `cutoff_index`, the expired entry at that index is always included in the returned valid set. A node running the expired image hash can therefore pass TEE authorization indefinitely after its grace period has elapsed.

### Finding Description

The vector `allowed_tee_proposals` is sorted oldest-first. `valid_entries` is supposed to return only non-expired entries (plus, by design, the single most-recently-expired entry when *all* entries have expired, to avoid an empty list). [1](#0-0) 

Trace for the two-entry case where only the oldest entry has expired:

| Index | `image_hash` | `grace_period_deadline` | Expired? |
|-------|-------------|------------------------|----------|
| 0 | H1 | T1 + D | **yes** |
| 1 | H2 | T2 + D | no |

`rposition` scans right-to-left:
- Index 1: predicate `grace_period_deadline < current_time` → **false** (not expired)
- Index 0: predicate → **true** (expired)
- Returns `Some(0)` → `cutoff_index = 0`

The slice `allowed_tee_proposals.get(0..)` returns **both** entries `[H1, H2]`. H1 is expired but is included.

The same flaw propagates through `cleanup_expired_hashes`, which calls `valid_entries` and replaces the internal vector with its result — so the expired entry is never actually removed from storage either. [2](#0-1) 

The correct slice when `rposition` returns `Some(i)` and `i + 1 < len` is `[i+1..]`. The `[i..]` form is only correct when all entries are expired (i.e., `i == len - 1`), to preserve the "always keep at least one" invariant.

The existing test `test_clean_expired` only exercises the all-expired case (it advances time past **both** entries' deadlines), so it does not catch this bug. [3](#0-2) 

### Impact Explanation

`get_allowed_mpc_docker_image_hashes` delegates directly to `valid_entries`: [4](#0-3) 

That list is passed to `attestation.verify_locally` inside `add_participant`: [5](#0-4) 

And to `re_verify` inside `reverify_participants`: [6](#0-5) 

`verify_mpc_hash` is a simple membership check: [7](#0-6) 

Because H1 is still in the list returned by `valid_entries`, a node presenting a valid TDX attestation for H1 passes `verify_mpc_hash`, its attestation is stored, and it remains an attested participant eligible to call `respond`/`respond_ckd`. The intended enforcement — that nodes must upgrade to a newer image within the grace period — is completely bypassed.

### Likelihood Explanation

This triggers in the normal upgrade flow: governance votes in a new image hash H2, H1's grace period elapses, but any node still running H1 can continue submitting fresh attestations and passing reverification. No special privileges, no collusion, and no network-level attack are required — only a NEAR account and a TDX node running the old image.

### Recommendation

Replace the unconditional `[cutoff_index..]` slice with logic that distinguishes the two cases:

```rust
let cutoff = self.allowed_tee_proposals
    .iter()
    .rposition(|e| {
        e.added.checked_add(tee_upgrade_deadline_duration)
            .map_or(true, |deadline| deadline < current_time)
    });

match cutoff {
    None => self.allowed_tee_proposals.clone(), // none expired → return all
    Some(i) if i + 1 == self.allowed_tee_proposals.len() => {
        // all expired → keep only the newest to avoid empty list
        self.allowed_tee_proposals[i..].to_vec()
    }
    Some(i) => {
        // some expired → exclude them; start from first non-expired entry
        self.allowed_tee_proposals[i + 1..].to_vec()
    }
}
```

Add a unit test that inserts two entries, advances time past only the first entry's deadline, and asserts the expired entry is **not** present in the result of `valid_entries`.

### Proof of Concept

```
T=0:   insert H1 (grace_period_deadline = T + 10 days)
T=5d:  insert H2 (grace_period_deadline = T + 10 days = day 15)
T=11d: H1 expired, H2 still valid
       call valid_entries():
         rposition finds index 0 (H1, last expired)
         returns proposals[0..] = [H1, H2]   ← H1 incorrectly included
       attacker submits attestation for H1
       verify_mpc_hash([H1, H2], H1) → Ok
       attacker stored as attested participant
       attacker calls respond/respond_ckd
```

### Citations

**File:** crates/contract/src/tee/proposal.rs (L170-193)
```rust
    fn valid_entries(&self, tee_upgrade_deadline_duration: Duration) -> Vec<AllowedMpcDockerImage> {
        let current_time = Timestamp::now();
        // get the index of the most recently enforced docker image
        let cutoff_index = self
            .allowed_tee_proposals
            .iter()
            .rposition(|allowed_docker_image| {
                let Some(grace_period_deadline) = allowed_docker_image
                    .added
                    .checked_add(tee_upgrade_deadline_duration)
                else {
                    log!("Error: timestamp overflowed when calculating grace_period_deadline.");
                    return true;
                };
                // if the grace period for this docker hash is in the past, then older hashes are no longer accepted
                grace_period_deadline < current_time
            })
            .unwrap_or(0);

        self.allowed_tee_proposals
            .get(cutoff_index..)
            .unwrap_or(&[])
            .to_vec()
    }
```

**File:** crates/contract/src/tee/proposal.rs (L197-200)
```rust
    pub fn cleanup_expired_hashes(&mut self, tee_upgrade_deadline_duration: Duration) {
        let valid_entries = self.valid_entries(tee_upgrade_deadline_duration);
        self.allowed_tee_proposals = valid_entries;
    }
```

**File:** crates/contract/src/tee/proposal.rs (L441-489)
```rust
    fn test_clean_expired() {
        let mut allowed = AllowedDockerImageHashes::default();
        let first_entry_time_nano_seconds = NANOS_IN_SECOND;

        testing_env!(
            VMContextBuilder::new()
                .block_timestamp(first_entry_time_nano_seconds)
                .build()
        );

        // Insert two proposals at different time intervals
        allowed.insert(dummy_code_hash(1), TEST_TEE_UPGRADE_DEADLINE_DURATION);

        let second_entry_time_nano_seconds = first_entry_time_nano_seconds + NANOS_IN_SECOND;
        testing_env!(
            VMContextBuilder::new()
                .block_timestamp(second_entry_time_nano_seconds)
                .build()
        );

        allowed.insert(dummy_code_hash(2), TEST_TEE_UPGRADE_DEADLINE_DURATION);

        let first_entry_expiry_time_nanoseconds = second_entry_time_nano_seconds
            + TEST_TEE_UPGRADE_DEADLINE_DURATION.as_nanos() as u64
            + 1;

        testing_env!(
            VMContextBuilder::new()
                .block_timestamp(first_entry_expiry_time_nanoseconds)
                .build()
        );

        allowed.cleanup_expired_hashes(TEST_TEE_UPGRADE_DEADLINE_DURATION);
        let proposals: Vec<_> = allowed.get(TEST_TEE_UPGRADE_DEADLINE_DURATION);

        // Only the second proposal should remain if the first is expired
        assert_eq!(proposals.len(), 1);
        assert_eq!(proposals[0].image_hash, dummy_code_hash(2));

        // Move block time far enough to expire both proposals. We always keep at least one
        // proposal in storage
        testing_env!(VMContextBuilder::new().block_timestamp(u64::MAX).build());

        allowed.cleanup_expired_hashes(TEST_TEE_UPGRADE_DEADLINE_DURATION);

        let proposals: Vec<_> = allowed.get(TEST_TEE_UPGRADE_DEADLINE_DURATION);

        assert_eq!(proposals.len(), 1);
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L166-175)
```rust
        let AcceptedAttestation {
            attestation: verified_attestation,
            advisory_ids,
        } = attestation.verify_locally(
            expected_report_data.into(),
            Self::current_time_seconds(),
            &self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration),
            &self.get_allowed_launcher_compose_hashes(),
            &accepted_measurements,
        )?;
```

**File:** crates/contract/src/tee/tee_state.rs (L211-231)
```rust
        let allowed_mpc_docker_image_hashes =
            self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration);
        let allowed_launcher_compose_hashes = self.get_allowed_launcher_compose_hashes();
        let allowed_measurements = self.get_accepted_measurements();

        let participant_attestation = self.stored_attestations.get(&node_id.tls_public_key);
        let Some(participant_attestation) = participant_attestation else {
            return TeeQuoteStatus::Invalid("participant has no attestation".to_string());
        };

        // Verify the attestation quote
        let time_stamp_seconds = Self::current_time_seconds();
        match participant_attestation.verified_attestation.re_verify(
            time_stamp_seconds,
            &allowed_mpc_docker_image_hashes,
            &allowed_launcher_compose_hashes,
            &allowed_measurements,
        ) {
            Ok(()) => TeeQuoteStatus::Valid,
            Err(err) => TeeQuoteStatus::Invalid(err.to_string()),
        }
```

**File:** crates/contract/src/tee/tee_state.rs (L287-295)
```rust
    pub fn get_allowed_mpc_docker_image_hashes(
        &self,
        tee_upgrade_deadline_duration: Duration,
    ) -> Vec<NodeImageHash> {
        self.get_allowed_mpc_docker_images(tee_upgrade_deadline_duration)
            .into_iter()
            .map(|entry| entry.image_hash)
            .collect()
    }
```

**File:** crates/mpc-attestation/src/attestation.rs (L431-450)
```rust
fn verify_mpc_hash(
    image_hash: &NodeImageHash,
    allowed_hashes: &[NodeImageHash],
) -> Result<(), VerificationError> {
    if allowed_hashes.is_empty() {
        return Err(VerificationError::Custom(
            "the allowed mpc image hashes list is empty".to_string(),
        ));
    }

    let image_hash_is_allowed = allowed_hashes.contains(image_hash);
    if !image_hash_is_allowed {
        return Err(VerificationError::Custom(format!(
            "MPC image hash {:?} is not in the allowed hashes list",
            image_hash
        )));
    }

    Ok(())
}
```
