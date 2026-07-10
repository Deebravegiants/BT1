### Title
Byzantine Equivocation via Zero Echo/Ready Thresholds at n=3 Causes Silent DKG Key Inconsistency — (`crates/threshold-signatures/src/protocol/echo_broadcast.rs`)

---

### Summary

`echo_ready_thresholds(3)` returns `(0, 0)`, collapsing the echo-broadcast protocol's equivocation protection entirely for the minimum allowed deployment size. A single Byzantine DKG participant can send two different `Send` messages to the two honest nodes in Round 2 (commitments), causing each honest node to independently deliver a different commitment without any cross-confirmation. Both honest nodes then complete the DKG "successfully" but hold inconsistent public keys. The `broadcast_success` final round does not detect this because it only checks `session_id` agreement, not public-key agreement. The resulting key can never produce a valid threshold signature, permanently freezing any funds associated with it.

---

### Finding Description

**Root cause — `echo_ready_thresholds`:** [1](#0-0) 

The comment explicitly states "no malicious parties are assumed" for n ≤ 3, but `assert_key_invariants` permits n=3 with threshold=2, which by definition tolerates one Byzantine participant. [2](#0-1) 

**Delivery mechanics with `ready_t = 0`:**

When `ready_t = 0`, the amplification guard `count > ready_t` fires on the very first Ready message received (count becomes 1, `1 > 0`). The node immediately amplifies by sending its own Ready and simulating a self-Ready, raising the count to 2. The delivery guard `count > 2 * ready_t` then fires (`2 > 0`), delivering the value — all triggered by a single external Ready message. [3](#0-2) 

This means each honest node delivers whatever value it first receives for a given session, with no cross-confirmation from the other honest node.

**Equivocation attack in DKG Round 2:**

The attacker B sends two different `Send(commitment_B1, proof_B1)` → A and `Send(commitment_B2, proof_B2)` → C for session B. With `(echo_t=0, ready_t=0)`:

- A processes `Send(commitment_B1)`, echoes it, simulates self-Echo (`echo_t=0` → `1>0`), sends Ready, simulates self-Ready (`ready_t=0` → `1>0`), delivers `commitment_B1`. `finish_ready=true` for session B.
- C does the same independently and delivers `commitment_B2`. `finish_ready=true` for session B.
- Cross-echo/ready messages from A and C arrive after `finish_echo`/`finish_ready` are already set and are silently dropped.

**Commitment hash does not prevent this:**

The commitment hash is sent via point-to-point `chan.send_many`, not via `do_broadcast`. B sends `H(B, commitment_B1, session_id)` to A and `H(B, commitment_B2, session_id)` to C. Both `verify_commitment_hash` calls pass independently. [4](#0-3) [5](#0-4) 

**`broadcast_success` does not detect the inconsistency:**

The final round broadcasts `(true, session_id)`. Since Round 1 was not equivocated, A and C share the same `session_id`. Both broadcast `(true, session_id)`, both pass the `sid == &session_id` check, and both return `Ok`. Neither node ever compares its `verifying_key` with the other's. [6](#0-5) 

A holds `verifying_key_A = commitment_A + commitment_B1 + commitment_C` and C holds `verifying_key_C = commitment_A + commitment_B2 + commitment_C`. These are different group elements. The DKG reports success to both.

**Clarification on the question's specific sub-path (Ready without Send/Echo for another participant's session):**

If B sends `Ready(forged_data)` for session A (a different participant's session), honest node C delivers `forged_data` for A's session. However, honest node A detects the mismatch at line 311–317 and aborts with an error. This sub-path produces a detectable abort (DoS), not a silent inconsistency. The silent inconsistency requires equivocation in B's own session (Round 2), as described above. [7](#0-6) 

---

### Impact Explanation

A Byzantine participant in a 3-party DKG can cause the two honest nodes to complete the protocol with different group public keys. Any funds sent to the address derived from this key are permanently frozen: no valid threshold signature can ever be produced because the honest nodes disagree on the public key against which signatures are verified. This matches **Critical — permanent freezing of funds controlled by the MPC network**.

---

### Likelihood Explanation

n=3 is the minimum permitted configuration (`assert_key_invariants` allows `participants.len() >= 2`, `threshold >= 2`). The attack requires only that the Byzantine participant craft two valid `(commitment, proof)` pairs — trivial since the attacker knows both secrets — and route them to different peers. No network-level capability beyond standard Byzantine message routing is needed. The attack is silent: both honest nodes report DKG success.

---

### Recommendation

1. **Remove the `n <= 3` special case.** The formula `broadcast_threshold = (n-1)/3` gives 0 for n=3, which is the same result. The special case is redundant and its comment ("no malicious parties assumed") contradicts the DKG's own threat model. Use the general formula for all n, or enforce `n >= 4` as a minimum.

2. **Broadcast the commitment hash via `do_broadcast`, not `chan.send_many`.** The current point-to-point send allows B to equivocate on the hash itself, defeating the binding property of the commitment scheme.

3. **Include `verifying_key` in the `broadcast_success` payload** so that honest nodes detect public-key disagreement before returning `Ok`.

---

### Proof of Concept

```
Participants: A (honest), B (attacker), C (honest), n=3, threshold=2
echo_ready_thresholds(3) = (0, 0)

--- Commitment hash round (chan.send_many, point-to-point) ---
B → A: H(B, commitment_B1, session_id)   // hash_1
B → C: H(B, commitment_B2, session_id)   // hash_2  (different)

--- Round 2: do_broadcast for (commitment, proof) ---
B → A: Send(commitment_B1, proof_B1)
B → C: Send(commitment_B2, proof_B2)

A: receives Send(commitment_B1), echo_t=0 → echo → ready → deliver commitment_B1
   finish_ready[B] = true
C: receives Send(commitment_B2), echo_t=0 → echo → ready → deliver commitment_B2
   finish_ready[B] = true

Cross-messages (Echo/Ready from A to C and vice versa) arrive after finish_ready=true → dropped.

--- verify_commitment_hash ---
A: H(B, commitment_B1, session_id) == hash_1  ✓
C: H(B, commitment_B2, session_id) == hash_2  ✓

--- verifying_key ---
A: vk_A = commitment_A + commitment_B1 + commitment_C
C: vk_C = commitment_A + commitment_B2 + commitment_C
vk_A ≠ vk_C

--- broadcast_success ---
A broadcasts (true, session_id), C broadcasts (true, session_id)
Both pass: session_id matches, boolean=true
Both return Ok(KeygenOutput { public_key: vk_A })  /  Ok(KeygenOutput { public_key: vk_C })

DKG reports success. Key is permanently inconsistent. Funds frozen.
```

### Citations

**File:** crates/threshold-signatures/src/protocol/echo_broadcast.rs (L67-73)
```rust
fn echo_ready_thresholds(n: usize) -> (usize, usize) {
    // case where no malicious parties are assumed: when n <= 3/
    // In this case the echo and ready thresholds are both 0
    // later we compare if we have collected more votes than these thresholds
    if n <= 3 {
        return (0, 0);
    }
```

**File:** crates/threshold-signatures/src/protocol/echo_broadcast.rs (L280-295)
```rust
                if state_sid.data_ready.get(&data).ok_or_else(|| {
                    ProtocolError::Other("Missing element in CounterList".to_string())
                })? > ready_t
                    && !state_sid.finish_amplification
                {
                    vote = MessageType::Ready(data.clone());
                    chan.send_many(wait, &(&sid, &vote))?;
                    state_sid.finish_amplification = true;

                    // simulate a ready vote sent by me
                    is_simulated_vote = true;
                    from = me;
                }
                if state_sid.data_ready.get(&data).ok_or_else(|| {
                    ProtocolError::Other("Missing element in CounterList".to_string())
                })? > 2 * ready_t
```

**File:** crates/threshold-signatures/src/protocol/echo_broadcast.rs (L311-318)
```rust
                    if sid == participants.index(me)? && MessageType::Send(data) != send_vote {
                        return Err(ProtocolError::AssertionFailed(
                            "Too many malicious parties, way above the assumed threshold:
                            The message output after the broadcast protocol is not the same as
                            the one originally sent by me"
                                .to_string(),
                        ));
                    }
```

**File:** crates/threshold-signatures/src/dkg.rs (L309-339)
```rust
async fn broadcast_success(
    chan: &mut SharedChannel,
    participants: &ParticipantList,
    me: Participant,
    session_id: HashOutput,
) -> Result<(), ProtocolError> {
    // broadcast node me succeded
    let vote_list = do_broadcast(chan, participants, me, (true, session_id)).await?;
    // unwrap here would never fail as the broadcast protocol ends only when the map is full
    let vote_list = vote_list
        .into_vec_or_none()
        .ok_or_else(|| ProtocolError::AssertionFailed("vote_list is empty".to_string()))?;
    // go through all the list of votes and check if any is fail or some does not contain the session id

    if !vote_list.iter().all(|(_, sid)| sid == &session_id) {
        return Err(ProtocolError::AssertionFailed(
            "A participant
                broadcast the wrong session id. Aborting Protocol!"
                .to_string(),
        ));
    }

    if !vote_list.iter().all(|&(boolean, _)| boolean) {
        return Err(ProtocolError::AssertionFailed(
            "A participant
                seems to have failed its checks. Aborting Protocol!"
                .to_string(),
        ));
    }
    // Wait for all the tasks to complete
    Ok(())
```

**File:** crates/threshold-signatures/src/dkg.rs (L415-428)
```rust
    // Step 2.9
    let wait_round_1 = chan.next_waitpoint();
    chan.send_many(wait_round_1, &commitment_hash)?;
    // receive commitment_hash

    let mut all_hash_commitments = ParticipantMap::new(&participants);
    all_hash_commitments.put(me, commitment_hash);

    // Step 3.1
    for (from, their_commitment_hash) in
        recv_from_others(&chan, wait_round_1, &participants, me).await?
    {
        all_hash_commitments.put(from, their_commitment_hash);
    }
```

**File:** crates/threshold-signatures/src/dkg.rs (L464-471)
```rust
        // verify that the commitment sent hashes to the received commitment_hash in round 1
        verify_commitment_hash(
            &session_id,
            p,
            &mut commit_domain_separator.clone(), // you want to have the same state
            commitment_i,
            &all_hash_commitments,
        )?;
```

**File:** crates/threshold-signatures/src/dkg.rs (L571-588)
```rust
    if participants.len() < 2 {
        return Err(InitializationError::NotEnoughParticipants {
            participants: participants.len(),
        });
    }

    // Step 1.1
    // validate threshold
    if threshold > participants.len() {
        return Err(InitializationError::ThresholdTooLarge {
            threshold,
            max: participants.len(),
        });
    }
    // Step 1.1
    if threshold < 2 {
        return Err(InitializationError::ThresholdTooSmall { threshold, min: 2 });
    }
```
