Looking at the exact code flow in `KeyEventInstance::vote_success` and `KeyEvent::vote_success`:

The code confirms this is a real vulnerability. Here is the complete analysis:

---

### Title
Committed Participant Can Bypass Duplicate-Vote Guard to Unilaterally Abort Any Active Key-Generation Instance — (`crates/contract/src/state/key_event.rs`)

### Summary

In `KeyEventInstance::vote_success`, the public-key disagreement check fires and returns early **before** the duplicate-vote guard is ever evaluated. A participant who has already cast a successful `vote_pk` call (and is therefore in `completed`) can call `vote_pk` again with a different `PublicKeyExtended` value, triggering `PublicKeyDisagreement`, which causes `KeyEvent::vote_success` to set `self.instance = None` and abort the active instance — bypassing the guard that was supposed to make committed votes irrevocable.

### Finding Description

The ordering bug is in `KeyEventInstance::vote_success`: [1](#0-0) 

```
1. Check public_key vs self.public_key  →  if mismatch, return PublicKeyDisagreement  (line 297)
2. Check completed.contains(&candidate) →  if duplicate, return VoteAlreadySubmitted  (line 304)
```

Step 1 returns early before Step 2 is ever reached. If participant P already voted `K1` (so `self.public_key = Some(K1)` and `P ∈ completed`), and P now calls `vote_pk(K2)` where `K2 ≠ K1`:

- Line 296: `K1 != K2` → `return Ok(VoteSuccessResult::PublicKeyDisagreement)` — **early return**
- Line 303: `completed.contains(&P)` — **never evaluated**

The caller `KeyEvent::vote_success` then handles `PublicKeyDisagreement` by unconditionally nulling the instance: [2](#0-1) 

This aborts the entire attempt, forcing the leader to call `start()` again and incrementing `next_attempt_id`.

The `verify_vote` helper that runs before `vote_success` only checks that the signer is a valid participant and that the `key_event_id` matches the active attempt — it does **not** check whether the participant already voted: [3](#0-2) 

**Scope note — resharing is not affected.** `ResharingContractState::vote_reshared` passes `previous_key.key.clone()` (a contract-determined value) as the public key, so all callers submit the same key and `PublicKeyDisagreement` cannot be triggered by a caller-controlled input: [4](#0-3) 

The vulnerability is confined to `vote_pk` / `InitializingContractState::vote_pk`: [5](#0-4) 

### Impact Explanation

A single Byzantine participant (below the signing threshold) who has already committed a success vote can:

1. Call `vote_pk` again with any different `PublicKeyExtended` value.
2. Trigger `PublicKeyDisagreement`, aborting the active instance.
3. Repeat this every time the leader starts a new attempt.

This permanently stalls key generation for any domain in `InitializingContractState`. No keys can be generated, and the contract cannot transition to `RunningContractState`, breaking the production key-generation lifecycle invariant.

### Likelihood Explanation

The attacker must be a registered, TEE-attested participant — not a random user. However, the threshold for harm is a **single** participant (not a threshold-sized coalition), making this exploitable by any one compromised or malicious node. The call is a normal contract transaction with no special privileges beyond being a participant.

### Recommendation

Swap the order of checks in `KeyEventInstance::vote_success`: evaluate `completed.contains(&candidate)` **first** and return `VoteAlreadySubmitted` before comparing public keys. A participant who has already committed must be rejected unconditionally, regardless of what key they now submit.

```rust
fn vote_success(
    &mut self,
    candidate: AuthenticatedParticipantId,
    public_key: PublicKeyExtended,
) -> Result<VoteSuccessResult, Error> {
    // Guard must come first: a committed participant cannot change or re-trigger anything.
    if self.completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    if let Some(existing_public_key) = &self.public_key {
        if existing_public_key != &public_key {
            return Ok(VoteSuccessResult::PublicKeyDisagreement);
        }
    } else {
        self.public_key = Some(public_key);
    }
    self.completed.insert(candidate.clone());
    Ok(VoteSuccessResult::Voted(self.completed.len()))
}
```

### Proof of Concept

The existing test suite in `initializing.rs` already partially documents the disagreement path (lines 266–276) but never tests the case where the *same* participant votes twice with different keys. A deterministic unit test:

1. Start a `KeyEventInstance` with participants `[P1, P2, P3]`.
2. Have `P1` call `vote_pk(K1)` → succeeds, `P1 ∈ completed`, `public_key = K1`.
3. Have `P1` call `vote_pk(K2)` where `K2 ≠ K1` → currently returns `Ok(false)` and sets `instance = None`.
4. Assert `instance.is_none()` — the attempt was aborted by an already-committed participant.
5. Assert that `vote_abort` from `P1` would have returned `VoteAlreadySubmitted` (proving the abort path is blocked but the key-disagreement path is not). [6](#0-5)

### Citations

**File:** crates/contract/src/state/key_event.rs (L135-139)
```rust
            VoteSuccessResult::PublicKeyDisagreement => {
                log!("Public key disagreement; aborting key event instance.");
                self.instance = None;
                Ok(false)
            }
```

**File:** crates/contract/src/state/key_event.rs (L173-189)
```rust
    fn verify_vote(
        &mut self,
        key_event_id: &KeyEventId,
    ) -> Result<AuthenticatedParticipantId, Error> {
        let candidate = AuthenticatedParticipantId::new(self.parameters.participants())?;
        self.cleanup_if_timed_out();
        let Some(instance) = self.instance.as_ref() else {
            return Err(KeyEventError::NoActiveKeyEvent.into());
        };
        if key_event_id.epoch_id != self.epoch_id
            || key_event_id.domain_id != self.domain.id
            || key_event_id.attempt_id != instance.attempt_id
        {
            return Err(KeyEventError::KeyEventIdMismatch.into());
        }
        Ok(candidate)
    }
```

**File:** crates/contract/src/state/key_event.rs (L290-309)
```rust
    fn vote_success(
        &mut self,
        candidate: AuthenticatedParticipantId,
        public_key: PublicKeyExtended,
    ) -> Result<VoteSuccessResult, Error> {
        if let Some(existing_public_key) = &self.public_key {
            if existing_public_key != &public_key {
                return Ok(VoteSuccessResult::PublicKeyDisagreement);
            }
        } else {
            self.public_key = Some(public_key);
        }
        // return error if the candidate alredy submitted a vote.
        if self.completed.contains(&candidate) {
            return Err(VoteError::VoteAlreadySubmitted.into());
        }
        // label candidate as complete
        self.completed.insert(candidate.clone());
        Ok(VoteSuccessResult::Voted(self.completed.len()))
    }
```

**File:** crates/contract/src/state/resharing.rs (L125-129)
```rust
        let previous_key = self.previous_keyset().domains[self.reshared_keys.len()].clone();
        if self
            .resharing_key
            .vote_success(&key_event_id, previous_key.key.clone())?
        {
```

**File:** crates/contract/src/state/initializing.rs (L77-80)
```rust
        if self
            .generating_key
            .vote_success(&key_event_id, public_key.clone())?
        {
```
