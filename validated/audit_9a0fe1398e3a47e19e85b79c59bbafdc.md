### Title
Key Event Timeout Uses Block Height Instead of Timestamps, Causing Inaccurate DKG/Resharing Timeouts on NEAR - (File: `crates/contract/src/state/key_event.rs`)

---

### Summary

The `KeyEventInstance` struct tracks attempt timeouts using NEAR block heights (`BlockHeight`) rather than wall-clock timestamps. Because NEAR's block time is not constant, the actual wall-clock duration of a key event timeout is non-deterministic. This is a direct analog to the StreamingNFT vesting-period bug: both use block counts as a proxy for time on a chain with variable block production rates. The contract already contains a correct `Timestamp` abstraction backed by `env::block_timestamp()`, but it is not used for key event timeouts.

---

### Finding Description

`KeyEventInstance` stores two `BlockHeight` fields to bound the lifetime of a DKG or resharing attempt: [1](#0-0) 

The constructor computes the expiry as a block-count offset from the current block: [2](#0-1) 

Liveness checks compare the current block height against `expires_on`: [3](#0-2) [4](#0-3) 

The configurable parameter is named `key_event_timeout_blocks` with a default of 30 blocks: [5](#0-4) [6](#0-5) 

This timeout governs both DKG (`InitializingContractState::start`) and resharing (`ResharingContractState::start`): [7](#0-6) [8](#0-7) 

Meanwhile, the contract already has a correct timestamp abstraction that uses `env::block_timestamp()` (nanoseconds since Unix epoch), which is used for TEE-related deadlines but **not** for key event timeouts: [9](#0-8) 

---

### Impact Explanation

NEAR's block time targets ~1 second but is not guaranteed to be constant — it varies with validator performance and protocol upgrades. If NEAR begins producing blocks faster than the baseline assumed when `key_event_timeout_blocks` was configured:

- The 30-block window expires in fewer wall-clock seconds than intended.
- Participants may not have enough real time to complete the off-chain DKG or resharing protocol and submit their `vote_pk` / `vote_reshared` transactions before the on-chain attempt is considered expired.
- Every attempt times out, the leader must restart, and the cycle repeats indefinitely.

If the network is stuck in `InitializingContractState` (key generation) or `ResharingContractState` (resharing), it can never transition to `RunningContractState`. In the resharing case, the old epoch's keys remain in use but governance is frozen — no new participants can join, no key rotation can complete. This constitutes a **contract execution-flow manipulation that breaks production safety invariants** (the invariant being: a sufficient timeout window always exists for honest participants to complete the protocol).

**Impact: Medium** — breaks the key event lifecycle without requiring threshold collusion or privileged access.

---

### Likelihood Explanation

NEAR's block time has historically varied. Any future protocol upgrade that increases throughput, or any period of reduced validator latency, can shorten the real-time window represented by 30 blocks. The operator who sets `key_event_timeout_blocks` calibrates it against the current average block time; if that average changes after deployment, the timeout silently becomes too short. This is not a hypothetical: the same class of bug was observed and fixed in the StreamingNFT contract on Berachain for the same reason.

**Likelihood: Medium** — requires a meaningful shift in NEAR block production rate, which is plausible over the lifetime of a deployed contract.

---

### Recommendation

Replace the block-height-based timeout with a timestamp-based timeout using the existing `Timestamp` primitive:

1. Change `KeyEventInstance` fields from `BlockHeight` to `Timestamp` (using `crates/contract/src/primitives/time.rs`).
2. Replace `env::block_height() + 1 + timeout_blocks` with `Timestamp::now().checked_add(Duration::from_secs(timeout_seconds))`.
3. Rename `key_event_timeout_blocks` in `Config` to `key_event_timeout_seconds` and update the default to a wall-clock duration (e.g., 30 seconds).
4. Update `active()` and `current_key_event_id()` to compare `Timestamp::now()` against the stored expiry timestamp. [10](#0-9) 

---

### Proof of Concept

1. Deploy the contract with the default `key_event_timeout_blocks = 30`.
2. Assume NEAR is currently producing blocks at ~1 s/block → 30-block window ≈ 30 seconds.
3. A NEAR protocol upgrade or validator-set change causes blocks to be produced at ~0.5 s/block.
4. The leader calls `start_keygen` / `start_resharing`; `expires_on = current_block + 31`.
5. The off-chain DKG protocol requires ~20 seconds of network round-trips among MPC nodes.
6. At 0.5 s/block, 31 blocks elapse in ~15.5 seconds — before the DKG completes.
7. All `vote_pk` / `vote_reshared` calls arrive after `env::block_height() >= expires_on`, so `active()` returns `false` and every vote is rejected with `NoActiveKeyEvent`.
8. The leader restarts; the same race repeats. The contract is permanently stuck in `Initializing` or `Resharing` state. [11](#0-10) [5](#0-4)

### Citations

**File:** crates/contract/src/state/key_event.rs (L195-197)
```rust
        if instance.expires_on <= env::block_height() {
            return None;
        }
```

**File:** crates/contract/src/state/key_event.rs (L242-253)
```rust
pub struct KeyEventInstance {
    attempt_id: AttemptId,
    /// The block in which KeyEvent::start() was called.
    started_in: BlockHeight,
    /// The block that this attempt expires on. To clarify off-by-one behavior: if the contract were
    /// called *on* or after this height, the attempt is considered no longer existent.
    expires_on: BlockHeight,
    /// The participants that voted that they successfully completed the keygen or resharing.
    completed: BTreeSet<AuthenticatedParticipantId>,
    /// The public key currently voted for. This is None iff no one has voted.
    public_key: Option<PublicKeyExtended>,
}
```

**File:** crates/contract/src/state/key_event.rs (L256-271)
```rust
    pub fn new(attempt_id: AttemptId, timeout_blocks: u64) -> Self {
        KeyEventInstance {
            attempt_id,
            started_in: env::block_height(),
            expires_on: env::block_height() + 1 + timeout_blocks,
            completed: BTreeSet::new(),
            public_key: None,
        }
    }
    pub fn completed(&self) -> &BTreeSet<AuthenticatedParticipantId> {
        &self.completed
    }

    pub fn active(&self) -> bool {
        env::block_height() < self.expires_on
    }
```

**File:** crates/contract/src/config.rs (L4-5)
```rust
/// Default for `key_event_timeout_blocks`.
const DEFAULT_KEY_EVENT_TIMEOUT_BLOCKS: u64 = 30;
```

**File:** crates/contract/src/config.rs (L44-44)
```rust
    pub(crate) key_event_timeout_blocks: u64,
```

**File:** crates/contract/src/state/initializing.rs (L48-55)
```rust
    pub fn start(
        &mut self,
        key_event_id: KeyEventId,
        key_event_timeout_blocks: u64,
    ) -> Result<(), Error> {
        self.generating_key
            .start(key_event_id, key_event_timeout_blocks)
    }
```

**File:** crates/contract/src/state/resharing.rs (L99-106)
```rust
    pub fn start(
        &mut self,
        key_event_id: KeyEventId,
        key_event_timeout_blocks: u64,
    ) -> Result<(), Error> {
        self.resharing_key
            .start(key_event_id, key_event_timeout_blocks)
    }
```

**File:** crates/contract/src/primitives/time.rs (L1-25)
```rust
use std::time::Duration;

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub(crate) struct Timestamp {
    duration_since_unix_epoch: Duration,
}

impl Timestamp {
    pub(crate) fn now() -> Self {
        let block_time_nano_seconds = near_sdk::env::block_timestamp();

        Self {
            duration_since_unix_epoch: Duration::from_nanos(block_time_nano_seconds),
        }
    }

    pub(crate) fn checked_add(self, duration: Duration) -> Option<Self> {
        let current_time_stamp = self.duration_since_unix_epoch;
        let new_time_stamp = current_time_stamp.checked_add(duration)?;

        Some(Timestamp {
            duration_since_unix_epoch: new_time_stamp,
        })
    }
}
```
