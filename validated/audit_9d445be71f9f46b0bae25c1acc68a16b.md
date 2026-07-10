### Title
Stale `cancel_votes` Accumulate Across Domain Transitions in `InitializingContractState::vote_pk` — (`crates/contract/src/state/initializing.rs`)

### Summary

`cancel_votes: BTreeSet<AuthenticatedParticipantId>` lives on `InitializingContractState` and is **never cleared** when `vote_pk` advances `generating_key` from one domain to the next. The only replay-prevention guard in `vote_cancel` — the `next_domain_id` check — does not change between domain transitions within the same `InitializingContractState`, so a cancel vote cast during domain-0 keygen silently carries forward and can be combined with a fresh cancel vote cast during domain-1 keygen to reach the required threshold, triggering an unauthorized state transition.

---

### Finding Description

`InitializingContractState` holds:

```
cancel_votes: BTreeSet<AuthenticatedParticipantId>   // never reset
generating_key: KeyEvent                              // replaced per domain
``` [1](#0-0) 

When `vote_pk` collects enough success votes for the current domain it replaces `self.generating_key` with a fresh `KeyEvent` for the next domain, but leaves `cancel_votes` untouched:

```rust
self.generating_key = KeyEvent::new(
    self.epoch_id,
    next_domain.clone(),
    self.generating_key.proposed_parameters().clone(),
);
// cancel_votes is never cleared here
``` [2](#0-1) 

`vote_cancel` contains one guard intended to scope votes to the current keygen instance:

```rust
if next_domain_id != self.domains.next_domain_id() {
    return Err(InvalidParameters::NextDomainIdMismatch.into());
}
``` [3](#0-2) 

`DomainRegistry::next_domain_id` is a monotone counter that advances only when **new** domains are appended via `add_domains`. It does **not** change as `vote_pk` walks through the domains already registered in the current `InitializingContractState`. [4](#0-3) 

Therefore the `next_domain_id` guard is identical for every domain transition within the same `InitializingContractState`, and a cancel vote cast during domain-0 keygen passes the guard unchanged during domain-1 keygen.

The threshold check and transition:

```rust
if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
    let mut domains = self.domains.clone();
    domains.retain_domains(self.generated_keys.len());
    return Ok(Some(RunningContractState::new(...)));
}
``` [5](#0-4) 

`retain_domains` truncates the domain list to only the already-generated keys, permanently discarding all remaining domains while leaving `next_domain_id` advanced — those domain IDs are consumed and never reused. [6](#0-5) 

---

### Impact Explanation

With threshold = 2 and two new domains being initialized:

1. Participant A calls `vote_cancel(next_domain_id=N)` during domain-0 keygen → inserted into `cancel_votes` (count = 1, below threshold, no transition).
2. Domain-0 completes normally via `vote_pk`; `generating_key` is replaced with a fresh `KeyEvent` for domain-1; `cancel_votes` still contains A's entry.
3. Participant B calls `vote_cancel(next_domain_id=N)` during domain-1 keygen → inserted (count = 2 = threshold) → contract transitions to `Running` with only domain-0's key; domain-1 is permanently deleted.

The result: domain-1's `DomainId` is permanently consumed (`next_domain_id` was already advanced when the domains were registered), no key is ever generated for it, and the `Running` state has no entry for it. Any future signing requests targeting domain-1 are permanently unserviceable. Re-adding the domain requires a new `vote_add_domains` round that will assign a fresh, different `DomainId`.

The impact fits **Medium** — a production safety/accounting invariant (cancel requires threshold participants to agree *for the same domain*) is broken without direct fund loss, since domain-1 never held a key. It does not reach Critical because no existing key material is exposed, no signature is forged, and no funds already secured by a generated key are at risk.

---

### Likelihood Explanation

Requires exactly two colluding Byzantine participants (below threshold individually). No special timing beyond normal protocol operation is needed: participant A simply votes cancel during domain-0 keygen (which may fail to reach threshold and be ignored), waits for domain-0 to complete, and participant B votes cancel during domain-1 keygen. Both calls are ordinary contract transactions. No validator collusion, TEE compromise, or network-level attack is required.

---

### Recommendation

Reset `cancel_votes` whenever `vote_pk` advances `generating_key` to the next domain:

```rust
// inside vote_pk, after pushing to generated_keys and before creating the new KeyEvent:
self.cancel_votes.clear();
self.generating_key = KeyEvent::new(...);
``` [2](#0-1) 

This ensures cancel votes are scoped to the keygen attempt for a single domain, not the entire `InitializingContractState` lifetime.

---

### Proof of Concept

```
Setup: threshold = 2, participants = {A, B, C}, two new domains (domain-0, domain-1).

1. Leader starts domain-0 keygen.
2. Participant A calls vote_cancel(next_domain_id = N).
   → cancel_votes = {A}, len=1 < 2, no transition.
3. All participants call vote_pk for domain-0 with the same public key.
   → vote_pk sees all-voted, pushes domain-0 key, replaces generating_key with
      KeyEvent for domain-1. cancel_votes = {A} (unchanged).
4. Leader starts domain-1 keygen.
5. Participant B calls vote_cancel(next_domain_id = N).  // same N as step 2
   → cancel_votes = {A, B}, len=2 >= 2 → transition fires.
   → domains.retain_domains(1) → domain-1 deleted.
   → Running state returned with only domain-0's key.

Assert: running.keyset.domains.len() == 1
Assert: running.domains.domains().len() == 1
Assert: running.domains.next_domain_id() == N  // domain-1 ID consumed, no key
```

### Citations

**File:** crates/contract/src/state/initializing.rs (L30-43)
```rust
pub struct InitializingContractState {
    /// All domains, including the already existing ones and the ones we're generating a new key for
    pub domains: DomainRegistry,
    /// The epoch ID; this is the same as the Epoch ID of the Running state we transitioned from.
    pub epoch_id: EpochId,
    /// The key for each domain we have already generated a key for; this is in the same order as
    /// the domains in the DomainRegistry, except that it only has a prefix of the domains.
    pub generated_keys: Vec<KeyForDomain>,
    /// The key generation state for the currently generating domain (the next domain after
    /// `generated_keys`).
    pub generating_key: KeyEvent,
    /// Votes that have been cast to cancel the key generation.
    pub cancel_votes: BTreeSet<AuthenticatedParticipantId>,
}
```

**File:** crates/contract/src/state/initializing.rs (L86-91)
```rust
            if let Some(next_domain) = self.domains.get_domain_by_index(self.generated_keys.len()) {
                self.generating_key = KeyEvent::new(
                    self.epoch_id,
                    next_domain.clone(),
                    self.generating_key.proposed_parameters().clone(),
                );
```

**File:** crates/contract/src/state/initializing.rs (L121-123)
```rust
        if next_domain_id != self.domains.next_domain_id() {
            return Err(InvalidParameters::NextDomainIdMismatch.into());
        }
```

**File:** crates/contract/src/state/initializing.rs (L132-141)
```rust
        if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
            let mut domains = self.domains.clone();
            domains.retain_domains(self.generated_keys.len());
            return Ok(Some(RunningContractState::new(
                domains,
                Keyset::new(self.epoch_id, self.generated_keys.clone()),
                self.generating_key.proposed_parameters().clone(),
                AddDomainsVotes::default(),
            )));
        }
```

**File:** crates/contract/src/primitives/domain.rs (L109-118)
```rust
    fn add_domain(&mut self, domain: DomainConfig) -> DomainId {
        let assigned = DomainConfig {
            id: DomainId(self.next_domain_id),
            ..domain
        };
        self.next_domain_id += 1;
        let id = assigned.id;
        self.domains.push(assigned);
        id
    }
```

**File:** crates/contract/src/primitives/domain.rs (L141-143)
```rust
    pub fn retain_domains(&mut self, num_domains: usize) {
        self.domains.truncate(num_domains);
    }
```
